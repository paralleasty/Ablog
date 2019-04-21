from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Length, ValidationError, Optional
from flask_pagedown.fields import PageDownField
from ..models import Category


class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(1, 80)])
    category = SelectField('Category', coerce=int, default=1)
    # category = StringField('Category', validators=[DataRequired()])
    tags = StringField('Tag', validators=[DataRequired()])
    # body = TextAreaField('Body', validators=[DataRequired()])
    body = PageDownField('Body', validators=[DataRequired()])
    submit = SubmitField()

    def __init__(self, *args, **kwargs):
        super(PostForm, self).__init__(*args, **kwargs)
        self.category.choices = [(category.id, category.name)
            for category in Category.query.order_by(Category.name).all()]


class CategoryForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(1, 32)])
    submit = SubmitField('Submit')

    def validate_name(self, field):
        if Category.query.filter_by(name=field.data).first():
            raise ValidationError('Name already in use.')


class TagForm(FlaskForm):
    # Optional()允许输入值为空，并跳过其他验证
    name = StringField('Tag (use space to separate',
                       validators=[Optional(), Length(0, 64)])
    submit = SubmitField()


class CommentForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(1, 64)])
    body = TextAreaField('Comment', validators=[DataRequired()])
    submit = SubmitField('Submit')
