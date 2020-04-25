from datetime import datetime

from pony.orm import *
from pony.orm import Database as PonyDatabase


# https://docs.ponyorm.org/api_reference.html

class DB:

    def __init__(self, **db_params):
        self.model = PonyDatabase(**db_params)

        class Article(self.model.Entity):
            id = PrimaryKey(int, auto=True)
            url = Optional(str, 255, nullable=True)
            title = Optional(str, nullable=True)
            abstract = Optional(LongStr, nullable=True)
            doi = Optional(str, nullable=True)
            collections = Set("Collection", cascade_delete=False)
            last_updated = Optional(datetime, nullable=True)
            added_on = Optional(datetime, nullable=True)
            published_on = Optional(datetime, nullable=True)
            posted = Optional(datetime, nullable=True)
            source = Optional("SourceSite")
            authors = Set("Author", cascade_delete=False)
            metric = Optional("ArticleMetric")
            attachments = Set("ArticleAttachments", cascade_delete=True)

        class ArticleAttachments(self.model.Entity):
            id = PrimaryKey(int, auto=True)
            url = Optional(str, 255, nullable=True)
            content = Optional(str, nullable=True)
            pdf_link = Optional(str, nullable=True)
            supplementary_link = Optional(str, nullable=True)
            data_code_link = Optional(str, nullable=True)
            article = Required(Article)

        class ArticleMetric(self.model.Entity):
            id = PrimaryKey(int, auto=True)
            article = Required(Article)
            all_posts = Optional(int)
            tweets = Optional(int)
            facebook = Optional(int)
            google_plus = Optional(int)
            reddit = Optional(int)
            blogs = Optional(int)
            article = Required(Article)

        class Collection(self.model.Entity):
            id = PrimaryKey(int, auto=True)
            url = Optional(str, 255, nullable=True)
            title = Optional(str, nullable=True)
            articles = Set(Article)

        class SourceSite(self.model.Entity):
            id = PrimaryKey(int, auto=True)
            name = Optional(str)
            url = Optional(str, 255, nullable=True)
            articles = Set(lambda : Article)

        class Author(self.model.Entity):
            id = PrimaryKey(int, auto=True)
            name = Required(str)
            email = Required(str)
            institution = Optional("Institute")
            articles = Set(lambda : Article)

        class Institute(self.model.Entity):
            id = PrimaryKey(int, auto=True)
            name = Required(str)
            lng = Optional(float)
            lat = Optional(float)
            authors = Set(lambda : Author)
            country = Optional("Country")

        class Country(self.model.Entity):
            code = Required(int, unique=True)
            name = Required(str)
            institutions = Set(lambda : Institute)


