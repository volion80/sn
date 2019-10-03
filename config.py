import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = 'secretkey1234567890'
    SQLALCHEMY_DATABASE_URI = 'mysql://root:@localhost/sn'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = 'jwtsecret1234567890'
    JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = ['access', 'refresh']

    MAX_USERS_SIGNUP = 10
    MAX_POSTS_PER_USER = 10
    MAX_LIKES_PER_USER = 10

    @staticmethod
    def init_app(app):
        pass
