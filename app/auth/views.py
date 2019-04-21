from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from app import db
from app.auth import auth_bp
from app.auth.forms import LoginForm, RegistrationForm, ChangePasswordForm
from app.models import User


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    # 验证用户是否登录
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = LoginForm()
    if form.validate_on_submit():
        # user = User.query.filter_by(email=form.email.data).first()
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.validate_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('auth.login'))
        # 注册用户登录状态
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.index')
        return redirect(next_page)
    return render_template('auth/login.html', title='Sign In', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data,
                    email=form.email.data,
                    password=form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('main.index'))
    return render_template('auth/register.html', title='Register', form=form)


@auth_bp.route('/changepwd', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.validate_password(form.old_password.data):
            current_user.password = form.password.data
            db.session.add(current_user)
            db.commit()
            return redirect(url_for('main.index'))
        return redirect(url_for('auth.changepwd'))
    return render_template('auth/changepwd.html', form=form)
