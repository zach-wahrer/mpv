from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired, Email


class MPVEmailForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    units = StringField('Units', validators=[DataRequired()])
