from backend.spiders import SPIDERS
from injector import inject
from backend.services import ArticleService
from backend.spiders.biorxiv_spider import BiorxivSpider


class Scraper:
    @inject
    def __init__(self, spider: BiorxivSpider, service: ArticleService):
        self.spider = spider
        self.service = service

    async def run_spiders(self, *args, **kwargs):
        await self.spider.run(*args, kwargs)
