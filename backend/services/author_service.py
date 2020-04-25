from flask_injector import inject
from pony.orm import db_session

from backend.model.author import AuthorDTO
from backend.model.entities import DB
from backend.services import InstituteService


class AuthorService:
    @inject
    def __init__(self, db: DB, institute_service: InstituteService):
        self.db = db
        self.institute_service = institute_service

    @db_session
    def find_by_id(self, id):
        assert id
        entry = self.db.model.Author[id]
        if entry:
            return entry.to_dict()
        return {"message": "Author not found."}, 404

    @db_session
    def find_by_fullname(self, fullname):
        assert fullname
        entry = self.db.model.Author.get(lambda s: s.fullname == fullname)
        if entry:
            return entry.to_dict()
        return {"message": "Author not found."}, 404

    @db_session
    def create_item(self, dto: AuthorDTO):
        if not dto:
            return None
        entry = None
        if "fullname" in dto:
            entry = self.db.model.Author.get(lambda s: s.fullname == dto["fullname"])
        if entry is None:
            institute_entry = None
            if "institution" in dto and not dto["institution"]:
                institute_entry = self.institute_service.find_by_name(dto["institution"])
                if not institute_entry:
                    institute_entry = self.institute_service.create_item(name=dto["institution"])
            dto["institution"] = institute_entry
            return self.db.model.Author(**dto).to_dict()
        return entry.to_dict()

    @db_session
    def list(self):
        authors = self.db.model.Author.select()
        authors = [author.to_dict() for author in authors]
        return authors
