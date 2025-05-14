import os


class Config(object):
    USER = os.environ.get('POSTGRES_USER', 'den')
    PASSWORD = os.environ.get('POSTGRES_PASSWORD', 'vinsit123')
    HOST = os.environ.get('POSTGRES_HOST', 'localhost')
    PORT = os.environ.get('POSTGRES_PORT', 5432)
    DB = os.environ.get('POSTGRES_DB', 'zadanie')
    SQLALCHEMY_DATABASE_URI = f'postgresql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DB}'
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SECRET_KEY = 'sdfgdfgrge325434gregdf'
