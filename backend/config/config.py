
config = dict(
    DEBUG = True,
    SECRET_KEY = '',
    PONY = {
        'provider': 'mysql',
        # 'host': 'db',
        'host': '127.0.0.1',
        'port': 3306,
        'user': 'db_user',
        'password': 'P@s$w0rd123!',
        'db': 'articles'
    }
)
