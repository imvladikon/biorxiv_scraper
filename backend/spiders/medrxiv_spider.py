from injector import inject

from backend.services import ArticleService


class MedrxivSpider(object):
    @inject
    def __init__(self, article_service: ArticleService):
        self.article_service = article_service
