from flask import render_template, g, url_for, request, flash, Markup, send_file, send_from_directory, redirect, jsonify, abort, Blueprint, request, current_app
from flask_login import login_user, current_user, logout_user, login_required
from dev import db, bcrypt, app
from dev.models import *
from dev.BP_auth.forms import LoginForm
#from dev.BP_auth.utils import save_picture, senEmail, send_mail, send_reset_email
from dev.BP_complaint.forms import *
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadTimeSignature
from flask_babel import Babel, format_date, gettext
from datetime import datetime, timedelta
from sqlalchemy.exc import IntegrityError
from werkzeug.utils import secure_filename
from dev.BP_complaint.utils import *
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


comp = Blueprint('comp', __name__)
s=URLSafeTimedSerializer(app.config['SECRET_KEY'])
COMP_ATT_PATH = 'C:/Users/boura/Desktop/testflask/SRM-Project/SRM-MAIN/app/dev/static/img/ComplaintAttachement'
COMP_ATT_ALLOWED_EXT={'jpeg', 'jpg', 'png', 'gif'}
REP8D_ATT_PATH='C:/Users/boura/Desktop/testflask/SRM-Project/SRM-MAIN/app/dev/static/img/Attachement8D'
REP8D_ATT_ALLOWED_EXT={'jpeg', 'jpg', 'png', 'gif'}

@comp.route("/complaint", methods=['GET', 'POST'])
@login_required
def complaint():
	roles = []
	for i in range(len(current_user.roles)):
		roles.append(current_user.roles[i].name)
	if 'super_admin' not in roles and 'complaint_level1' not in roles and 'complaint_level2' not in roles:
		flash('Vous n\'avez pas l\'accès', 'danger')
		return redirect(url_for('admin.index'))

	complaints = db.session.query(ComplaintTable).all()

	def select_supp(param_id):
		supp = db.session.query(Supplier).filter(Supplier.id==param_id).first()
		return supp.name
	
	def select_user(param_id):
		u = db.session.query(User).filter(User.id==param_id).first()
		return u

	myDict = {
        'legend' : gettext("Complaint"),
        'menu' : {},
		'title' : 'Complaint',
    }
	return render_template("complaint/complaint.html", myDict=myDict, complaints=complaints, select_supp=select_supp, select_user=select_user, roles=roles)

@comp.route("/add_complaint", methods=['GET', 'POST'])
@login_required
def add_complaint():
	roles = []
	for i in range(len(current_user.roles)):
		roles.append(current_user.roles[i].name)
	if current_user.type!='sysuser' or 'complaint_level2' not in roles:
		flash('Vous n\'avez pas l\'accès', 'danger')
		return redirect(url_for('admin.index'))

	form = Add_Complaint_Form()
	date = datetime.now()	

	if form.validate_on_submit():

		complaint = ComplaintTable(date=date, deliveryForm=form.deliveryForm.data, suspectQuantity=form.suspectQuantity.data, detectionZone=form.detectionZone.data, problemDescription=form.problemDescription.data, verificationMethod=form.verificationMethod.data, status="créée", sysuser_id=current_user.id, supplier_id=form.supplier.data, article_id=form.article.data, client_id=form.client.data, project_id=form.project.data)
		db.session.add(complaint)
		db.session.flush()
		db.session.refresh(complaint)
		complaint_id = complaint.id
		complaint.number = "REC-" + str(complaint_id)
		for f in request.files.getlist("file"):
			att = ComplaintAttachement(complaint_id=complaint_id)
			db.session.add(att)
			db.session.flush()
			db.session.refresh(att)
			att_id = att.id
			filename = secure_filename(f.filename)
			name = str(att_id)+"_"+filename	
			att.name= name	
			f.save(os.path.join(COMP_ATT_PATH, name))
		db.session.commit()
		return redirect(url_for('comp.complaint'))

	myDict = {
		'form' : form,
		'legend' : gettext("Créer une réclamation"),
		'menu' : {},
		'title' : 'Créer une réclamation',
		}
	return render_template('complaint/add_complaint.html', myDict=myDict, roles=roles)

@comp.route("/complaint/<int:complaint_id>/update", methods=['GET', 'POST'])
@login_required
def update_complaint(complaint_id):
	roles = []
	for i in range(len(current_user.roles)):
		roles.append(current_user.roles[i].name)
	if current_user.type!='sysuser' or 'complaint_level2' not in roles:
		flash('Vous n\'avez pas l\'accès', 'danger')
		return redirect(url_for('admin.index'))

	comp = db.session.query(ComplaintTable).filter(ComplaintTable.id==complaint_id).first()
	supp = db.session.query(Supplier).filter(Supplier.id==comp.supplier_id).first()
	
	form = Update_Complaint_Form(supplier=comp.supplier_id, project=comp.project_id, article=comp.article_id, client=comp.client_id)	
	date = datetime.now()

	if form.validate_on_submit():
		comp.supplier_id=form.supplier.data
		comp.deliveryForm=form.deliveryForm.data
		comp.suspectQuantity=form.suspectQuantity.data
		comp.detectionZone=form.detectionZone.data
		comp.problemDescription=form.problemDescription.data
		comp.verificationMethod=form.verificationMethod.data
		comp.project_id=form.project.data
		comp.article_id=form.article.data
		comp.client_id=form.client.data
		comp.submissionDate=date
		comp.status="soumise"
		comp.date3D = date + timedelta(days=supp.jalan3D)
		comp.date5D = date + timedelta(days=supp.jalan5D)
		comp.date8D = date + timedelta(days=supp.jalan8D)
		comp.initialResponseDate = date + timedelta(days=supp.initialResponse)
		comp.finalResponseDate = date + timedelta(days=supp.finalResponse)
		db.session.commit()
		flash('Données sont bien mises à jour', 'success')
		return redirect(url_for('comp.complaint'))
	elif request.method == 'GET':
		form.number.data=comp.number
		form.number.render_kw = {'disabled': 'disabled'}
		form.deliveryForm.data=comp.deliveryForm
		form.suspectQuantity.data=comp.suspectQuantity
		form.detectionZone.data=comp.detectionZone
		form.problemDescription.data=comp.problemDescription
		form.verificationMethod.data=comp.verificationMethod
	
	myDict = {
        'form' : form,
        'legend' : gettext("Modifier un site"),
        'menu' : {},
        'title' : 'Modifeir un site',
        }

	return render_template('complaint/update_complaint.html', myDict=myDict, complaint_id=complaint_id, roles=roles)

@comp.route("/complaint/<int:complaint_id>/consult_complaint", methods=['GET', 'POST'])
@login_required
def consult_complaint(complaint_id):
	roles = []
	for i in range(len(current_user.roles)):
		roles.append(current_user.roles[i].name)
	if 'super_admin' not in roles and 'complaint_level1' not in roles and 'complaint_level2' not in roles:
		flash('Vous n\'avez pas l\'accès', 'danger')
		return redirect(url_for('admin.index'))

	complaint = db.session.query(ComplaintTable).filter(ComplaintTable.id==complaint_id).first()
	attachements = db.session.query(ComplaintAttachement).filter(ComplaintAttachement.complaint_id==complaint_id).all()

	def select_supp(param_id):
		supp = db.session.query(Supplier).filter(Supplier.id==param_id).first()
		return supp
	
	def select_user(param_id):
		u = db.session.query(User).filter(User.id==param_id).first()
		return u

	def select_article(param_id):
		art = db.session.query(Article).filter(Article.id==param_id).first()
		return art
	
	def select_client(param_id):
		clt = db.session.query(Client).filter(Client.id==param_id).first()
		return clt

	myDict = {
        'legend' : gettext("Consult Complaint"),
        'menu' : {},
		'title' : 'Consult Complaint',
    }
	return render_template("complaint/consult_complaint.html", myDict=myDict, complaint=complaint, attachements=attachements, select_supp=select_supp, select_user=select_user, select_article=select_article, select_client=select_client, roles=roles)

@comp.route("/complaint/<int:complaint_id>/add_report8D", methods=['GET', 'POST'])
@login_required
def add_report8D(complaint_id):
	roles = []
	for i in range(len(current_user.roles)):
		roles.append(current_user.roles[i].name)
	if current_user.type!='suppuser' or 'complaint_level2' not in roles:
		flash('Vous n\'avez pas l\'accès', 'danger')
		return redirect(url_for('admin.index'))

	complaint = db.session.query(ComplaintTable).filter(ComplaintTable.id==complaint_id).first()
	date = datetime.now()
	report = Report8D(startDate=date, deadLine=complaint.finalResponseDate)
	db.session.add(report)
	db.session.flush()
	db.session.refresh(report)
	report_id = report.id
	complaint.report8D_id=report_id
	complaint.status="en traitement"
	db.session.commit()	
	return redirect(url_for('comp.list_report8D'))

@comp.route("/list_report8D", methods=['GET', 'POST'])
@login_required
def list_report8D():
	roles = []
	for i in range(len(current_user.roles)):
		roles.append(current_user.roles[i].name)
	if 'super_admin' not in roles and 'complaint_level1' not in roles and 'complaint_level2' not in roles:
		flash('Vous n\'avez pas l\'accès', 'danger')
		return redirect(url_for('admin.index'))

	reports = db.session.query(Report8D).all()

	def select_comp(param_id):
		num = db.session.query(ComplaintTable).filter(ComplaintTable.report8D_id==param_id).first()
		return num
	
	def select_supp(param_id):
		supp = db.session.query(Supplier).filter(Supplier.id==param_id).first()
		return supp

	myDict = {
        'legend' : gettext("Liste des rapports 8D"),
        'menu' : {},
		'title' : 'Liste des rapports 8D',
    }
	return render_template("complaint/list_report8D.html", myDict=myDict, reports=reports, select_comp=select_comp, select_supp=select_supp, roles=roles)

@comp.route("/report8D/<int:report_id>", methods=['GET', 'POST'])
@login_required
def report8D(report_id):
	roles = []
	for i in range(len(current_user.roles)):
		roles.append(current_user.roles[i].name)
	if current_user.type!='suppuser' or 'complaint_level2' not in roles:
		flash('Vous n\'avez pas l\'accès', 'danger')
		return redirect(url_for('admin.index'))

	f1 = Add_Team_Form()
	f2 = Describe_Problem_Form()
	f3 = Add_3DAction_Form()
	f4 = Add_Cause_Form()
	f5 = Add_5DAction_Form()
	f6 = Add_7DAction_Form()
	rapport = db.session.query(Report8D).filter(Report8D.id==report_id).first()
	members = db.session.query(Team).filter(Team.report8D_id==report_id).all()
	attachements = db.session.query(Attachement8D).filter(Attachement8D.report8D_id==report_id).all()
	actions = db.session.query(Action).filter(Action.report8D_id==report_id).all()
	causes = db.session.query(RootCause).filter(RootCause.report8D_id==report_id).all()

	myDict = {
		'f1' : f1,
		'f2' : f2,
		'f3' : f3,
		'f4' : f4,
		'f5' : f5,
		'f6' : f6,
		'legend' : gettext("Liste des rapports 8D"),
		'menu' : {},
		'title' : 'Liste des rapports 8D',
	}
	return render_template("complaint/report8D.html", myDict=myDict, report_id=report_id, rapport=rapport, members=members, attachements=attachements, actions=actions, causes=causes, roles=roles)

@comp.route("/add_team/<int:report_id>", methods=['GET', 'POST'])
@login_required
def add_team(report_id):
	roles = []
	for i in range(len(current_user.roles)):
		roles.append(current_user.roles[i].name)
	if current_user.type!='suppuser' or 'complaint_level2' not in roles:
		flash('Vous n\'avez pas l\'accès', 'danger')
		return redirect(url_for('admin.index'))

	f1 = Add_Team_Form()	

	if f1.validate_on_submit():
		member = Team(firstName=f1.firstName.data, lastName=f1.lastName.data, function=f1.function.data, report8D_id=report_id)
		db.session.add(member)
		db.session.commit()
		return redirect(url_for('comp.report8D', report_id=report_id))

@comp.route("/descripe_prob/<int:report_id>", methods=['GET', 'POST'])
@login_required
def descripe_prob(report_id):
	roles = []
	for i in range(len(current_user.roles)):
		roles.append(current_user.roles[i].name)
	if current_user.type!='suppuser' or 'complaint_level2' not in roles:
		flash('Vous n\'avez pas l\'accès', 'danger')
		return redirect(url_for('admin.index'))

	f2 = Describe_Problem_Form()
	rapport = db.session.query(Report8D).filter(Report8D.id==report_id).first()

	if f2.validate_on_submit():
		rapport.problemDescription=f2.problem.data
		for f in request.files.getlist("file"):
			att = Attachement8D(report8D_id=report_id)
			db.session.add(att)
			db.session.flush()
			db.session.refresh(att)
			att_id = att.id
			filename = secure_filename(f.filename)
			name = str(att_id)+"_"+filename	
			att.name= name	
			f.save(os.path.join(REP8D_ATT_PATH, name))
		db.session.commit()
		return redirect(url_for('comp.report8D', report_id=report_id))
	elif request.method == 'GET':
		f2.problem.data=rapport.problemDescription

@comp.route("/add_action/<int:report_id>/<string:type>", methods=['GET', 'POST'])
@login_required
def add_action(report_id, type):
	roles = []
	for i in range(len(current_user.roles)):
		roles.append(current_user.roles[i].name)
	if current_user.type!='suppuser' or 'complaint_level2' not in roles:
		flash('Vous n\'avez pas l\'accès', 'danger')
		return redirect(url_for('admin.index'))

	f3 = Add_3DAction_Form()
	f4 = Add_Cause_Form()
	f5 = Add_5DAction_Form()
	f6 = Add_7DAction_Form()
	date = datetime.now()

	if f3.validate_on_submit() and type=="3D":
		action = Action(description=f3.action.data, type="3D", owner=f3.owner.data, date=date, report8D_id=report_id)
		db.session.add(action)
		db.session.commit()
		return redirect(url_for('comp.report8D', report_id=report_id))
	
	if f4.validate_on_submit() and type=="4D":
		cause = RootCause(description=f4.cause.data, report8D_id=report_id)
		db.session.add(cause)
		db.session.commit()
		return redirect(url_for('comp.report8D', report_id=report_id))
	
	if f5.validate_on_submit() and type=="5D":
		action = Action(description=f5.action.data, type="5D", owner=f5.owner.data, type5D=f5.type.data, date=date, report8D_id=report_id)
		db.session.add(action)
		db.session.commit()
		return redirect(url_for('comp.report8D', report_id=report_id))
	
	if f6.validate_on_submit() and type=="7D":
		action = Action(description=f6.action.data, type="7D", owner=f6.owner.data, date=date, report8D_id=report_id)
		db.session.add(action)
		db.session.commit()
		return redirect(url_for('comp.report8D', report_id=report_id))

@comp.route("/done_action/<int:report_id>/<int:action_id>", methods=['GET', 'POST'])
@login_required
def done_action(report_id, action_id):
	roles = []
	for i in range(len(current_user.roles)):
		roles.append(current_user.roles[i].name)
	if current_user.type!='sysuser' or 'complaint_level2' not in roles:
		flash('Vous n\'avez pas l\'accès', 'danger')
		return redirect(url_for('admin.index'))

	action = db.session.query(Action).filter(Action.id==action_id).first()

	action.done=True
	action.verifiedDate=datetime.now()
	action.verifiedBy=current_user.id
	db.session.commit()
	return redirect(url_for('comp.consult_report', report_id=report_id))

@comp.route("/consult_report/<int:report_id>", methods=['GET', 'POST'])
@login_required
def consult_report(report_id):
	roles = []
	for i in range(len(current_user.roles)):
		roles.append(current_user.roles[i].name)
	if 'super_admin' not in roles and 'complaint_level1' not in roles and 'complaint_level2' not in roles:
		flash('Vous n\'avez pas l\'accès', 'danger')
		return redirect(url_for('admin.index'))

	rapport = db.session.query(Report8D).filter(Report8D.id==report_id).first()
	complaint = db.session.query(ComplaintTable).filter(ComplaintTable.report8D_id==report_id).first()
	members = db.session.query(Team).filter(Team.report8D_id==report_id).all()
	attachements = db.session.query(Attachement8D).filter(Attachement8D.report8D_id==report_id).all()
	actions = db.session.query(Action).filter(Action.report8D_id==report_id).all()
	causes = db.session.query(RootCause).filter(RootCause.report8D_id==report_id).all()

	def select_supp(param_id):
		supp = db.session.query(Supplier).filter(Supplier.id==param_id).first()
		return supp
	
	def select_user(param_id):
		u = db.session.query(User).filter(User.id==param_id).first()
		return u
	
	def select_site(param_id):
		s = db.session.query(Site).filter(Site.id==param_id).first()
		return s
	
	def select_company(param_id):
		s = db.session.query(Company).filter(Company.id==param_id).first()
		return s

	myDict = {
        'legend' : gettext("Consult Report"),
        'menu' : {},
		'title' : 'Consult Report',
    }
	return render_template("complaint/consult_report.html", myDict=myDict, rapport=rapport, complaint=complaint, members=members, attachements=attachements, actions=actions, causes=causes, select_supp=select_supp, select_user=select_user, select_site=select_site, select_company=select_company, roles=roles)

@comp.route("/close_complaint/<int:report_id>", methods=['GET', 'POST'])
@login_required
def close_complaint(report_id):
	roles = []
	for i in range(len(current_user.roles)):
		roles.append(current_user.roles[i].name)
	if current_user.type!='suppuser' or 'complaint_level2' not in roles:
		flash('Vous n\'avez pas l\'accès', 'danger')
		return redirect(url_for('admin.index'))

	rapport = db.session.query(Report8D).filter(Report8D.id==report_id).first()
	complaint = db.session.query(ComplaintTable).filter(ComplaintTable.report8D_id==report_id).first()

	complaint.status="closed"
	rapport.closed=True
	rapport.closeDate=datetime.now()
	db.session.commit()
	return redirect(url_for('comp.list_report8D'))

@comp.route("/generate_report/<int:report_id>/<string:stat>", methods=['GET', 'POST'])
@login_required
def generate_report(report_id, stat):
	roles = []
	for i in range(len(current_user.roles)):
		roles.append(current_user.roles[i].name)
	if current_user.type!='suppuser' or 'complaint_level2' not in roles:
		flash('Vous n\'avez pas l\'accès', 'danger')
		return redirect(url_for('admin.index'))

	complaint = db.session.query(ComplaintTable).filter(ComplaintTable.report8D_id==report_id).first()

	if stat=="3D":
		complaint.status="3D"
	if stat=="5D":
		complaint.status="5D"
	if stat=="8D":
		complaint.status="8D"

	db.session.commit()
	return redirect(url_for('comp.consult_report', report_id=report_id))