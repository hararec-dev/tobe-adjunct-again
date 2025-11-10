from decouple import config

EMAIL_CONFIG = {
    'user': config('EMAIL_USER'),
    'password': config('EMAIL_PASSWORD'),
    'server': config('EMAIL_SERVER'),
    'port': config('EMAIL_PORT', cast=int)
}

TIMESCALE_CONFIG = {
    'host': config('POSTGRES_HOST'),
    'port': config('POSTGRES_PORT', cast=int),
    'user': config('POSTGRES_USER'),
    'password': config('POSTGRES_PASSWORD'),
    'db': config('POSTGRES_DB')
}
