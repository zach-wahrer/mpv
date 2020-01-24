from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired, Email


class MPVEmailForm(FlaskForm):
    email = StringField(label='Email', validators=[DataRequired(), Email()])
    units = StringField(label='Units', validators=[DataRequired()])
