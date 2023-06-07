from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, HiddenField, SelectField, RadioField, DateField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flask_login import current_user
from flask_babel import gettext, lazy_gettext
from dev.models import *
from dev import db
from datetime import datetime

class Add_Excel_Form(FlaskForm):

	file=FileField(lazy_gettext('Fichier source'), validators=[FileRequired(), FileAllowed(['xls', 'xlsx', 'csv'])], render_kw={"placeholder" : lazy_gettext(u'Ficheir source')})
	submit= SubmitField(lazy_gettext(u"Valider"))

class Add_Complaint_Form(FlaskForm):
	suppliers = Supplier.query.all()
	projects = Project.query.all()
	articles = Article.query.all()
	clients = Client.query.all()
	
	supplier = SelectField( lazy_gettext('Choisir un fournisseur :'), validators=[DataRequired()],  choices = [(supplier.id, supplier.name) for supplier in suppliers])
	deliveryForm= StringField( lazy_gettext('Bon de livraison'), render_kw={"placeholder" : lazy_gettext(u'Bon de livraison')})
	project = SelectField( lazy_gettext('Choisir le projet :'), validators=[DataRequired()],  choices = [(project.id, project.name) for project in projects])
	article = SelectField( lazy_gettext('Choisir l\'article :'), validators=[DataRequired()],  choices = [(article.id, article.internaltCode) for article in articles])
	client = SelectField( lazy_gettext('Choisir le client :'), validators=[DataRequired()],  choices = [(client.id, client.name) for client in clients])
	suspectQuantity= StringField( lazy_gettext('Quantité suspect'), render_kw={"placeholder" : lazy_gettext(u'Quantité suspect')})
	detectionZone= RadioField( lazy_gettext('Zone de détection'), choices=[('reception','Réception'),('production','Production'),('client','Client')], validators=[DataRequired()])
	problemDescription= TextAreaField( lazy_gettext('Description du problème'), render_kw={"placeholder" : lazy_gettext(u'Description du problème')})
	verificationMethod= StringField( lazy_gettext('Méthode de vérification'), render_kw={"placeholder" : lazy_gettext(u'Méthode de vérification')})
	file=FileField(lazy_gettext('Photos'), validators=[FileAllowed(['jpeg', 'jpg', 'png', 'gif'])], render_kw={"placeholder" : lazy_gettext(u'Photos')})
	submit= SubmitField(lazy_gettext(u"  Valider  "))
	
	def validate_suspectQuantity(self, suspectQuantity):
		if not(suspectQuantity.data.isnumeric()):
			raise ValidationError('Vérifier la quantité suspect')

class Update_Complaint_Form(FlaskForm):
	suppliers = Supplier.query.all()
	projects = Project.query.all()
	articles = Article.query.all()
	clients = Client.query.all()
	
	number= StringField( lazy_gettext('numéro'), render_kw={"placeholder" : lazy_gettext(u'numéro')})
	supplier = SelectField( lazy_gettext('Choisir un fournisseur :'), validators=[DataRequired()],  choices = [(supplier.id, supplier.name) for supplier in suppliers])
	deliveryForm= StringField( lazy_gettext('Bon de livraison'), render_kw={"placeholder" : lazy_gettext(u'Bon de livraison')})
	project = SelectField( lazy_gettext('Choisir le projet :'), validators=[DataRequired()],  choices = [(project.id, project.name) for project in projects])
	article = SelectField( lazy_gettext('Choisir l\'article :'), validators=[DataRequired()],  choices = [(article.id, article.internaltCode) for article in articles])
	client = SelectField( lazy_gettext('Choisir le client :'), validators=[DataRequired()],  choices = [(client.id, client.name) for client in clients])
	suspectQuantity= StringField( lazy_gettext('Quantité suspect'), render_kw={"placeholder" : lazy_gettext(u'Quantité suspect')})
	detectionZone= RadioField( lazy_gettext('Zone de détection'), choices=[('reception','Réception'),('production','Production'),('client','Client')], validators=[DataRequired()])
	problemDescription= TextAreaField( lazy_gettext('Description du problème'), render_kw={"placeholder" : lazy_gettext(u'Description du problème')})
	verificationMethod= StringField( lazy_gettext('Méthode de vérification'), render_kw={"placeholder" : lazy_gettext(u'Méthode de vérification')})
	submit= SubmitField(lazy_gettext(u"  Soumettre  "))
	
	def validate_suspectQuantity(self, suspectQuantity):
		if not(suspectQuantity.data.isnumeric()):
			raise ValidationError('Vérifier la quantité suspect')

class Add_Team_Form(FlaskForm):

	firstName= StringField( lazy_gettext('Prénom'), validators=[DataRequired()], render_kw={"placeholder" : lazy_gettext(u'Prénom')})
	lastName= StringField( lazy_gettext('Nom'), validators=[DataRequired()], render_kw={"placeholder" : lazy_gettext(u'Nom')})
	function= StringField( lazy_gettext('Fonction'), validators=[DataRequired()], render_kw={"placeholder" : lazy_gettext(u'Fonction')})
	submit= SubmitField(lazy_gettext(u"Valider"))

class Describe_Problem_Form(FlaskForm):

	problem= TextAreaField( lazy_gettext('Problème'), validators=[DataRequired()], render_kw={"placeholder" : lazy_gettext(u'Problème')})
	file=FileField(lazy_gettext('Photos'), validators=[FileAllowed(['jpeg', 'jpg', 'png', 'gif'])], render_kw={"placeholder" : lazy_gettext(u'Photos')})
	submit= SubmitField(lazy_gettext(u"Valider"))

class Add_3DAction_Form(FlaskForm):
	action= TextAreaField( lazy_gettext('Action'), validators=[DataRequired()], render_kw={"placeholder" : lazy_gettext(u'Action')})
	owner= StringField( lazy_gettext('Responsable'), validators=[DataRequired()], render_kw={"placeholder" : lazy_gettext(u'Responsable')})
	submit= SubmitField(lazy_gettext(u"Valider"))

class Add_Cause_Form(FlaskForm):
	cause= TextAreaField( lazy_gettext('Cause'), validators=[DataRequired()], render_kw={"placeholder" : lazy_gettext(u'Cause')})
	submit= SubmitField(lazy_gettext(u"Valider"))

class Add_5DAction_Form(FlaskForm):
	action= TextAreaField( lazy_gettext('Action'), validators=[DataRequired()], render_kw={"placeholder" : lazy_gettext(u'Action')})
	owner= StringField( lazy_gettext('Responsable'), validators=[DataRequired()], render_kw={"placeholder" : lazy_gettext(u'Responsable')})
	type= RadioField( lazy_gettext('Type de l\'action'), choices=[('occurence','Occurence'),('non detection','Non detection')], validators=[DataRequired()])
	submit= SubmitField(lazy_gettext(u"Valider"))

class Add_7DAction_Form(FlaskForm):
	action= TextAreaField( lazy_gettext('Action'), validators=[DataRequired()], render_kw={"placeholder" : lazy_gettext(u'Action')})
	owner= StringField( lazy_gettext('Responsable'), validators=[DataRequired()], render_kw={"placeholder" : lazy_gettext(u'Responsable')})
	submit= SubmitField(lazy_gettext(u"Valider"))

def numeric_check(form,field):
		if not(field.data.isnumeric()):
			raise ValidationError('Ce champs doit être numérique!')