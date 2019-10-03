from app import db
from passlib.hash import pbkdf2_sha256 as sha256
from sqlalchemy import text


class PostRate(db.Model):
    __tablename__ = 'post_rates'
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    is_like = db.Column(db.Boolean)

    def save(self):
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_posts_rating():
        sql = """select u.email, pr.post_id, sum(case when pr.is_like = 0 then -1 else 1 end) as rating
                    from post_rates pr
                        join posts p on pr.post_id = p.id
                        join users u on u.id = p.user_id
                    group by pr.post_id, u.email
                    order by rating desc limit 10"""
        data = db.engine.execute(text(sql))
        return [PostRate.rating_to_json(row) for row in data]

    @staticmethod
    def rating_to_json(row):
        return {
            'user': row.email,
            'post_id': row.post_id,
            'rating': int(row.rating)
        }


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    posts = db.relationship('Post', backref='user', lazy='dynamic')
    posts_rated = db.relationship('PostRate',
                                  foreign_keys=[PostRate.user_id],
                                  backref=db.backref('user', lazy='joined'),
                                  lazy='dynamic',
                                  cascade='all, delete-orphan')

    def save(self):
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def generate_hash(password):
        return sha256.hash(password)

    @staticmethod
    def verify_hash(password, hash):
        return sha256.verify(password, hash)

    @classmethod
    def find_by_email(cls, email):
        return cls.query.filter_by(email=email).first()

    @classmethod
    def all(cls):
        return [user.to_json() for user in cls.query.all()]

    @classmethod
    def stats(cls):
        return [user.stats_to_json() for user in cls.query.all()]

    @classmethod
    def count(cls):
        return cls.query.count()

    def is_post_author(self, post_id):
        query = self.posts.posts.filter_by(id=post_id).first()
        return bool(query)

    @classmethod
    def delete_all(cls):
        try:
            num_rows_deleted = cls.query.delete()
            db.session.commit()
            return {'message': '{} row(s) deleted'.format(num_rows_deleted)}
        except:
            return {'message': 'Something went wrong'}

    def to_json(self):
        return {
            'id': self.id,
            'email': self.email
        }

    def stats_to_json(self):
        return {
            'id': self.id,
            'email': self.email,
            'user_posts': self.posts.count(),
            'posts_rated_by_user': self.posts_rated.count()
        }


class RevokedToken(db.Model):
    __tablename__ = 'revoked_tokens'
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(120))

    def add(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def is_jti_in_blacklist(cls, jti):
        query = cls.query.filter_by(jti=jti).first()
        return bool(query)


class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user_rates = db.relationship('PostRate',
                                 foreign_keys=[PostRate.post_id],
                                 backref=db.backref('post', lazy='joined'),
                                 lazy='dynamic',
                                 cascade='all, delete-orphan')

    @classmethod
    def get(cls, post_id):
        return cls.query.filter_by(id=post_id).first()

    @classmethod
    def all(cls):
        return [post.to_json() for post in cls.query.all()]

    def check_author(self, user_id):
        return self.user_id == user_id

    def rated_by_user(self, user_id):
        query = self.user_rates.filter_by(user_id=user_id).first()
        return bool(query)

    def save(self):
        db.session.add(self)
        db.session.commit()

    def to_json(self):
        return {
            'id': self.id,
            'body': self.body,
            'user_id': self.user_id,
        }
