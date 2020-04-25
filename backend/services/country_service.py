from flask_injector import inject
from pony.orm import db_session

from backend.model.article import ArticleDTO
from backend.model.collection import CollectionDTO
from backend.model.entities import DB


class CountryService:
    @inject
    def __init__(self, db: DB):
        self.db = db

    @db_session
    def find_by_id(self, id):
        assert id
        entry = self.db.model.Country[id]
        if entry:
            return entry.to_dict()
        return {"message": "Country not found."}, 404

    @db_session
    def find_by_name(self, name):
        assert name
        entry = self.db.model.Country.get(lambda s: s.name == name)
        if entry:
            return entry.to_dict()
        return {"message": "Country not found."}, 404

    @db_session
    def create_item(self, *args, **kwargs):
        if not kwargs:
            return None
        dto = kwargs
        entry = None
        if "name" in dto:
            entry = self.db.model.Country.get(lambda s: s.name == dto.name)
        if entry is None:
            return self.db.model.Country(**dto).to_dict()
        return entry

    @db_session
    def list(self):
        countries = self.db.model.Country.select()
        countries = [country.to_dict() for country in countries]
        return countries
