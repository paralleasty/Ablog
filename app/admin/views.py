from flask import render_template, flash, redirect, url_for, \
                  request, current_app, abort
from flask_login import login_required, current_user
from . import admin_bp
from ..main.forms import PostForm, CategoryForm, TagForm
from ..models import Post, Category, Tag
from app import db


@admin_bp.route('/post/manage')
@login_required
def manage_post():
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['MANAGE_POSTS_PER_PAGE']
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, per_page, False)
    posts = pagination.items
    return render_template('admin/manage_post.html', pagination=pagination,
                           posts=posts)


@admin_bp.route('/post/new', methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post()
        post.title = form.title.data
        post.body = form.body.data
        post.category = Category.query.get(form.category.data)
        db.session.add(post)
        db.session.commit()
        flash('You have been created a post')
        return redirect(url_for('main.post', post_id=post.id))
    return render_template('admin/new_post.html', form=form)


@admin_bp.route('/post/edit/<int:post_id>', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    form = PostForm()
    post = Post.query.get_or_404(post_id)
    if form.validate_on_submit():
        post.title = form.title.data
        post.body = form.body.data
        post.category = Category.query.get(form.category.data)
        db.session.commit()
        flash('Post have been updated')
        return redirect(url_for('main.post', post_id=post.id))
    form.title.data = post.title
    form.body.data = post.body
    form.category.data = post.category_id
    return render_template('admin/edit_post.html', form=form)


@admin_bp.route('/post/delete/<int:post_id>', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    flash('Post deleted')
    return redirect(url_for('admin.manage_post'))


@admin_bp.route('/category/manage')
@login_required
def manage_category():
    categories = Category.query.all()
    return render_template('admin/manage_category.html', categories=categories)


@admin_bp.route('/category/new', methods=['GET', 'POST'])
@login_required
def new_category():
    form = CategoryForm()
    if form.validate_on_submit():
        category = Category(name=form.name.data)
        db.session.add(category)
        db.session.commit()
        flash('Category created')
        return redirect(url_for('.manage_category'))
    return render_template('admin/new_category.html', form=form)


@admin_bp.route('/category/edit/<int:category_id>', methods=['GET', 'POST'])
@login_required
def edit_category(category_id):
    form = CategoryForm()
    category = Category.query.get_or_404(category_id)
    if category.id == 1:
        flash('You can not edit the default category')
        return redirect(url_for('main.index'))
    if form.validate_on_submit():
        category.name = form.name.data
        db.session.commit()
        flash('Category updated')
        return redirect(url_for('.manage_category'))
    form.name.data = category.name
    return render_template('admin/edit_category.html', form=form)


@admin_bp.route('/category/delete/<int:category_id>', methods=['POST'])
@login_required
def delete_category(category_id):
    category = Category.query.get_or_404(category_id)
    if category.id == 1:
        flash('You can not delete the default category')
        return redirect(url_for('main.index'))
    # 将该分类的posts移至默认分类中
    default_cate = Category.query.get(1)
    posts = category.posts
    for p in posts:
        p.category = default_cate
    db.session.delete(category)
    db.session.commit()
    flash('Category deleted')
    return redirect(url_for('.manage_category'))


@admin_bp.route('/post/<int:post_id>/tag/new', methods=['GET', 'POST'])
@login_required
def new_tag(post_id):
    post = Post.query.get_or_404(post_id)
    if current_user != post.user:
        abort(403)

    form = TagForm()
    if form.validate_on_submit():
        # 一篇文章往往有多个标签，在输入数据时，以空格分隔
        for e in form.tag.data.split():
            tag = Tag.query.filter_by(name=e).first()
            if tag is None:
                t = Tag(name=e)
                db.session.add(t)
                db.session.commit()
            # 新标签
            if tag not in post.tags:
                post.tags.append(tag)
                db.session.commit()
    return redirect(url_for('main.post', post_id=post_id))


@admin_bp.route('/post/<int:post_id>/<int:tag_id>/delete', methods=['POST'])
@login_required
def delete_tag(post_id, tag_id):
    tag = Tag.query.get_or_404(tag_id)
    post = Post.query.get_or_404(post_id)
    if current_user != post.user:
        abort(403)

    post.tags.remove(tag)
    db.session.commit()

    # 没有文章与之关联
    if not tag.posts:
        db.session.delete(tag)
        db.session.commit()

    return redirect(url_for('main.post', post_id=post_id))
