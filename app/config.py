from decouple import config
from datetime import timedelta

class Config:
    SECRET_KEY = config('SECRET_KEY', 'secret')
    RESTX_MASK_SWAGGER = False
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=30)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(minutes=30)
    JWT_SECRET_KEY = config('JWT_SECRET_KEY')

class DevConfig(Config):
    DEBUG = config('DEBUG', cast=bool)
    SQLALCHEMY_ECHO = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = config('SQLALCHEMY_DATABASE_URI')

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:Sarkar#8991@localhost:5432/flaskapi_test'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = True

class ProdConfig(Config):
    pass

config_dict = {
    'dev': DevConfig,
    'prod': ProdConfig,
    'test': TestConfig
}