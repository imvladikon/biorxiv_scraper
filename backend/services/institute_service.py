from flask_injector import inject
from pony.orm import db_session

from backend.model.entities import DB
from backend.services import GeocoderService
from backend.services.country_service import CountryService


class InstituteService:
    @inject
    def __init__(self, db: DB, country_service: CountryService, geocoder_service: GeocoderService):
        self.db = db
        self.country_service = country_service
        self.geocoder_service = geocoder_service

    @db_session
    def find_by_id(self, id):
        assert id
        entry = self.db.model.Institute[id]
        if entry:
            return entry.to_dict()
        return {"message": "Institute not found."}, 404

    @db_session
    def find_by_name(self, name):
        assert name
        entry = self.db.model.Institute.get(lambda s: s.name == name)
        if entry:
            return entry.to_dict()
        return {"message": "Institute not found."}, 404

    @db_session
    def create_item(self, *args, **kwargs):
        if not kwargs:
            return None
        dto = kwargs
        entry = None
        if "name" in dto:
            entry = self.db.model.Institute.get(lambda s: s.name == dto.name)
        if entry is None:
            geo_result = self.geocoder_service.from_google_sync(entry.name)
            if geo_result:
                dto.lat, dto.lng, dto.country = geo_result.get("lat", None), geo_result.get("lon",
                                                                                            None), geo_result.get(
                    "country", "")
            return self.db.model.Institute(**dto).to_dict()
        return entry

    @db_session
    def list(self):
        institutes = self.db.model.Institute.select()
        institutes = [institute.to_dict() for institute in institutes]
        return institutes
