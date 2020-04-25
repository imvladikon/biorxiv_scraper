from flask_injector import inject
from pony.orm import db_session

from backend.model.article import ArticleDTO
from backend.model.entities import DB
from backend.services import AuthorService


class ArticleService:
    @inject
    def __init__(self, db: DB, author_service: AuthorService):
        self.db = db
        self.author_service = author_service

    @db_session
    def find_by_id(self, id):
        assert id
        entry = self.db.model.Article[id]
        if entry:
            return entry.to_dict()
        return {"message": "Article not found."}, 404

    @db_session
    def find_by_url(self, url):
        assert url
        entry = self.db.model.Article.get(lambda s: s.url == url)
        if entry:
            return entry.to_dict()
        return {"message": "Article not found."}, 404

    @db_session
    def find_by_title(self, title):
        assert title
        entry = self.db.model.Article.get(lambda s: s.title == title)
        if entry is None:
            car_info = self.db.model.Article(title=title)
            return car_info.to_dict()
        return entry.to_dict()

    @db_session
    def create_item(self, article_dto: ArticleDTO):
        if not article_dto:
            return None
        entry = None
        if "href" in article_dto:
            entry = self.db.model.Article.get(lambda s: s.href == article_dto.get("href", ""))
        if entry is None:
            dto = dict()
            dto["url"] = article_dto.url
            dto["title"] = article_dto.title
            dto["abstract"] = article_dto.abstract
            dto["doi"] = article_dto.doi
            dto["last_updated"] = article_dto.last_updated
            dto["added_on"] = article_dto.added_on
            dto["published_on"] = article_dto.published_on
            dto["posted"] = article_dto.posted
            entry = self.db.model.Article(**dto)
            entry.metric.create(**article_dto.metric)
            entry.attachments.create(**article_dto.attachment)
            for author_dto in article_dto.authors:
                entry_author = self.author_service.find_by_fullname(author_dto.fullname)
                if not entry_author:
                    # entry_author = self.author_service.create_item(**author_dto)
                    author = entry.authors.create(**author_dto)
            # source = Optional("SourceSite")
            # collections = Set("Collection", cascade_delete=False)
            return entry.to_dict()
        return entry

    @db_session
    def list(self):
        car_infos = self.db.model.Article.select()
        car_info_list = [car_info.to_dict() for car_info in car_infos]
        return car_info_list
