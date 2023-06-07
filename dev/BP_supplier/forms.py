from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, HiddenField, SelectField, RadioField, DateField, TextAreaField, SelectMultipleField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flask_login import current_user
from flask_babel import gettext, lazy_gettext
from dev.models import *
from dev import db
from datetime import datetime

class Select2MultipleField(SelectMultipleField):

    def pre_validate(self, form):
        # Prevent "not a valid choice" error
        pass

    def process_formdata(self, valuelist):
        if valuelist:
            self.data = "".join(valuelist)
        else:
            self.data = ""

class Update_Logo_Form(FlaskForm):

	file=FileField(lazy_gettext('Logo'), validators=[FileAllowed(['jpeg', 'jpg', 'png', 'gif'])], render_kw={"placeholder" : lazy_gettext(u'Logo')})
	submit= SubmitField(lazy_gettext(u"Valider"))

class Add_Excel_Form(FlaskForm):

	file=FileField(lazy_gettext('Fichier source'), validators=[FileRequired(), FileAllowed(['xls', 'xlsx', 'csv'])], render_kw={"placeholder" : lazy_gettext(u'Ficheir source')})
	submit= SubmitField(lazy_gettext(u"Valider"))

class Add_Supplier_Charge_Form(FlaskForm):
	code = SelectField("Code Frais",  choices = [])
	unit = StringField('Unité',render_kw = {'disabled': 'disabled'})
	unitcost = StringField('Prix Unitaire',) 
	currency = StringField('Devise',render_kw = {'disabled': 'disabled'})
	submit = SubmitField(' Ajouter  ')	



class Update_Supplier_Charge_Form(FlaskForm):
	code = StringField("Code Frais",render_kw = {'disabled': 'disabled'})
	unit = StringField('Unité',render_kw = {'disabled': 'disabled'})
	unitcost = StringField('Prix Unitaire') 
	currency = StringField('Devise',render_kw = {'disabled': 'disabled'})

	submit = SubmitField('  Valider  ')	

def numeric_check(form,field):
		if not(field.data.isnumeric()):
			raise ValidationError('Ce champs doit être numérique!')

class Update_Supp_profile_Form(FlaskForm):
	
	uniqueIdentifier= StringField( lazy_gettext('Identifiant Unique'), render_kw={"placeholder" : lazy_gettext(u'Identifiant Unique')})
	name= StringField( lazy_gettext('Nom'), validators=[DataRequired()], render_kw={"placeholder" : lazy_gettext(u'Nom')})
	jalan3D= StringField( lazy_gettext('jalan3D'), validators=[numeric_check], render_kw={"placeholder" : lazy_gettext(u'jalan3D')})
	jalan5D= StringField( lazy_gettext('jalan5D'), validators=[numeric_check], render_kw={"placeholder" : lazy_gettext(u'jalan5D')})
	jalan8D= StringField( lazy_gettext('jalan8D'), validators=[numeric_check], render_kw={"placeholder" : lazy_gettext(u'jalan8D')})
	initialResponse= StringField( lazy_gettext('Réponse initiale'), validators=[numeric_check], render_kw={"placeholder" : lazy_gettext(u'Réponse initiale')})
	finalResponse= StringField( lazy_gettext('Réponse finale'), validators=[numeric_check], render_kw={"placeholder" : lazy_gettext(u'Réponse finale ')})
	adresse= StringField( lazy_gettext('Adresse'), render_kw={"placeholder" : lazy_gettext(u'Adresse')})
	phone= StringField( lazy_gettext('Numéro du téléphone'), render_kw={"placeholder" : lazy_gettext(u'Numéro du téléphone')})
	fax= StringField( lazy_gettext('Numéro du fax'), render_kw={"placeholder" : lazy_gettext(u'Numéro du fax')})
	currency = SelectField('Devise',  choices = [('Euro','Euro'),('Dollar','Dollar'),('Dinar','Dinar')])
	taxRegisration= StringField( lazy_gettext('Matricule Fiscal'), render_kw={"placeholder" : lazy_gettext(u'Matricule Fiscal')})
	submit= SubmitField(lazy_gettext("  Valider  "))

class Update_Supp_profile_Form2(FlaskForm):
	categories = SuppCategory.query.all()

	category=SelectField( lazy_gettext('Choisir catégorie fournisseur :'),  choices = [(category.id, category.name) for category in categories])
	status = SelectField('Status',  choices = [('Identification','Identification'),('Souscription','Souscription'),('Essai','Essai'),('Validation','Validation'),('Mode serie','Mode série')])
	submit= SubmitField(lazy_gettext("  Valider  "))

class Edit_VisVis_Form(FlaskForm):
	sysusers = SysUser.query.all()
	suppusers = SuppUser.query.all()

	sys_user1 = Select2MultipleField( lazy_gettext('Choisir les vis à vis coté société :'), choices = [(sysuser.id, sysuser.firstName +" "+ sysuser.lastName) for sysuser in sysusers])
	supp_user1 = Select2MultipleField( lazy_gettext('Choisir les vis à vis coté fournisseur :'), choices = [(suppuser.id, suppuser.firstName +" " + suppuser.lastName) for suppuser in suppusers])
	sys_user2 = Select2MultipleField( lazy_gettext('Choisir les vis à vis coté société  :'), choices = [(sysuser.id, sysuser.firstName +" "+ sysuser.lastName) for sysuser in sysusers])
	supp_user2 = Select2MultipleField( lazy_gettext('Choisir les vis à vis coté fournisseur :'), choices = [(suppuser.id, suppuser.firstName +" " + suppuser.lastName) for suppuser in suppusers])
	sys_user3 = Select2MultipleField( lazy_gettext('Choisir les vis à vis coté société  :'), choices = [(sysuser.id, sysuser.firstName +" " + sysuser.lastName) for sysuser in sysusers])
	supp_user3 = Select2MultipleField( lazy_gettext('Choisir les vis à vis coté fournisseur :'), choices = [(suppuser.id, suppuser.firstName +" " + suppuser.lastName) for suppuser in suppusers])
	submit= SubmitField(lazy_gettext("  Valider  "))

class Add_qualitymanual_Form(FlaskForm):
	name= StringField( lazy_gettext('Nom'), validators=[DataRequired()], render_kw={"placeholder" : lazy_gettext(u'Nom')})
	attachement=FileField(lazy_gettext('Document'), validators=[FileAllowed(['jpeg', 'jpg', 'png', 'gif','pdf'])], render_kw={"placeholder" : lazy_gettext(u'Document')})
	submit= SubmitField(lazy_gettext(u"  Valider  "))

class Add_certificate_Form(FlaskForm):
	certificates= CertificationType.query.all()
	type = SelectField( lazy_gettext('Choisir type certificat :'), validators=[DataRequired()],  choices = [(certificate.id, certificate.name) for certificate in certificates])
	name= StringField( lazy_gettext('Nom'), validators=[DataRequired()], render_kw={"placeholder" : lazy_gettext(u'Nom')})
	expirationDate=DateField( lazy_gettext('Date d\'expiration'), validators=[DataRequired()], format='%Y-%m-%d', render_kw={"placeholder" : lazy_gettext(u'Date d\'expiration')} )
	attachement=FileField(lazy_gettext('Document'), validators=[FileAllowed(['jpeg', 'jpg', 'png', 'gif','pdf'])], render_kw={"placeholder" : lazy_gettext(u'Document')})
	submit= SubmitField(lazy_gettext(u"  Valider  "))

class Add_suppContact_Form(FlaskForm):

	firstName= StringField( lazy_gettext('Nom'), validators=[DataRequired()], render_kw={"placeholder" : lazy_gettext(u'Nom')})
	lastName= StringField( lazy_gettext('Prénom'), validators=[DataRequired()], render_kw={"placeholder" : lazy_gettext(u'Prénom')})
	function= StringField( lazy_gettext('Fonction'), validators=[DataRequired()], render_kw={"placeholder" : lazy_gettext(u'Fonction')})
	phone= StringField( lazy_gettext('Numéro du téléphone'),validators=[DataRequired()], render_kw={"placeholder" : lazy_gettext(u'Numéro du téléphone')})
	email= StringField( lazy_gettext('Email'), validators=[Email()], render_kw={"placeholder" : lazy_gettext(u'Email')})
	submit= SubmitField(lazy_gettext(u"  Valider  "))

class Update_Supp_contact_Form(FlaskForm):

	firstName= StringField( lazy_gettext('Nom'), validators=[DataRequired()], render_kw={"placeholder" : lazy_gettext(u'Nom')})
	lastName= StringField( lazy_gettext('Prénom'), validators=[DataRequired()], render_kw={"placeholder" : lazy_gettext(u'Prénom')})
	function= StringField( lazy_gettext('Fonction'), validators=[DataRequired()], render_kw={"placeholder" : lazy_gettext(u'Fonction')})
	phone= StringField( lazy_gettext('Numéro du téléphone'),validators=[DataRequired()], render_kw={"placeholder" : lazy_gettext(u'Numéro du téléphone')})
	email= StringField( lazy_gettext('Email'), validators=[Email()], render_kw={"placeholder" : lazy_gettext(u'Email')})
	submit= SubmitField(lazy_gettext(u"  Valider  "))

class Update_Supp_certificate_Form(FlaskForm):
	
	name= StringField( lazy_gettext('Nom'), validators=[DataRequired()], render_kw={"placeholder" : lazy_gettext(u'Nom')})
	submit= SubmitField(lazy_gettext(u"  Valider  "))