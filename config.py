import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = 'secretkey1234567890'
    SQLALCHEMY_DATABASE_URI = 'mysql://root:@localhost/sn'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = 'jwtsecret1234567890'
    JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = ['access', 'refresh']

    MAX_USERS_SIGNUP = 5
    MAX_POSTS_PER_USER = 5
    MAX_LIKES_PER_USER = 5

    EMAIL_HUNTER_ENABLED = False
    EMAIL_HUNTER_API_KEY = 'email-hunter-api-key'

    CLEARBIT_ENABLED = False
    CLEARBIT_API_KEY = 'clearbit-api-key'

    @staticmethod
    def init_app(app):
        pass
