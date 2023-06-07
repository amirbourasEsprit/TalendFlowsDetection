from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, HiddenField, SelectField, RadioField, DateField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flask_login import current_user
from flask_babel import gettext, lazy_gettext
from dev.models import *
from dev import db
from datetime import datetime


def numeric_check(form,field):
		if not(field.data.isnumeric()):
			raise ValidationError('Ce champs doit être numérique!')

class Add_Cost_Line_Form(FlaskForm):
	code = SelectField("Code Frais",  choices = [])
	unit = StringField('Unité',render_kw = {'disabled': 'disabled'})
	unitcost = StringField('Prix Unitaire',validators=[
		DataRequired(message='Ce champs est obligatoire!'),
		Length(min=2,max=30,message='Le nom doit être entre 2 et 30 caractères!')
		])
	quantity = StringField('Quantité',validators=[DataRequired(message='Ce champs est obligatoire!'),numeric_check])
	othercost = StringField('Autre Coût',validators=[DataRequired(message='Ce champs est obligatoire!')])
	coefficient = StringField('Coefficient',validators=[DataRequired(message='Ce champs est obligatoire!')])
	comment = TextAreaField('Commentaire')
	submitadd = SubmitField('Ajouter')

	def validate_unitcost(self,unitcost):
		if not(unitcost.data.isnumeric()):
			print("wrong")
			raise ValidationError('Ce champs doit être numérique!')
	def validate_quantity(self,quantity):
		if not(quantity.data.isnumeric()):
			print("wrong")
			raise ValidationError('Ce champs doit être numérique!')

class Update_Cost_Line_Form(FlaskForm):
	identifier = StringField("")
	code = StringField("Code Frais",render_kw = {'disabled': 'disabled'})
	unit = StringField('Unité',render_kw = {'disabled': 'disabled'})
	unitcost = StringField('Prix Unitaire',validators=[DataRequired(message='Ce champs est obligatoire!')])
	quantity = StringField('Quantité',validators=[DataRequired(message='Ce champs est obligatoire!')])
	othercost = StringField('Autre Coût',validators=[DataRequired(message='Ce champs est obligatoire!')])
	coefficient = StringField('Coefficient',validators=[DataRequired(message='Ce champs est obligatoire!')])
	comment = TextAreaField('Commentaire')
	submitupdate = SubmitField('Valider')

class Add_Declaration_Form(FlaskForm):
	complaints = db.session.query(ComplaintTable).all()
	complaint = SelectField("Réclamation", validators=[DataRequired()],  choices = [(complaint.id, 'REC-'+complaint.number) for complaint in complaints])
	supplier = StringField("Fournisseur",render_kw = {'disabled': 'disabled'})
	submit = SubmitField("Ajouter")