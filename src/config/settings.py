from decouple import config

EMAIL_CONFIG = {
    'user': config('EMAIL_USER'),
    'password': config('EMAIL_PASSWORD'),
    'server': config('SMTP_SERVER'),
    'port': config('SMTP_PORT', cast=int)
}