
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, HiddenField, SelectField, RadioField, DateField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flask_login import current_user
from flask_babel import gettext, lazy_gettext
from dev.models import User

class LoginForm(FlaskForm):
	email=StringField(lazy_gettext('Login'), validators=[DataRequired(), Email()], render_kw={"placeholder" : lazy_gettext(u'Entrez votre Email')})
	remember=BooleanField(lazy_gettext('Se souvenir'))
	password=PasswordField(lazy_gettext('Password'), validators=[DataRequired()], render_kw={"placeholder" : lazy_gettext(u'Entrez votre mot de passe')})
	submit=SubmitField(lazy_gettext(u"Se connecter"))