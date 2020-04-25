from flask_injector import inject
from pony.orm import db_session

from backend.model.article import ArticleDTO
from backend.model.collection import CollectionDTO
from backend.model.entities import DB


class CollectionService:
    @inject
    def __init__(self, db: DB):
        self.db = db

    @db_session
    def find_by_id(self, id):
        assert id
        entry = self.db.model.Collection[id]
        if entry:
            return entry.to_dict()
        return {"message": "Collection not found."}, 404

    @db_session
    def find_by_url(self, url):
        assert url
        entry = self.db.model.Collection.get(lambda s: s.url == url)
        if entry:
            return entry.to_dict()
        return {"message": "Collection not found."}, 404

    @db_session
    def find_by_title(self, title):
        assert title
        entry = self.db.model.Collection.get(lambda s: s.title == title)
        if entry is None:
            entry = self.db.model.Collection(title=title)
            return entry.to_dict()
        return entry.to_dict()

    @db_session
    def create_item(self, *args, **kwargs):
        dto = None
        if args and isinstance(args[0], (CollectionDTO, dict)):
            dto = args[0]
        elif kwargs:
            dto = kwargs
        entry = None
        if "url" in dto:
            entry = self.db.model.Collection.get(lambda s: s.url == dto.get("url", ""))
        if dto and entry is None:
            return self.db.model.Collection(**dto).to_dict()
        return None

    @db_session
    def list(self):
        collections = self.db.model.Collection.select()
        collections = [collection.to_dict() for collection in collections]
        return collections
