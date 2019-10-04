from app import create_app, db, jwt
from flask_restful import Api
from flask_migrate import Migrate
from app.models import User, RevokedToken
from app.api import resources


app = create_app()
api = Api(app)
migrate = Migrate(app, db)

api.add_resource(resources.UserSignup, '/signup')
api.add_resource(resources.UserLogin, '/login')
api.add_resource(resources.UserLogoutAccess, '/logout/access')
api.add_resource(resources.UserLogoutRefresh, '/logout/refresh')
api.add_resource(resources.TokenRefresh, '/token/refresh')
api.add_resource(resources.Posts, '/posts')
api.add_resource(resources.PostsRates, '/posts/rate')
api.add_resource(resources.Users, '/users')


@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    jti = decrypted_token['jti']
    return RevokedToken.is_jti_in_blacklist(jti)


@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User)
