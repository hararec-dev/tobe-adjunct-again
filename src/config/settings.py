from decouple import config

EMAIL_CONFIG = {
    'user': config('EMAIL_USER'),
    'password': config('EMAIL_PASSWORD'),
    'server': config('SMTP_SERVER'),
    'port': config('SMTP_PORT', cast=int)
}

MONGO_CONFIG = {
    'host': config('MONGO_HOST'),
    'port': config('MONGO_PORT', cast=int),
    'username': config('MONGO_USERNAME'),
    'password': config('MONGO_PASSWORD'),
    'database': config('MONGO_DATABASE'),
    'collection': config('MONGO_COLLECTION')
}