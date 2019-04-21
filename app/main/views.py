from flask import render_template, redirect, flash, url_for, current_app,\
    request, abort
from app import db
from app.models import Post, Category, Comment, User, Tag
from .forms import CommentForm
from . import main_bp


@main_bp.route('/index')
@main_bp.route('/')
def index():
    # 获取当前页数
    page = request.args.get('page', 1, type=int)
    # pagination()方法得到分页对象
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, current_app.config['POSTS_PER_PAGE'], False)
    # next_url = url_for('main.index', page=pagination.next_num) \
    #     if pagination.has_next else None
    # prev_url = url_for('main.index', page=pagination.prev_num) \
    #     if pagination.has_prev else None
    posts = pagination.items
    return render_template('index.html', pagination=pagination, posts=posts)


@main_bp.route('/about')
def about():
    return render_template('about.html')


@main_bp.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        abort(400)
    return render_template('user.html', user=user)


@main_bp.route('/archives')
def archives():
    # count = Post.query.count()
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, current_app.config['POSTS_PER_PAGE'], False)
    posts = pagination.items
    year = list(set([post.year for post in posts]))[::-1]
    data = {}
    year_posts = []
    for y in year:
        for p in posts:
            if y == p.year:
                year_posts.append(p)
                data[y] = year_posts
        year_posts = []

    return render_template('archives.html', posts=posts,
                           year=year, data=data, pagination=pagination)


@main_bp.route('/categories')
def categories():
    categories = Category.query.all()
    return render_template('categories.html', categories=categories)


@main_bp.route('/category/<int:category_id>')
def posts_by_category(category_id):
    category = Category.query.get_or_404(category_id)
    page = request.args.get('page', 1, type=int)
    pagination = category.posts.order_by(Post.timestamp.desc()).paginate(
        page, current_app.config['POSTS_PER_PAGE'], False)
    posts = pagination.items
    return render_template('posts_by_category.html', category=category,
                           pagination=pagination, posts=posts)


@main_bp.route('/tag/<name>')
def posts_by_tag(name):
    tag = Tag.query.filter_by(name=name).first_or_404()
    # posts = tag.posts.order_by(Post.timestamp.desc())
    page = request.args.get('page', 1, type=int)
    order = Post.query.filter_by(Post.tags.any(id=tag.id)).order_by(
                                 Post.timestamp())
    pagination = order.pagintion(page, current_app.config['POSTS_PER_PAGE'],
                                 False)
    posts = pagination.items
    return render_template('posts_by_tag.html', tag=tag,
                           paginaton=pagination, posts=posts)


@main_bp.route('/post/<int:post_id>', methods=['GET', 'POST'])
def post(post_id):
    post = Post.query.get_or_404(post_id)
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['COMMENT_PER_PAGE']
    pagination = post.comments.order_by(Comment.timestamp.asc()).paginate(
        page, per_page, False)
    comments = pagination.items
    form = CommentForm()
    if form.validate_on_submit():
        new_comment = Comment(name=form.name.data, body=form.body.data)
        new_comment.post_id = post_id
        try:
            db.session.add(new_comment)
            db.session.commit()
        except Exception as e:
            flash('Error adding your comment: {}'.format(str(e)), 'error')
        else:
            flash('Comment added')
        return redirect(url_for('.post', post_id=post_id))

    return render_template('post.html', post=post, pagination=pagination,
                           form=form, comments=comments)
