from flask import render_template, g, url_for, request, flash, Markup, send_file, send_from_directory, redirect, jsonify, abort, Blueprint, request, current_app
from flask_login import login_user, current_user, logout_user, login_required
from dev import db, bcrypt, app
from dev.models import *
from dev.BP_auth.forms import LoginForm
#from dev.BP_auth.utils import save_picture, senEmail, send_mail, send_reset_email
from dev.BP_admin.forms import *
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadTimeSignature
from flask_babel import Babel, format_date, gettext
from datetime import datetime, timedelta
from sqlalchemy.exc import IntegrityError
from werkzeug.utils import secure_filename
from dev.BP_admin.utils import *
#from dev.flaskadmin import *
from io import BytesIO
from os.path import join, dirname, realpath
import pandas as pd
import xlrd
import openpyxl
import traceback
import uuid
import sys
import os
import subprocess
import numpy as np
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.ensemble import RandomForestRegressor
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder


admin = Blueprint('admin', __name__)
s=URLSafeTimedSerializer(app.config['SECRET_KEY'])
COMP_ATT_PATH = 'C:/Users/boura/Desktop/testflask/SRM-Project/SRM-MAIN/app/dev/static/img/ComplaintAttachement'
COMP_ATT_ALLOWED_EXT={'jpeg', 'jpg', 'png', 'gif'}
REP8D_ATT_PATH='C:/Users/boura/Desktop/testflask/SRM-Project/SRM-MAIN/app/dev/static/img/Attachement8D'
REP8D_ATT_ALLOWED_EXT={'jpeg', 'jpg', 'png', 'gif'}
COMP_LOGO_PATH='C:/Users/boura/Desktop/testflask/SRM-Project/SRM-MAIN/app/dev/static/img/CompanyLogo'
COMP_LOGO_ALLOWED_EXT={'jpeg', 'jpg', 'png', 'gif'}
SUPP_LOGO_PATH='C:/Users/boura/Desktop/testflask/SRM-Project/SRM-MAIN/app/dev/static/img/SupplierLogo'
SUPP_LOGO_ALLOWED_EXT={'jpeg', 'jpg', 'png', 'gif'}
CERTIF_ATT_PATH ='C:/Users/boura/Desktop/testflask/SRM-Project/SRM-MAIN/app/dev/documents_directory/certif_doc'
ALLOWED_EXTENSIONS = { 'pdf','jpeg', 'jpg', 'png', 'gif'}

@admin.route("/index", methods=['GET', 'POST'])
@login_required
def index():
	roles = []
	for i in range(len(current_user.roles)):
		roles.append(current_user.roles[i].name)

	companies = db.session.query(Company).count()
	sites = db.session.query(Site).count()
	suppliers = db.session.query(Supplier).count()
	complaints = db.session.query(ComplaintTable).count()
	reports = db.session.query(Report8D).count()
	declarations = db.session.query(CostDeclarationTable).count()

	myDict = {
		'legend' : gettext("Index Page"),
		'menu' : {},
		'title' : 'Index',
	}
	return render_template("admin/index.html", myDict=myDict, companies=companies, sites=sites, complaints=complaints, reports=reports, declarations=declarations, suppliers=suppliers)#, roles=roles

@admin.route("/predicatefiras", methods=['GET', 'POST'])
@login_required
def predicatefiras():
	roles = []
	for i in range(len(current_user.roles)):
		roles.append(current_user.roles[i].name)
	
	form = predicatefirasForm()
	if form.validate_on_submit():
		
		df = pd.read_csv('C:/Users/boura/Desktop/testflask/SRM-Project/SRM-MAIN/app/dev/static/img/jobs2.csv', names=["job", "count", "duration"], encoding='latin-1')

		X = df[['count']]
		y = df['duration']

		model = RandomForestRegressor()
		model.fit(X, y)

		new_count = int(form.parameter.data)   # Or set it as desired

		new_duration = model.predict([[new_count]])

		
		output= str(new_duration[0])
	

		
		flash('For the Count '+str(new_count)+' The Predicate Value of duration is : '+ output, 'success')
		return redirect(url_for('admin.predicatefiras', output=output))

	myDict = {
		'form' : form,
		'legend' : gettext("predicate Page"),
		'menu' : {},
		'title' : 'predicate',
	}
	return render_template("admin/predicatefiras.html", myDict=myDict)#, roles=roles

@admin.route("/predicatechadhaArij", methods=['GET', 'POST'])
@login_required
def predicatechadhaArij():
	roles = []
	for i in range(len(current_user.roles)):
		roles.append(current_user.roles[i].name)
	
	form = predicatechadhaArijForm()
	if form.validate_on_submit():
		df = pd.read_csv('C:/Users/boura/Desktop/testflask/SRM-Project/SRM-MAIN/app/dev/static/img/jobs1.csv')
		version_mapping = {version: label for label, version in enumerate(df['Version'].unique())}

		# Map the 'Version' column to numerical labels
		df['VersionLabel'] = df['Version'].map(version_mapping)

		# Split the dataset into features (duration) and target (version label)
		X = df['Duration'].values.reshape(-1, 1)
		y = df['VersionLabel']

		# Split the dataset into training and testing sets
		X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=20, random_state=42)

		# Create a Random Forest classifier
		classifier = RandomForestClassifier(random_state=42)

		# Train the classifier
		classifier.fit(X_train, y_train)
		
		# Predict the version label based on the input duration
		input_duration = int(form.parameter.data)
		predicted_version_label = classifier.predict([[input_duration]])

		# Map the predicted label back to the original version
		predicted_version = next(version for version, label in version_mapping.items() if label == predicted_version_label)

		
		output = str(predicted_version)
	
		flash('For the Duration '+ str(input_duration) +' The Predicate Value of Version is : '+ output, 'success')
		return redirect(url_for('admin.predicatechadhaArij', output=output))

	myDict = {
		'form' : form,
		'legend' : gettext("predicate Page"),
		'menu' : {},
		'title' : 'predicate',
	}
	return render_template("admin/predicatechadhaArij.html", myDict=myDict)#, roles=roles

@admin.route("/predicateAmirAnis", methods=['GET', 'POST'])
@login_required
def predicateAmirAnis():
	roles = []
	for i in range(len(current_user.roles)):
		roles.append(current_user.roles[i].name)
	
	form = predicateAmirAnisForm()
	
	if form.validate_on_submit():
		df=pd.read_csv('C:/Users/boura/Desktop/testflask/SRM-Project/SRM-MAIN/app/dev/static/img/flows.csv')
		#df.shape
		# Find the number of duplicate rows
		num_duplicates = df.duplicated().sum()
		#print(f"There are {num_duplicates} duplicate rows in the dataset.")

		# Drop duplicate rows from the dataframe : nsetti l index une autre fois 
		df.drop_duplicates(inplace=True)

		# Verify that duplicates have been dropped
		#print(f"The new dataframe has {len(df)} rows and {len(df.columns)} columns.")
		# Drop the 'reference' and 'thresholds' columns psk 100 % NULL 
		df = df.drop(columns=['father_pid','root_pid','reference', 'thresholds','context','label'])

		# convert "moment" column to datetime type
		df['moment'] = pd.to_datetime(df['moment'])

		#Generation d un nouveau feature engineering

		# extract year, month, day, hour, minute, and second from the "moment" column
		df['year'] = df['moment'].dt.year
		df['month'] = df['moment'].dt.month
		df['day'] = df['moment'].dt.day
		df['hour'] = df['moment'].dt.hour
		df['minute'] = df['moment'].dt.minute


		# drop the "moment" column
		df = df.drop('moment', axis=1)

		# show the resulting DataFrame
		#df



		# Create a new instance of LabelEncoder for each variable
		encoder_pid = LabelEncoder()
		encoder_project = LabelEncoder()
		encoder_job = LabelEncoder()
		encoder_job_repository_id = LabelEncoder()
		encoder_origin = LabelEncoder()

		# Fit the encoders on the respective columns
		encoder_pid.fit(df['pid'])
		encoder_project.fit(df['project'])
		encoder_job.fit(df['job'])
		encoder_job_repository_id.fit(df['job_repository_id'])
		encoder_origin.fit(df['origin'])

		# Transform the columns using the respective encoders
		df['pid'] = encoder_pid.transform(df['pid'])
		df['project'] = encoder_project.transform(df['project'])
		df['job'] = encoder_job.transform(df['job'])
		df['job_repository_id'] = encoder_job_repository_id.transform(df['job_repository_id'])
		df['origin'] = encoder_origin.transform(df['origin'])

		#print(df)

		input_data = {
			'pid': form.pid.data,
			'system_pid': form.system_pid.data,
			'project': form.project.data,
			'job': form.job.data,
			'job_repository_id': form.job_repository_id.data,
			'job_version': form.job_version.data,
			'origin': form.origin.data,
			'year': form.year.data,
			'month': form.month.data,
			'day': form.day.data,
			'hour': form.hour.data,
			'minute': form.minute.data
		}

		# Convert the input dictionary to a DataFrame
		input_df = pd.DataFrame(input_data, index=[0])

		# Perform the same data preprocessing steps as before
		input_df['pid'] = encoder_pid.transform(input_df['pid'])
		input_df['project'] = encoder_project.transform(input_df['project'])
		input_df['job'] = encoder_job.transform(input_df['job'])
		input_df['job_repository_id'] = encoder_job_repository_id.transform(input_df['job_repository_id'])
		input_df['origin'] = encoder_origin.transform(input_df['origin'])
		#print(input_df)
		# split the data into training and testing sets
		X_train, X_test, y_train, y_test = train_test_split(df.drop('count', axis=1), df['count'], test_size=0.2, random_state=42)

		# define the parameter grid for RandomForestRegressor
		rf_param_grid = {
			'n_estimators': [100, 200],
			'max_depth': [ 5, 10],
		}

		# create a Random Forest Regressor model and perform grid search
		rf_model = RandomForestRegressor(random_state=42)
		rf_grid = GridSearchCV(rf_model, rf_param_grid, cv=5)
		rf_grid.fit(X_train, y_train)


		# Make the prediction using the trained model
		prediction = rf_grid.predict(input_df)
		predic= (prediction[0])
		# Print the predicted job version
		#print("Predicted count:", prediction[0])
		
		flash(' The Predicate Value of Count is :'+ str(predic) , 'success')
		return redirect(url_for('admin.predicateAmirAnis', ))

	myDict = {
		'form' : form,
		'legend' : gettext("predicate Page"),
		'menu' : {},
		'title' : 'predicate',
	}
	return render_template("admin/predicateAmirAnis.html", myDict=myDict)#, roles=roles

@admin.route("/profile", methods=['GET', 'POST'])
@login_required
def profile():
	roles = []
	for i in range(len(current_user.roles)):
		roles.append(current_user.roles[i].name)
	company=""
	supplier=""
	if current_user.type=='sysuser':
		company = db.session.query(Company).filter(Company.id==db.session.query(Site).filter(Site.id==db.session.query(SysUser).filter(SysUser.id==current_user.id).first().site_id).first().company_id).first()
	elif current_user.type=='suppuser':
		supplier = db.session.query(Supplier).filter(Supplier.id==current_user.supplier.id).first()
	myDict = {
		'legend' : gettext("profile"),
		'menu' : {},
		'title' : 'profile',
	}
	return render_template("admin/profile.html", myDict=myDict, company=company, supplier=supplier, roles=roles)

@admin.route("/update_profile/<int:user_id>", methods=['GET', 'POST'])
@login_required
def update_profile(user_id):
	roles = []
	for i in range(len(current_user.roles)):
		roles.append(current_user.roles[i].name)

	user=db.session.query(User).filter(User.id==user_id).first()
	form = Update_Profile_Form()
	f2 = Update_Password_Form()

	if form.validate_on_submit():
		user.firstName=form.firstName.data
		user.lastName=form.lastName.data
		user.email=form.email.data
		user.phone=form.phone.data
		db.session.commit()
		flash('Vos informations sont bien mises à jour', 'success')
		return redirect(url_for('admin.profile', user_id=user.id))
	elif request.method == 'GET':
		form.firstName.data=user.firstName
		form.lastName.data=user.lastName
		form.email.data=user.email
		form.phone.data=user.phone
	myDict = {
		'form' : form,
		'f2': f2,
		'legend' : gettext("Mise à jour du profile"),
		'menu' : {},
		'title' : 'Mise à jour du profile',
	}
	return render_template("admin/update_profile.html", myDict=myDict, roles=roles)

@admin.route("/update_password/<int:user_id>", methods=['GET', 'POST'])
@login_required
def update_password(user_id):
	user=db.session.query(User).filter(User.id==user_id).first()
	f2 = Update_Password_Form()

	if f2.validate_on_submit():
		if (bcrypt.check_password_hash(user.password, f2.old_password.data)):
			hashed_password = bcrypt.generate_password_hash(f2.new_password.data).decode('utf-8')
			user.password=hashed_password
			db.session.commit()
			flash('Votre mot de passe est bien mise à jour', 'success')
			return redirect(url_for('admin.update_profile', user_id=user.id))
		else:
			flash('Vérifiez votre mot de passe actuel', 'danger')
			return redirect(url_for('admin.update_profile', user_id=user.id))
	else:
		flash('Confirmez votre nouveaumot de passe', 'danger')
		return redirect(url_for('admin.update_profile', user_id=user.id))

@admin.route("/access_user", methods=['GET', 'POST'])
@login_required
def access_user():
	roles = []
	for i in range(len(current_user.roles)):
		roles.append(current_user.roles[i].name)
	if 'super_admin' not in roles:
		flash('Vous n\'avez pas l\'accès', 'danger')
		return redirect(url_for('admin.index'))

	companies = db.session.query(Company).all()
	suppliers = db.session.query(Supplier).all()

	myDict = {
		'legend' : gettext("Utilisateurs"),
		'menu' : {},
		'title' : 'Utilisateurs',
	}
	return render_template("admin/access_user.html", myDict=myDict, companies=companies, suppliers=suppliers, roles=roles)

@admin.route("/sit/<company>")
@login_required
def sit(company):
	sites = Site.query.filter_by(company_id=company).all()
	s_list = []
	for site in sites:
		sObj = {}
		sObj['id'] = site.id
		sObj['name'] = site.name
		s_list.append(sObj)
	return jsonify({'sites' : s_list})

@admin.route("/sysuser", methods=['GET', 'POST'])
@login_required
def sysuser():
	roles = []
	for i in range(len(current_user.roles)):
		roles.append(current_user.roles[i].name)
	if 'super_admin' not in roles:
		flash('Vous n\'avez pas l\'accès', 'danger')
		return redirect(url_for('admin.index'))

	sysusers = db.session.query(SysUser).all()

	def select_name(param_id):
		s = db.session.query(Site).filter(Site.id==param_id).first()
		return s.name

	def select_company(param_id):
		cmp = db.session.query(Company).filter(Company.id==(db.session.query(Site).filter(Site.id==param_id).first()).company_id).first()
		return cmp

	myDict = {
		'legend' : gettext("System useres"),
		'menu' : {},
			'title' : 'System useres',
	}
	return render_template("admin/sysuser.html", myDict=myDict, sysusers=sysusers, select_name=select_name, select_company=select_company, roles=roles)

@admin.route("/add_sysuser", methods=['GET', 'POST'])
@login_required
def add_sysuser():
	roles = []
	for i in range(len(current_user.roles)):
		roles.append(current_user.roles[i].name)
	if 'super_admin' not in roles:
		flash('Vous n\'avez pas l\'accès', 'danger')
		return redirect(url_for('admin.index'))

	form = Add_Sysuser_Form()
	form.company.choices=[(str(cmp.id), cmp.name) for cmp in db.session.query(Company).all()]
	form.site.choices=[(str(s.id), s.name) for s in db.session.query(Site).all()]	

	if form.validate_on_submit():
		sysuser = SysUser(firstName=form.firstName.data, lastName=form.lastName.data, email=form.email.data, site_id=form.site.data)
		db.session.add(sysuser)
		db.session.flush()
		db.session.refresh(sysuser)
		sys_id = sysuser.id
		for r in form.role.data:
			userRole = AssignUserRole.insert().values(role_id= r, user_id=sys_id)
			db.session.execute(userRole)
			db.session.commit()
		db.session.commit()
		#send_mail(official.email)
		flash('Utilisateur est ajouté avec succés', 'success')
		return redirect(url_for('admin.sysuser'))

	myDict = {
		'form' : form,
		'legend' : gettext("Ajouter un Utilisateur"),
		'menu' : {},
		'title' : 'Ajouter un Utilisateur',
		}
	return render_template('admin/add_sysuser.html', myDict=myDict, roles=roles)


@admin.route("/sysuser/<int:sysuser_id>/update", methods=['GET', 'POST'])
@login_required
def update_sysuser(sysuser_id):
	roles = []
	for i in range(len(current_user.roles)):
		roles.append(current_user.roles[i].name)
	if 'super_admin' not in roles:
		flash('Vous n\'avez pas l\'accès', 'danger')
		return redirect(url_for('admin.index'))

	ssu = db.session.query(SysUser).filter(SysUser.id==sysuser_id).first()
	cmp = db.session.query(Company).filter(Company.id==db.session.query(Site).filter(Site.id==db.session.query(SysUser).filter(SysUser.id==sysuser_id).first().site_id).first().company_id).first()
	r = Role.query.filter(Role.users.any(id=sysuser_id)).all()

	roles_user = []
	for x in range(len(r)):
		roles_user.append(r[x].id)

	form = Update_Sysuser_Form(company=cmp.id, site=ssu.site_id, role=roles_user)

	if form.validate_on_submit():
		ssu.firstName=form.firstName.data
		ssu.lastName=form.lastName.data
		ssu.email=form.email.data
		ssu.site_id=form.site.data
		ssu.roles = []
		db.session.commit()
		for r in form.role.data:
			userRole = AssignUserRole.insert().values(role_id= r, user_id=ssu.id)
			db.session.execute(userRole)
			db.session.commit()
		flash('Données utilisateurs sont bien mises à jour', 'success')
		return redirect(url_for('admin.sysuser', sysuser_id=ssu.id))
	elif request.method == 'GET':
		form.uniqueIdentifier.data=ssu.id
		form.uniqueIdentifier.render_kw = {'disabled': 'disabled'}
		form.firstName.data=ssu.firstName
		form.lastName.data=ssu.lastName		
		form.email.data=ssu.email

	myDict = {
		'form' : form,
		'legend' : gettext("Mettre à jour l'utilisateur"),
		'menu' : {},
		'title' : 'Mettre à jour l\'utilisateur',
	}
	return render_template("admin/update_sysuser.html", myDict=myDict, roles=roles)

@admin.route("/sysuser/<int:sysuser_id>/delete", methods=['POST'])
@login_required
def delete_sysuser(sysuser_id):
	ssu = db.session.query(SysUser).filter(SysUser.id==sysuser_id).first()
	ssu.roles = []
	db.session.commit()
	db.session.delete(ssu)
	db.session.commit()
	flash('Utilisateur supprimé', 'success')
	return redirect(url_for('admin.sysuser'))

@admin.route("/suppuser", methods=['GET', 'POST'])
@login_required
def suppuser():
	roles = []
	for i in range(len(current_user.roles)):
		roles.append(current_user.roles[i].name)
	if 'super_admin' not in roles:
		flash('Vous n\'avez pas l\'accès', 'danger')
		return redirect(url_for('admin.index'))

	suppusers = db.session.query(SuppUser).all()

	def select_name(param_id):
		s = db.session.query(Supplier).filter(Supplier.id==param_id).first()
		return s.name

	myDict = {
		'legend' : gettext("Les utilisateurs du fournisseur"),
		'menu' : {},
		'title' : 'Les utilisateurs du fournisseur',
	}
	return render_template("admin/suppuser.html", myDict=myDict, suppusers=suppusers, select_name=select_name, roles=roles)

@admin.route("/add_suppuser", methods=['GET', 'POST'])
@login_required
def add_suppuser():
	roles = []
	for i in range(len(current_user.roles)):
		roles.append(current_user.roles[i].name)
	if 'super_admin' not in roles:
		flash('Vous n\'avez pas l\'accès', 'danger')
		return redirect(url_for('admin.index'))

	form = Add_Suppuser_Form()
	form.supplier.choices=[(str(s.id), s.name) for s in db.session.query(Supplier).all()]

	if form.validate_on_submit():
		suppuser = SuppUser(firstName=form.firstName.data, lastName=form.lastName.data, email=form.email.data, supplier_id=form.supplier.data)
		db.session.add(suppuser)
		db.session.flush()
		db.session.refresh(suppuser)
		sup_id = suppuser.id
		for r in form.role.data:
			userRole = AssignUserRole.insert().values(role_id= r, user_id=sup_id)
			db.session.execute(userRole)
			db.session.commit()
		db.session.commit()
		#send_mail(official.email)
		flash('Utilisateur est ajouté avec succés', 'success')
		return redirect(url_for('admin.suppuser'))

	myDict = {
		'form' : form,
		'legend' : gettext("Ajouter un Utilisateur"),
		'menu' : {},
		'title' : 'Ajouter un Utilisateur',
		}
	return render_template('admin/add_suppuser.html', myDict=myDict, roles=roles)


@admin.route("/suppuser/<int:suppuser_id>/update", methods=['GET', 'POST'])
@login_required
def update_suppuser(suppuser_id):
	roles = []
	for i in range(len(current_user.roles)):
		roles.append(current_user.roles[i].name)
	if 'super_admin' not in roles:
		flash('Vous n\'avez pas l\'accès', 'danger')
		return redirect(url_for('admin.index'))

	ssu = db.session.query(SuppUser).filter(SuppUser.id==suppuser_id).first()
	r = Role.query.filter(Role.users.any(id=suppuser_id)).all()

	roles_user = []
	for x in range(len(r)):
		roles_user.append(r[x].id)
	
	form = Update_Suppuser_Form(role=roles_user)

	if form.validate_on_submit():
		ssu.firstName=form.firstName.data
		ssu.lastName=form.lastName.data
		ssu.email=form.email.data
		ssu.roles = []
		db.session.commit()
		for r in form.role.data:
			userRole = AssignUserRole.insert().values(role_id= r, user_id=ssu.id)
			db.session.execute(userRole)
			db.session.commit()
		flash('Données utilisateurs sont bien mises à jour', 'success')
		return redirect(url_for('admin.suppuser', suppuser_id=ssu.id))
	elif request.method == 'GET':
		form.uniqueIdentifier.data=ssu.id
		form.uniqueIdentifier.render_kw = {'disabled': 'disabled'}
		form.firstName.data=ssu.firstName
		form.lastName.data=ssu.lastName
		form.email.data=ssu.email

	myDict = {
		'form' : form,
		'legend' : gettext("Mettre à jour l'utilisateur"),
		'menu' : {},
		'title' : 'Mettre à jour l\'utilisateur',
	}
	return render_template("admin/update_suppuser.html", myDict=myDict, roles=roles)

@admin.route("/suppuser/<int:suppuser_id>/delete", methods=['POST'])
@login_required
def delete_suppuser(suppuser_id):
	ssu = db.session.query(SuppUser).filter(SuppUser.id==suppuser_id).first()
	ssu.roles = []
	db.session.commit()
	db.session.delete(ssu)
	db.session.commit()
	flash('Utilisateur supprimé', 'success')
	return redirect(url_for('admin.suppuser'))

@admin.route("/company", methods=['GET', 'POST'])
@login_required
def company():
	roles = []
	for i in range(len(current_user.roles)):
		roles.append(current_user.roles[i].name)
	if 'super_admin' not in roles:
		flash('Vous n\'avez pas l\'accès', 'danger')
		return redirect(url_for('admin.index'))

	companies = db.session.query(Company).all()

	myDict = {
        'legend' : gettext("Companies"),
        'menu' : {},
		'title' : 'Companies',
    }
	return render_template("admin/company.html", myDict=myDict, companies=companies, roles=roles)

@admin.route("/add_company", methods=['GET', 'POST'])
@login_required
def add_company():
    roles = []
    for i in range(len(current_user.roles)):
        roles.append(current_user.roles[i].name)
    if 'super_admin' not in roles:
        flash('Vous n\'avez pas l\'accès', 'danger')
        return redirect(url_for('admin.index'))

    form = Add_Company_Form()

    if form.validate_on_submit():
        company = Company(name=form.name.data, taxRegisration=form.taxRegisration.data, phone=form.phone.data, fax=form.fax.data, adresse=form.adresse.data, city=form.city.data, country=form.country.data)
        db.session.add(company)
        db.session.commit()
        flash('Entité juridique est créée avec succés', 'success')
        return redirect(url_for('admin.company'))

    myDict = {
        'form' : form,
        'legend' : gettext("Ajouter une Entité juridique"),
        'menu' : {},
        'title' : 'Ajouter une Entité juridique',
        }
    return render_template('admin/add_company.html', myDict=myDict, roles=roles)

@admin.route("/company/<int:company_id>/update", methods=['GET', 'POST'])
@login_required
def update_company(company_id):
	roles = []
	for i in range(len(current_user.roles)):
		roles.append(current_user.roles[i].name)
	if 'super_admin' not in roles:
		flash('Vous n\'avez pas l\'accès', 'danger')
		return redirect(url_for('admin.index'))

	sites = db.session.query(Site).filter(Site.company_id==company_id).all()
	company = db.session.query(Company).filter(Company.id==company_id).first()

	
	form = Update_Company_Form()
	f2 = Update_Logo_Form()

	if form.validate_on_submit():
		company.name=form.name.data
		company.phone=form.phone.data
		company.fax=form.fax.data
		company.adresse=form.adresse.data
		company.city=form.city.data
		company.country=form.country.data
		db.session.commit()
		flash('Données sont bien mises à jour', 'success')
		return redirect(url_for('admin.company'))
	elif request.method == 'GET':
		form.uniqueIdentifier.data=company.id
		form.uniqueIdentifier.render_kw = {'disabled': 'disabled'}
		form.name.data=company.name
		form.taxRegisration.data=company.taxRegisration
		form.taxRegisration.render_kw = {'disabled': 'disabled'}
		form.phone.data=company.phone
		form.fax.data=company.fax
		form.adresse.data=company.adresse
		form.city.data=company.city
		form.country.data=company.country

	myDict = {
		'form' : form,
		'f2' : f2,
		'legend' : gettext("Mettre à jour l'entité juridique"),
		'menu' : {},
		'title' : 'Mettre à jour l\'entité juridique',
	}
	return render_template("admin/update_company.html", myDict=myDict, company=company, sites=sites, company_id=company_id, roles=roles)

@admin.route("/company/<int:company_id>/update/update_logo", methods=['GET', 'POST'])
@login_required
def update_logo_company(company_id):
	f2 = Update_Logo_Form()
	company = db.session.query(Company).filter(Company.id==company_id).first()

	if f2.validate_on_submit():
		if company.logo:
			file = COMP_LOGO_PATH + "/" + company.logo
			os.remove(file)
		f = request.files['file']
		filename = secure_filename(f.filename)
		name = str(company_id)+"_"+filename	
		company.logo= name	
		f.save(os.path.join(COMP_LOGO_PATH, name))
		db.session.commit()
		return redirect(url_for('admin.update_company', company_id=company_id))
	else:
		flash('vérifiez le type de l\'image', 'danger')
		return redirect(url_for('admin.update_company', company_id=company_id))

@admin.route("/company/<int:company_id>/delete", methods=['POST'])
@login_required
def delete_company(company_id):
	roles = []
	for i in range(len(current_user.roles)):
		roles.append(current_user.roles[i].name)
	if 'super_admin' not in roles:
		flash('Vous n\'avez pas l\'accès', 'danger')
		return redirect(url_for('admin.index'))

	cmp = db.session.query(Company).filter(Company.id==company_id).first()
	db.session.delete(cmp)
	db.session.commit()
	flash('Entité juridique supprimée', 'success')
	return redirect(url_for('admin.company'))

@admin.route("/company/<int:company_id>/update/add_site", methods=['GET', 'POST'])
@login_required
def add_site(company_id):
    roles = []
    for i in range(len(current_user.roles)):
        roles.append(current_user.roles[i].name)
    if 'super_admin' not in roles:
        flash('Vous n\'avez pas l\'accès', 'danger')
        return redirect(url_for('admin.index'))

    form = Add_Site_Form()

    if form.validate_on_submit():
        site = Site(name=form.name.data, phone=form.phone.data, fax=form.fax.data, adresse=form.adresse.data, city=form.city.data, country=form.country.data, company_id=company_id)
        db.session.add(site)
        db.session.commit()
        flash('Site est créé avec succés', 'success')
        return redirect(url_for('admin.update_company', company_id=company_id))

    myDict = {
        'form' : form,
        'legend' : gettext("Ajouter un site"),
        'menu' : {},
        'title' : 'Ajouter un site',
        }
    return render_template('admin/add_site.html', myDict=myDict, company_id=company_id, roles=roles)

@admin.route("/company/<int:company_id>/update/<int:site_id>/update", methods=['GET', 'POST'])
@login_required
def update_site(company_id, site_id):
	roles = []
	for i in range(len(current_user.roles)):
		roles.append(current_user.roles[i].name)
	if 'super_admin' not in roles:
		flash('Vous n\'avez pas l\'accès', 'danger')
		return redirect(url_for('admin.index'))

	s = db.session.query(Site).filter(Site.id==site_id).first()
	
	form = Update_Site_Form()	

	if form.validate_on_submit():
		s.name=form.name.data
		s.phone=form.phone.data
		s.fax=form.fax.data
		s.adresse=form.adresse.data
		s.city=form.city.data
		s.country=form.country.data
		db.session.commit()
		flash('Données sont bien mises à jour', 'success')
		return redirect(url_for('admin.update_company', company_id=company_id))
	elif request.method == 'GET':
		form.uniqueIdentifier.data=s.id
		form.uniqueIdentifier.render_kw = {'disabled': 'disabled'}
		form.name.data=s.name
		form.phone.data=s.phone
		form.fax.data=s.fax
		form.adresse.data=s.adresse
		form.city.data=s.city
		form.country.data=s.country
	
	myDict = {
        'form' : form,
        'legend' : gettext("Modifier un site"),
        'menu' : {},
        'title' : 'Modifeir un site',
        }

	return render_template('admin/update_site.html', myDict=myDict, company_id=company_id, site_id=site_id, roles=roles)

@admin.route("/company/<int:company_id>/update/<int:site_id>/delete", methods=['POST'])
@login_required
def delete_site(company_id, site_id):
	roles = []
	for i in range(len(current_user.roles)):
		roles.append(current_user.roles[i].name)
	if 'super_admin' not in roles:
		flash('Vous n\'avez pas l\'accès', 'danger')
		return redirect(url_for('admin.index'))

	s = db.session.query(Site).filter(Site.id==site_id).first()
	db.session.delete(s)
	db.session.commit()
	flash('Site supprimé', 'success')
	return redirect(url_for('admin.update_company', company_id=company_id))

@admin.route("/setting", methods=['GET', 'POST'])
@login_required
def setting():
	roles = []
	for i in range(len(current_user.roles)):
		roles.append(current_user.roles[i].name)
	if 'super_admin' not in roles:
		flash('Vous n\'avez pas l\'accès', 'danger')
		return redirect(url_for('admin.index'))

	myDict = {
		'legend' : gettext("Importer des données"),
		'menu' : {},
		'title' : 'Importer des données',
	}
	return render_template("admin/setting.html", myDict=myDict, roles=roles)

@admin.route("/import_data", methods=['GET', 'POST'])
@login_required
def import_data():
	roles = []
	for i in range(len(current_user.roles)):
		roles.append(current_user.roles[i].name)
	if 'super_admin' not in roles:
		flash('Vous n\'avez pas l\'accès', 'danger')
		return redirect(url_for('admin.index'))

	myDict = {
		'legend' : gettext("Importer des données"),
		'menu' : {},
		'title' : 'Importer des données',
	}
	return render_template("admin/import_data.html", myDict=myDict, roles=roles)

@admin.route("/project", methods=['GET', 'POST'])
@login_required
def project():
	roles = []
	for i in range(len(current_user.roles)):
		roles.append(current_user.roles[i].name)
	if 'super_admin' not in roles:
		flash('Vous n\'avez pas l\'accès', 'danger')
		return redirect(url_for('admin.index'))

	form = Add_Excel_Form()
	projects = db.session.query(Project).all()

	myDict = {
		'form' : form,
        'legend' : gettext("Project"),
        'menu' : {},
		'title' : 'Project',
    }
	return render_template("admin/project.html", myDict=myDict, projects=projects, roles=roles)

@admin.route("/add_project", methods=['GET', 'POST'])
@login_required
def add_project():
	roles = []
	for i in range(len(current_user.roles)):
		roles.append(current_user.roles[i].name)
	if 'super_admin' not in roles:
		flash('Vous n\'avez pas l\'accès', 'danger')
		return redirect(url_for('admin.index'))

	form = Add_Excel_Form()

	if form.validate_on_submit():
		f = request.files['file']
		filename = secure_filename(f.filename)
		f.save(filename)
		document = xlrd.open_workbook(filename)
		feuille = document.sheet_by_index(0)
		rows = feuille.nrows
		for i in range(1, rows):
			code = feuille.cell_value(rowx=i, colx=0)
			name = feuille.cell_value(rowx=i, colx=1)
			pro = db.session.query(Project).filter(Project.code==code).first()
			if not pro:
				project = Project(code=code, name=name)
				db.session.add(project)
				db.session.commit()					
		os.remove(filename)
		return redirect(url_for('admin.project'))

@admin.route("/client", methods=['GET', 'POST'])
@login_required
def client():
	roles = []
	for i in range(len(current_user.roles)):
		roles.append(current_user.roles[i].name)
	if 'super_admin' not in roles:
		flash('Vous n\'avez pas l\'accès', 'danger')
		return redirect(url_for('admin.index'))

	form = Add_Excel_Form()
	clients = db.session.query(Client).all()

	myDict = {
		'form' : form,
        'legend' : gettext("Client"),
        'menu' : {},
		'title' : 'Client',
    }
	return render_template("admin/client.html", myDict=myDict, clients=clients, roles=roles)

@admin.route("/add_client", methods=['GET', 'POST'])
@login_required
def add_client():
	roles = []
	for i in range(len(current_user.roles)):
		roles.append(current_user.roles[i].name)
	if 'super_admin' not in roles:
		flash('Vous n\'avez pas l\'accès', 'danger')
		return redirect(url_for('admin.index'))

	form = Add_Excel_Form()

	if form.validate_on_submit():
		f = request.files['file']
		filename = secure_filename(f.filename)
		f.save(filename)
		document = xlrd.open_workbook(filename)
		feuille = document.sheet_by_index(0)
		rows = feuille.nrows
		for i in range(1, rows):
			code = feuille.cell_value(rowx=i, colx=0)
			name = feuille.cell_value(rowx=i, colx=1)
			adresse = feuille.cell_value(rowx=i, colx=2)
			clt = db.session.query(Client).filter(Client.code==code).first()
			if not clt:
				client = Client(code=code, name=name, adresse=adresse)
				db.session.add(client)
				db.session.commit()					
		os.remove(filename)
		return redirect(url_for('admin.client'))

@admin.route("/article", methods=['GET', 'POST'])
@login_required
def article():
	roles = []
	for i in range(len(current_user.roles)):
		roles.append(current_user.roles[i].name)
	if 'super_admin' not in roles:
		flash('Vous n\'avez pas l\'accès', 'danger')
		return redirect(url_for('admin.index'))

	form = Add_Excel_Form()
	articles = db.session.query(Article).all()

	myDict = {
		'form' : form,
        'legend' : gettext("Article"),
        'menu' : {},
		'title' : 'Article',
    }
	return render_template("admin/article.html", myDict=myDict, articles=articles, roles=roles)

@admin.route("/add_article", methods=['GET', 'POST'])
@login_required
def add_article():
	roles = []
	for i in range(len(current_user.roles)):
		roles.append(current_user.roles[i].name)
	if 'super_admin' not in roles:
		flash('Vous n\'avez pas l\'accès', 'danger')
		return redirect(url_for('admin.index'))

	form = Add_Excel_Form()

	if form.validate_on_submit():
		f = request.files['file']
		filename = secure_filename(f.filename)
		f.save(filename)
		document = xlrd.open_workbook(filename)
		feuille = document.sheet_by_index(0)
		rows = feuille.nrows
		for i in range(1, rows):
			internaltCode = feuille.cell_value(rowx=i, colx=0)
			externaltCode = feuille.cell_value(rowx=i, colx=1)
			designation = feuille.cell_value(rowx=i, colx=2)
			art = db.session.query(Article).filter(Article.internaltCode==internaltCode).first()
			if not art:
				article = Article(internaltCode=internaltCode, externaltCode=externaltCode, designation=designation)
				db.session.add(article)
				db.session.commit()					
		os.remove(filename)
		return redirect(url_for('admin.article'))

@admin.route("/typeCertificate", methods=['GET', 'POST'])
@login_required
def typeCertificate():
    roles = []
    for i in range(len(current_user.roles)):
        roles.append(current_user.roles[i].name)
    if 'super_admin' not in roles:
        flash('Vous n\'avez pas l\'accès', 'danger')
        return redirect(url_for('admin.index'))

    typeCertificate = db.session.query(CertificationType).all()
    
    myDict = {
        'legend': gettext("typeCertificat"),
        'menu': {},
        'title': 'typeCertificat',
    }
    return render_template("admin/typeCertificate.html", myDict=myDict, typeCertificates=typeCertificate, roles=roles)

@admin.route("/add_typeCertificate", methods=['GET', 'POST'])
@login_required
def add_typeCertificate():
    roles = []
    for i in range(len(current_user.roles)):
        roles.append(current_user.roles[i].name)
    if 'super_admin' not in roles:
        flash('Vous n\'avez pas l\'accès', 'danger')
        return redirect(url_for('admin.index'))

    form = Add_typeCertificate_Form()
    
    if form.validate_on_submit():
     name= form.name.data
     certifT = db.session.query(CertificationType).filter(CertificationType.name == name).first()

     if not certifT:
          typeCertificate = CertificationType(name=form.name.data, description=form.description.data)
          db.session.add(typeCertificate)
          db.session.commit()
          flash('Type certificat est créé avec succés', 'success')
          return redirect(url_for('admin.typeCertificate'))
     else: 
          flash('Type certificat existe déja', 'danger')
          return redirect(url_for('admin.add_typeCertificate'))
       
    myDict = {
        'form': form,
        'legend': gettext("Ajouter un type certificat"),
        'menu': {},
        'title': 'Ajouter un type certificat',
    }
   
    return render_template('admin/add_typeCertificate.html', myDict=myDict, roles=roles)

@admin.route("/typeCertificate/<int:typeCertificate_id>/delete", methods=['POST'])
@login_required
def delete_typeCertificate(typeCertificate_id):
    roles = []
    for i in range(len(current_user.roles)):
        roles.append(current_user.roles[i].name)
    if 'super_admin' not in roles:
        flash('Vous n\'avez pas l\'accès', 'danger')
        return redirect(url_for('admin.index'))

    cmp = db.session.query(CertificationType).filter(CertificationType.id == typeCertificate_id).first()
    db.session.delete(cmp)
    db.session.commit()
    flash('typeCertificat supprimée', 'success')
    return redirect(url_for('admin.typeCertificate'))

# VIEW ALL CHARGES
@admin.route("/charges",methods=['GET','POST'])
@login_required
def view_charges():
	roles = []
	for i in range(len(current_user.roles)):
		roles.append(current_user.roles[i].name)
	if 'super_admin' not in roles:
		flash('Vous n\'avez pas l\'accès', 'danger')
		return redirect(url_for('admin.index'))

	charges = db.session.query(CostType).all()
	myDict = {
		'legend' : gettext("Charges"),
		'menu' : {},
		'title' : 'Charges',
	}
	return render_template("admin/charges.html",myDict=myDict, charges=charges, roles=roles)


# ADD NEW CHARGE 
@admin.route("/charges/add",methods=['GET','POST'])
@login_required
def add_charge():
	roles = []
	for i in range(len(current_user.roles)):
		roles.append(current_user.roles[i].name)
	if 'super_admin' not in roles:
		flash('Vous n\'avez pas l\'accès', 'danger')
		return redirect(url_for('admin.index'))

	form = Add_Charge_Form()
	if form.validate_on_submit():
		newCharge = CostType(code=form.code.data,unit=form.unit.data,description=form.description.data)
		db.session.add(newCharge)
		db.session.commit()
		flash('Le frais '+form.code.data+' a été ajouté à la liste globale des frais avec succès!', 'success')
		return redirect(url_for('admin.view_charges'))

	myDict = {
		'form' : form,
        'legend' : gettext("Ajout Frais"),
        'menu' : {},
		'title' : 'Ajout Frais',
    }

	return render_template("admin/add_charge.html",myDict=myDict, roles=roles)

# UPDATE CHARGE 
@admin.route("/charges/<int:charge_id>/update",methods=['GET','POST'])
@login_required
def update_charge(charge_id):
	roles = []
	for i in range(len(current_user.roles)):
		roles.append(current_user.roles[i].name)
	if 'super_admin' not in roles:
		flash('Vous n\'avez pas l\'accès', 'danger')
		return redirect(url_for('admin.index'))

	form = Update_Charge_Form()
	myCharge = db.session.query(CostType).filter(CostType.id==charge_id).first()
	if form.validate_on_submit():
		myCharge.code = form.code.data
		myCharge.unit = form.unit.data 
		myCharge.description = form.description.data
		db.session.commit()
		flash('Le frais '+form.code.data+' a été mis à jour avec succès!', 'success')
		return redirect(url_for('admin.view_charges'))
	elif request.method == 'GET':
		form.code.data = myCharge.code
		form.unit.data = myCharge.unit
		form.description.data = myCharge.description

	myDict = {
		'form' : form,
        'legend' : gettext("Modifier Frais"),
        'menu' : {},
		'title' : 'Modifier Frais',
    }

	return render_template("admin/update_charge.html",myDict=myDict, charge_id=charge_id, roles=roles)

# DELETE CHARGE
@admin.route("/charges/<int:charge_id>/delete",methods=['GET','POST'])
@login_required
def delete_charge(charge_id):
	roles = []
	for i in range(len(current_user.roles)):
		roles.append(current_user.roles[i].name)
	if 'super_admin' not in roles:
		flash('Vous n\'avez pas l\'accès', 'danger')
		return redirect(url_for('admin.index'))

	myCharge = db.session.query(CostType).filter(CostType.id==charge_id).first()
	suppCharges = db.session.query(SuppCosts).filter(SuppCosts.costtype_id==charge_id).all()
	for suppCharge in suppCharges:
		db.session.delete(suppCharge)
	db.session.delete(myCharge)
	db.session.commit()
	flash('Le frais '+ myCharge.code +' a été supprimé de la liste globale des frais!', 'success')
	return redirect(url_for('admin.view_charges'))

@admin.route('/charge/<charge_id>')
def getChargeDetails(charge_id):
	charge = db.session.query(CostType).filter(CostType.id==charge_id).first()
	return jsonify({'id':charge.id,'code':charge.code,'unit':charge.unit,'description':charge.description})
