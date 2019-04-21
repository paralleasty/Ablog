import bleach
from markdown import markdown
from app import db, login_manager
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64))
    email = db.Column(db.String(120), index=True, unique=True)
    blog_title = db.Column(db.String(64))
    password_hash = db.Column(db.String(128))
    about_me = db.Column(db.Text)

    # 保护密码
    @property
    def password(self):
        raise AttributeError('password is not readable attribute.')

    # def set_password(self, password):
    #     self.password_hash = generate_password_hash(password)

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def validate_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<Admin {}>'.format(self.username)


class User(UserMixin, db.Model):
    # 自定义表名
    # __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(128), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    posts = db.relationship('Post', backref='user', lazy='dynamic')

    @property
    def password(self):
        raise AttributeError('Password is not readable attribute.')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def validate_password(self, password):
        return check_password_hash(self.password_hash, password)


# 加载给定id的用户
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# one to many
class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)

    # backref参数自动为关系的另一侧添加关系属性
    posts = db.relationship('Post', backref='category', lazy='dynamic')

    # @property
    # def count(self):
    #     post_nums = Post.query.filter_by(category_id=self.id).count()
    #     return post_nums

    def __repr__(self):
        return '<Category {}>'.format(self.name)


# many to many table 关联表
post_tags = db.Table(
        'post_tags',
        db.Column('post_id', db.Integer, db.ForeignKey('post.id')),
        db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'))
        )


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64))
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    # 外键约束，强制要求category_id字段的值存在于category表的id列中
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    comments = db.relationship('Comment', backref='post', lazy='dynamic')
    # backref()函数接收第一个参数作为在关系另一侧添加的关系属性名
    # 其他关键字参数会作为关系另一侧关系函数的参数传入
    tags = db.relationship('Tag', secondary=post_tags,
                           backref=db.backref('posts'), lazy='dynamic')

    @property
    def year(self):
        return int(self.timestamp.year)

    def tag_in_post(self, tag):
        if ',' in self.tags:
            tags = [t for t in self.tags.split(',')]
            if tag in tags:
                return True
            return False
        else:
            # 只有一个标签
            if tag == self.tags:
                return True
            return False

    # markdown
    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul', 'h1',
                        'h2', 'h3', 'p']
        target.body_html = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, strip=True
        ))

    def __repr__(self):
        return '<Post {}>'.format(self.title)


db.event.listen(Post.body, 'set', Post.on_changed_body)


class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, index=True)

    def __repr__(self):
        return '<Tag {}>'.format(self.name)


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'code', 'em',
                        'i', 'strong']
        target.body_html = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags,
            strip=True
        ))


db.event.listen(Comment.body, 'set', Comment.on_changed_body)
