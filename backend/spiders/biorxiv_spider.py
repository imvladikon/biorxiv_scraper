import logging
import os

import aiohttp
import asyncio

import dateparser
import flupy
from flask_injector import inject
from bs4 import BeautifulSoup
from typing import Iterable

from flupy import flu

from backend.model.article_metric import ArticleMetricDTO
from backend.model.author import AuthorDTO
from backend.model.collection import CollectionDTO
from backend.services import ArticleService, GeocoderService
from backend.model.article import ArticleDTO
from backend.services.altmetric_service import AltmetricService, Citation
from backend.services.collection_service import CollectionService
from backend.utils.http import fetch, fetch_async
from backend.utils.misc import parse, try_parse
from backend.utils.optional import Optional
from backend.utils.strings import blank_string, absolute_url, replace_all, not_blank_string
from decimal import Decimal, ROUND_UP

MAIN_URL = "https://www.biorxiv.org/{}"
BASE_URL = "https://www.biorxiv.org/"
logger = logging.getLogger(__name__)
project_dir = os.path.dirname(os.path.realpath(__file__))

sources = {"biorxiv", "arxiv", "medrxiv"}


class BiorxivSpider(object):
    @inject
    def __init__(self, article_service: ArticleService, altmetric_service: AltmetricService,
                 collection_service: CollectionService):
        self.article_service = article_service
        self.altmetric_service = altmetric_service
        self.collection_service = collection_service

    @asyncio.coroutine
    async def parse_collections(self) -> Iterable[CollectionDTO]:
        # yield CollectionDTO(title="COVID-19", url="https://connect.biorxiv.org/relate/content/181")
        async with aiohttp.ClientSession() as session:
            html = await fetch_async(session, BASE_URL)
            soup = BeautifulSoup(html, 'html.parser')
            for node in soup.select(".field-content"):
                url, title = Optional.of(node.select_one("a")).map(
                    lambda e: (e.get("href").strip(), e.text.strip())).get_or_else(("", ""))
                url = url[1:] if url.startswith("/") else url
                yield CollectionDTO(title=title, url=url)

    @asyncio.coroutine
    async def parse_article(self, n) -> ArticleDTO:
        article = ArticleDTO()
        url_abstract = (Optional.of(n.select_one("div:first-of-type")).map(
            lambda e: absolute_url(BASE_URL, e.get("data-url"))).get_or_else(""))
        if url_abstract:
            async with aiohttp.ClientSession() as session:
                html = await fetch_async(session, url_abstract)
                soup_abstract = BeautifulSoup(html, 'html.parser')
                article.abstract = Optional.of(soup_abstract.select_one("#content-block")).map(
                    lambda e: e.text.strip()).get_or_else("")
                del soup_abstract
        article.doi = (Optional.of(n.select_one(".highwire-cite-metadata-doi.highwire-cite-metadata")).map(
            lambda e: e.text.strip().strip("doi:")).get_or_else(""))
        if not article.doi:
            article.doi = (Optional.of(n.select_one(".highwire-cite-metadata-pages.highwire-cite-metadata")).map(
                lambda e: e.text.strip().strip(";")).get_or_else(""))
        if not article.doi:
            article.doi = Optional.of(n.select_one("div:first-of-type")).map(
                lambda e: replace_all(e.get("data-pisa-master"), *sources)).get_or_else("")
        article.url = (Optional.of(n.select_one(".highwire-cite-title>a")).map(
            lambda e: absolute_url(BASE_URL, e.get("href"))).get_or_else(""))
        article.title = Optional.of(n.select_one(".highwire-cite-title")).map(lambda e: e.text.strip()).get_or_else("")
        node_authors = n.select(".highwire-citation-author")
        if node_authors:
            article.authors = list()
            for na in n.select(".highwire-citation-author"):
                name = Optional.of(na.select_one(".nlm-given-names")).map(lambda e: e.text.strip()).get_or_else("")
                surname = Optional.of(na.select_one(".nlm-surname")).map(lambda e: e.text.strip()).get_or_else("")
                if name and surname:
                    article.authors.append(AuthorDTO(name=name, surname=surname, fullname=f"{name} {surname}"))
            del node_authors
        async with aiohttp.ClientSession() as session:
            html = await fetch_async(session, f"{article.url}.article-info")
            soup = BeautifulSoup(html, 'html.parser')
            article.pdf_link = Optional.of(soup.select_one(".article-dl-pdf-link")).map(
                lambda e: absolute_url(BASE_URL, e.get("href"))).get_or_else("")
            article.title = article.title or Optional.of(soup.select_one("#page-title")).map(
                lambda e: e.text).get_or_else("")
            article.supplementary_link = Optional.of(soup.select_one(".pane-biorxiv-supplementary-fragment a")).map(
                lambda e: e.get("href")).get_or_else("")
            links = (flu(soup.select(".pane-highwire-variant-link"))
                     .filter(lambda e: e and "Data/Code" in e.text)
                     .map(lambda e: e.select_one("a")).collect())
            article.datacode_link = (Optional.of(links)
                                     .filter(lambda n: not n)
                                     .map(lambda e: absolute_url(BASE_URL, e.get("href")))
                                     .get_or_else(""))
            del links
            article.posted = Optional.of(soup.select_one(".published")).map(lambda e: e.text.strip().strip(".")).filter(
                blank_string).map(lambda s: dateparser.parse(s)).get_or_else(None)
            node_universities = soup.select_one(".affiliation-list")
            dict_universities = {}
            if node_universities:
                for node_university in node_universities.select(".aff"):
                    university_number_ref = Optional.of(node_university.select_one("sup")).map(
                        lambda e: e.text.strip()).get_or_else("")
                    university_href_id = Optional.of(node_university.select_one("a")).map(
                        lambda e: e.get("id")).get_or_else("")
                    dict_universities[university_href_id] = node_university.text.strip().replace(university_number_ref,
                                                                                                 "").strip().strip(
                        ";").strip()
            node_authors = soup.select_one("#contrib-group-1")
            if node_authors:
                for node_author in node_authors.select("[id^=contrib-]"):
                    fullname = Optional.of(node_author.select_one(".name")).map(lambda e: e.text).get_or_else("")
                    if not fullname:
                        continue
                    author = None
                    authors = (flu(article.authors)
                               .filter(lambda a: a.fullname == fullname or (a.name and a.name in fullname) or (
                            a.surname and a.surname in fullname))
                               .take(1)
                               .collect())  # first()?
                    if authors:
                        author = authors[0]
                    else:
                        continue
                    email = (Optional.of(node_author.select_one(".contrib-email"))
                             .map(lambda e: e.text.strip().strip("()").replace("{at}", "@"))
                             .get_or_else(""))
                    if email and author:
                        author.email = email
                    author.institution = (Optional.of(node_author.select_one("[id^=xref-aff-]")).map(
                        lambda e: dict_universities.get(e.get("href").strip("#"), "")).get_or_else(""))
            del soup
            del node_universities
            del node_authors
        # f"{url}.article-metrics"
        if article.doi:
            citation = self.altmetric_service.get(article.doi)
            metric = ArticleMetricDTO()
            metric.all_posts = citation.stats_all_posts
            metric.tweets = citation.stats_tweets
            metric.facebook = citation.stats_facebook
            metric.google_plus = citation.stats_google_plus
            metric.reddit = citation.stats_reddit
            metric.blogs = citation.stats_blogs
            article.metric = metric
        return article

    @asyncio.coroutine
    async def parse_article_lists(self, collection: CollectionDTO) -> Iterable[ArticleDTO]:
        collection_url = collection.url
        async with aiohttp.ClientSession() as session:
            html = await fetch_async(session, collection_url)
            soup = BeautifulSoup(html, 'html.parser')
            for n in soup.select(".highwire-list-wrapper ul li"):
                yield self.parse_article(n)
            first_page = 1
            href, last_page = Optional.of(soup.select_one(".pager-last>a")).map(
                lambda e: (e.get("href").strip(), try_parse(1, e.text.strip()))).get_or_else(("", 0))
            for page in range(first_page, last_page):
                for n in soup.select(".highwire-list-wrapper ul li"):
                    yield self.parse_article(n)

    async def run(self, *args, **kwargs):
        articles = []
        for collection in self.parse_collections():
            async for article_a in await self.parse_article_lists(collection):
                article = await article_a
                articles.append(article)
                self.article_service.create_item(article)
            logger.info(f"fetching {collection.title} page")
        if kwargs and "output_filename" in kwargs or "to_file" in kwargs:
            project_dir = os.path.dirname(os.path.realpath(__file__))
            output_filename = kwargs["output_filename"] or "articles.csv"
            ArticleDTO.to_csv(articles, os.path.join(project_dir, "data", output_filename))


async def start_spider():
    db = None
    spider = BiorxivSpider(db)
    await spider.run()


def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(start_spider())
    # articles = parse_article_lists("https://www.biorxiv.org/collection/genetics")
    # articles = parse_article_lists("https://connect.biorxiv.org/relate/content/181")
    i = 42
    # parse_article("https://www.biorxiv.org/content/10.1101/2020.04.23.055293v1")
    # a = AltmetricService()
    # b = a.doi("10.1101/2020.04.23.055293")
    # c = Citation(b)
    # print(c.stats_all_posts)
    # print(c.stats_tweets)
    # print(c.stats_facebook)
    # print(c.stats_google_plus)
    # print(c.stats_reddit)
    # print(c.stats_blogs)
    # title
    # doi
    # altmetric_id
    # journal
    # authors : list
    # type
    # cited_by_posts_count : 7
    # cited_by_tweeters_count : 7
    # cited_by_accounts_count : 7
    # last_updated : 1587766772
    # score : float
    # history: {'1y': 2.85, '6m': 2.85, '3m': 2.85, '1m': 2.85, '1w': 2.85, '6d': 2.85, '5d': 2.85, '4d': 2.85, '3d': 2.85,
    #  '2d': 2.85, '1d': 2.85, 'at': 2.85}
    # url : http://dx.doi.org/10.1101/2020.04.23.055293
    # added_on = {int}1587747121
    # published_on' = {int}1587686400
    # details_url 'http://www.altmetric.com/details.php?citation_id=80489219'
    # cohorts : {'pub': 4, 'sci': 3}
    # 'context' = {dict: 4}
    # {'all': {'count': 14714661, 'mean': 8.6399717985907, 'rank': 7452156, 'pct': 48, 'higher_than': 7199634},
    #  'journal': {'count': 79324, 'mean': 13.336499401183, 'rank': 50176, 'pct': 36, 'higher_than': 28643},
    #  'similar_age_3m': {'count': 123983, 'mean': 20.3
    #                     'all' = {dict: 5}
    # {'count': 14714661, 'mean': 8.6399717985907, 'rank': 7452156, 'pct': 48, 'higher_than': 7199634}
    # 'journal' = {dict: 5}
    # {'count': 79324, 'mean': 13.336499401183, 'rank': 50176, 'pct': 36, 'higher_than': 28643}
    # 'similar_age_3m' = {dict: 5}
    # {'count': 123983, 'mean': 20.31717952606, 'rank': 48485, 'pct': 60, 'higher_than': 74431}
    # 'similar_age_journal_3m' = {dict: 5}
    # {'count': 4431, 'mean': 19.11702979684, 'rank': 2367, 'pct': 45, 'higher_than': 2026}
    #
    # for c in parse_collections():
    #     print(c)


if __name__ == '__main__':
    main()
