from decimal import Decimal

from flask.json import JSONEncoder


class ApiJSONEncoder(JSONEncoder):

    def default(self, obj):
        if isinstance(obj, Decimal):
            return str(obj)
        return super(ApiJSONEncoder, self).default(obj)
