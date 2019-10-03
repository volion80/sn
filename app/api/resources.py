from flask import current_app
from flask_restful import Resource, reqparse
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, jwt_refresh_token_required, get_jwt_identity, get_raw_jwt
from app.models import User, RevokedToken, Post, PostRate


user_parser = reqparse.RequestParser()
user_parser.add_argument('email', help='This field cannot be blank', required=True)
user_parser.add_argument('password', help='This field cannot be blank', required=True)


class UserSignup(Resource):
    def post(self):
        if User.count() >= current_app.config['MAX_USERS_SIGNUP']:
            return {'error': 'Users sign up limit has been reached'}
        data = user_parser.parse_args()
        if User.find_by_email(data['email']):
            return {'error': 'User {} already exists'. format(data['email'])}
        if not data['password']:
            return {'error': 'password cannot be empty'}
        new_user = User(
            email=data['email'],
            password=User.generate_hash(data['password'])
        )
        try:
            new_user.save()
            access_token = create_access_token(identity=data['email'])
            refresh_token = create_refresh_token(identity=data['email'])
            return {
                'message': 'User {} has been created'.format(data['email']),
                'id': new_user.id,
                'access_token': access_token,
                'refresh_token': refresh_token
            }
        except:
            return {'error': 'Sign up: Something went wrong.'}, 500


class UserLogin(Resource):
    def post(self):
        data = user_parser.parse_args()
        current_user = User.find_by_email(data['email'])
        if not current_user:
            return {'error': 'User {} doesn\'t exist'.format(data['email'])}

        if User.verify_hash(data['password'], current_user.password):
            access_token = create_access_token(identity=data['email'])
            refresh_token = create_refresh_token(identity=data['email'])
            return {
                'message': 'Logged in as {}'.format(current_user.email),
                'access_token': access_token,
                'refresh_token': refresh_token
            }
        else:
            return {'error': 'Wrong credentials'}


class UserLogoutAccess(Resource):
    @jwt_required
    def post(self):
        jti = get_raw_jwt()['jti']
        try:
            revoked_token = RevokedToken(jti=jti)
            revoked_token.add()
            return {'message': 'Access token has been revoked'}
        except:
            return {'error': 'Logout (Access Token): Something went wrong'}, 500


class UserLogoutRefresh(Resource):
    @jwt_refresh_token_required
    def post(self):
        jti = get_raw_jwt()['jti']
        try:
            revoked_token = RevokedToken(jti=jti)
            revoked_token.add()
            return {'message': 'Refresh token has been revoked'}
        except:
            return {'error': 'Logout (Refresh Token): Something went wrong'}, 500


class TokenRefresh(Resource):
    @jwt_refresh_token_required
    def post(self):
        current_user = get_jwt_identity()
        access_token = create_access_token(identity=current_user)
        return {'access_token': access_token}


class AllUsers(Resource):
    def get(self):
        return {'users': User.all()}

    def delete(self):
        return User.delete_all()


post_parser = reqparse.RequestParser()
post_parser.add_argument('body', help='This field cannot be blank', required=True)


class Posts(Resource):
    def get(self):
        return {'posts': Post.all()}

    @jwt_required
    def post(self):
        data = post_parser.parse_args()
        current_user_email = get_jwt_identity()
        current_user = User.find_by_email(current_user_email)
        if current_user.posts.count() >= current_app.config['MAX_POSTS_PER_USER']:
            return {
                'error': '{} has reached posts limit'.format(current_user.email),
            }
        new_post = Post(
            body=data['body'],
            user_id=current_user.id
        )
        try:
            new_post.save()
            return {
                'message': 'Post has been added by {}'.format(current_user.email),
            }
        except:
            return {'error': 'Add Post: Something went wrong. User ID {}'.format(current_user.id)}, 500


rates_parser = reqparse.RequestParser()
rates_parser.add_argument('post_id', help='This field cannot be blank', required=True)
rates_parser.add_argument('is_like', help='This field cannot be blank', required=True)


class PostsRates(Resource):
    @jwt_required
    def post(self):
        data = rates_parser.parse_args()
        current_user_email = get_jwt_identity()
        current_user = User.find_by_email(current_user_email)
        post = Post.get(data['post_id'])
        if post is None:
            return {'error': 'Post not found, ID {}'.format(data['post_id'])}
        if post.check_author(current_user.id):
            return {'error': 'Author cannot rate his own post (User ID {}, Post ID {})'.format(current_user.id, post.id)}
        if post.rated_by_user(current_user.id):
            return {'error': 'User already rated the post (User ID {}, Post ID {})'.format(current_user.id, post.id)}
        if current_user.posts_rated.count() >= current_app.config['MAX_LIKES_PER_USER']:
            return {'error': 'User has reached rates number limit (User ID {})'.format(current_user.id)}

        new_rate = PostRate(
            post_id=post.id,
            user_id=current_user.id,
            is_like=int(data['is_like'])
        )
        try:
            new_rate.save()
            return {
                'message': 'Post has been rated by {}'.format(current_user.email),
            }
        except:
            return {'error': 'Rate Post: Something went wrong. User ID {}, Post ID {}'.format(current_user.id, post.id)}, 500
