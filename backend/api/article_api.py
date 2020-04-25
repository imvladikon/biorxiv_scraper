from decimal import Decimal

from flask import jsonify
from flask_restful import Resource, reqparse
from flask_injector import inject

from backend.services import ArticleService


class ArticleApi(Resource):
    ENDPOINT = "/api/v1/resources/article/<int:entry_id>"

    @inject
    def __init__(self, article_service: ArticleService):
        self.article_service = article_service

        self.parser = reqparse.RequestParser()
        self.parser.add_argument(
            "price",
            type=Decimal,
            required=True,
            help="The \"price\" field cannot be left blank!"
        )
        self.parser.add_argument(
            "id",
            type=str,
            required=True,
            help="Cannot insert item without a ID!"
        )

    def get(self, entry_id):
        return jsonify(self.article_service.find_by_id(entry_id))


class ArticleListApi(Resource):
    ENDPOINT = "/api/v1/resources/articles/all"

    @inject
    def __init__(self, article_service: ArticleService):
        self.article_service = article_service

    def get(self):
        return jsonify(self.article_service.list())
