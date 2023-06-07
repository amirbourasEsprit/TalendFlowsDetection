from flask import render_template, g, url_for, request, flash, Markup, send_file, send_from_directory, redirect, jsonify, abort, Blueprint, request, current_app
from flask_login import login_user, current_user, logout_user, login_required
from dev import db, bcrypt, app
from dev.models import *
from dev.BP_auth.forms import LoginForm
#from dev.BP_auth.utils import save_picture, senEmail, send_mail, send_reset_email
from dev.BP_cost.forms import *
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadTimeSignature
from flask_babel import Babel, format_date, gettext
from datetime import datetime, timedelta
from sqlalchemy.exc import IntegrityError
from werkzeug.utils import secure_filename
from dev.BP_cost.utils import *
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


cost = Blueprint('cost', __name__)
s=URLSafeTimedSerializer(app.config['SECRET_KEY'])

@cost.route('/charge/<charge_id>')
def getChargeDetails(charge_id):
	charge = db.session.query(CostType).filter(CostType.id==charge_id).first()
	return jsonify({'id':charge.id,'code':charge.code,'unit':charge.unit,'description':charge.description})


@cost.route("/supplier_declarations",methods=['GET','POST'])
@login_required
def view_supplier_declarations():
	# is User a supplier user? 
	if current_user.type == "suppuser":
		roles = []
		for i in range(len(current_user.roles)):
			roles.append(current_user.roles[i].name)
		if 'cost_level1' not in roles and 'cost_level2' not in roles:
			flash('Vous n\'avez pas l\'accès', 'danger')
			return redirect(url_for('admin.index'))
		# get the supplier he represents
		userSupplier = db.session.query(SuppUser).filter_by(id=current_user.id).first()
		currentSupplier = db.session.query(Supplier).filter_by(id=userSupplier.supplier_id).first()
		# get supplier declarations
		declarations = db.session.query(CostDeclarationTable,ComplaintTable,Supplier).join(CostDeclarationTable,ComplaintTable.costtable_id==CostDeclarationTable.id).filter(ComplaintTable.supplier_id == Supplier.id).filter(Supplier.id == currentSupplier.id).all()	
		myDict = {
		'legend' : gettext("View Supplier Declarations"),
		'menu' : {},
		'title' : 'View Supplier Declarations',
		}
		return render_template("cost/suppdeclarations.html",myDict=myDict,declarations=declarations, roles=roles)
		#return str(currentSupplier.name)
	else: 
		return redirect(url_for('cost.view_declarations'))


def supplierHasAccessToDeclaration(declaration_id):
	declarationExists = db.session.query(CostDeclarationTable).filter_by(id=declaration_id).first()
	if declarationExists:
		loggedUser = current_user.id
		userSupplier = db.session.query(SuppUser).filter_by(id=loggedUser).first()
		linkedComplaint = db.session.query(ComplaintTable).filter_by(costtable_id=declaration_id).first()
		if linkedComplaint:
			return userSupplier.supplier_id == linkedComplaint.supplier_id
		else:
			return False
	else:
		return False


# SUPPLIER VIEW ASSIGNED DECLARATION
@cost.route("/supplier_declarations/<int:declaration_id>/<string:action>",methods=['GET','POST'])
@login_required
def view_supplier_declaration(declaration_id,action):
	if current_user.type == "suppuser":
		roles = []
		for i in range(len(current_user.roles)):
			roles.append(current_user.roles[i].name)
		if  'cost_level1' not in roles and 'cost_level2' not in roles:
			flash('Vous n\'avez pas l\'accès', 'danger')
			return redirect(url_for('admin.index'))
		declarationExists = db.session.query(CostDeclarationTable).filter_by(id=declaration_id).first()
		if declarationExists:
			if supplierHasAccessToDeclaration(declaration_id):
				currentComplaint = db.session.query(ComplaintTable).filter(ComplaintTable.costtable_id==declaration_id).first()
				currentSupplier = db.session.query(Supplier).filter(Supplier.id == currentComplaint.supplier_id).first()	
				currentCostLines = db.session.query(CostType,CostDeclarationLine).join(CostDeclarationLine).filter(CostDeclarationLine.costtable_id==declaration_id).all()
				myDict = {
					'legend' : gettext("View Supplier Declaration"),
					'menu' : {},
					'title' : 'View Supplier Declaration',
				}
				return render_template("cost/view_suppdeclaration.html",myDict=myDict,complaint_id=currentComplaint.id, complaint_number=currentComplaint.number, declaration=declarationExists,costs=currentCostLines,supplier=currentSupplier,action=action, roles=roles)
			else:
				flash("Cette déclaration de coûts n'existe pas!",'danger')
				return redirect(url_for('cost.view_supplier_declarations'))
		else:
			flash("Cette déclaration de coûts n'existe pas!",'danger')
			return redirect(url_for('cost.view_supplier_declarations'))
	else: 
		return redirect(url_for('cost.view_declaration',declaration_id=declaration_id))


#  SUPPLIER - CHANGE DECLARATION STATUS 
@cost.route("/supplier_declarations/<int:declaration_id>/update_status/<string:action>",methods=['GET','POST'])
@login_required
def update_suppdeclaration_status(declaration_id,action):
	declaration = db.session.query(CostDeclarationTable).filter_by(id=declaration_id).first()
	if declaration and supplierHasAccessToDeclaration(declaration_id):
		if declaration.status == "Soumise" and action == "Valider":
			declaration.status =  "Validée"
			message = "Vous avez validé la déclaration ("+str(declaration.number)+")!"
		elif declaration.status == "Soumise" and action == "Rejeter":
			comment = request.form.get("comment")
			declaration.comment = comment
			declaration.status = "Rejetée"
			message = "Vous avez rejetté la déclaration ("+str(declaration.number)+")!"
		db.session.commit()
		flash(message,'success')
		return redirect(url_for('cost.view_supplier_declaration',declaration_id=declaration_id,action='update'))
	else:
		flash("Cette déclaration de coûts n'existe pas!",'danger')
		return redirect(url_for('cost.view_supplier_declarations'))


# VIEW ALL DECLARATIONS 
@cost.route("/declarations",methods=['GET','POST'])
@login_required
def view_declarations():	
	if current_user.type == "sysuser":
		roles = []
		for i in range(len(current_user.roles)):
			roles.append(current_user.roles[i].name)
		if 'super_admin' not in roles and 'cost_level1' not in roles and 'cost_level2' not in roles:
			flash('Vous n\'avez pas l\'accès', 'danger')
			return redirect(url_for('admin.index'))
		declarations = db.session.query(CostDeclarationTable,ComplaintTable,Supplier).join(CostDeclarationTable,ComplaintTable.costtable_id==CostDeclarationTable.id).filter(ComplaintTable.supplier_id == Supplier.id).all()	
		myDict = {
			'legend' : gettext("View Declarations"),
			'menu' : {},
			'title' : 'View Declarations',
		}
		return render_template("cost/declarations.html",myDict=myDict,declarations=declarations, roles=roles)
	else:
		return redirect(url_for('cost.view_supplier_declarations'))

# VIEW DECLARATION 
@cost.route("/declarations/<int:declaration_id>/view",methods=['GET','POST'])
@login_required
def view_declaration(declaration_id):
	if current_user.type == "sysuser":
		roles = []
		for i in range(len(current_user.roles)):
			roles.append(current_user.roles[i].name)
		if  'cost_level1' not in roles and 'cost_level2' not in roles:
			flash('Vous n\'avez pas l\'accès', 'danger')
			return redirect(url_for('admin.index'))
		declarationExists = db.session.query(CostDeclarationTable).filter_by(id=declaration_id).first()
		if declarationExists: #show update page else redirct with flash error
			currentDeclaration = db.session.query(CostDeclarationTable).filter(CostDeclarationTable.id==declaration_id).first()
			currentComplaint = db.session.query(ComplaintTable).filter(ComplaintTable.costtable_id==declaration_id).first()
			currentSupplier = db.session.query(Supplier).filter(Supplier.id == currentComplaint.supplier_id).first()	
			currentCostLines = db.session.query(CostType,CostDeclarationLine).join(CostDeclarationLine).filter(CostDeclarationLine.costtable_id==declaration_id).all()
			myDict = {
				'legend' : gettext("View Declaration"),
				'menu' : {},
				'title' : 'View Declaration',
			}
			return render_template("cost/view_declaration.html",myDict=myDict,complaint_id=currentComplaint.id, complaint_number=currentComplaint.number,declaration=currentDeclaration,costs=currentCostLines,supplier=currentSupplier, roles=roles)
		else:
			flash("Cette déclaration de coûts n'existe pas!",'danger')
			return redirect(url_for('cost.view_declarations'))
	else: 
		return redirect(url_for('cost.view_supplier_declaration',declaration_id=declaration_id, action='view'))
		

# ADD DECLARATION
@cost.route("/declarations/add",methods=['GET','POST'])
@login_required 
def add_declaration():
	roles = []
	for i in range(len(current_user.roles)):
		roles.append(current_user.roles[i].name)
	if current_user.type!='sysuser' or 'cost_level2' not in roles:
		flash('Vous n\'avez pas l\'accès', 'danger')
		return redirect(url_for('admin.index'))

	form = Add_Declaration_Form()
	if form.validate_on_submit():
		complaintID = form.complaint.data
		complaint = db.session.query(ComplaintTable).filter(ComplaintTable.id == complaintID).first()
		declarationExists = db.session.query(CostDeclarationTable).filter_by(complaint=complaint).first()
		if declarationExists:
			link = url_for('cost.view_declaration',declaration_id=declarationExists.id)
			flash(Markup('Cette réclamation a déjà une déclaration de coûts (<a href='+link+'>Afficher la déclaration</a>)'), 'danger')
			return redirect(url_for('cost.add_declaration'))
		else: 
			supplierCurrency = db.session.query(Supplier.currency).filter(Supplier.id == complaint.supplier_id)
			status = "Brouillon"
			newDeclaration = CostDeclarationTable(creationDate=datetime.now(),currency=supplierCurrency,totalCost=0,complaint=complaint,status=status)
			db.session.add(newDeclaration)
			db.session.flush()
			db.session.refresh(newDeclaration)
			dec_id = newDeclaration.id
			newDeclaration.number = "DEC-" + str(dec_id)
			db.session.commit()
			flash('La nouvelle déclaration ('+ str(newDeclaration.number) +') a été ajoutée avec succès!', 'success')
			return redirect(url_for('cost.view_declarations'))

	myDict = {
		'form':form,
		'legend' : gettext("Add Declaration"),
		'menu' : {},
		'title' : 'Add Declaration',
	}
	return render_template("cost/add_declaration.html",myDict=myDict, roles=roles)

# fetch complaint details 
@cost.route('/getdata/complaint_supplier/<complaint_id>')
def getComplaintSupplier(complaint_id):
	complaintSupplier = db.session.query(ComplaintTable.supplier_id).filter(ComplaintTable.id == complaint_id)
	supplierName = db.session.query(Supplier.name).filter(Supplier.id == complaintSupplier).first()
	return jsonify({'name':supplierName})



# Update declaration total
def updateDeclarationTotal(declaration_id):
	declaration = db.session.query(CostDeclarationTable).filter(CostDeclarationTable.id==declaration_id).first()
	costLinesTotal = db.session.query(func.sum(CostDeclarationLine.lineCost)).filter(CostDeclarationLine.costtable_id==declaration_id).scalar()
	if costLinesTotal is None:
		costLinesTotal = 0
	declaration.totalCost = costLinesTotal

@cost.route("/declarations/<int:declaration_id>/update",methods=['GET','POST'])
@login_required
def update_declaration(declaration_id):
	roles = []
	for i in range(len(current_user.roles)):
		roles.append(current_user.roles[i].name)
	if current_user.type!='sysuser' or 'cost_level2' not in roles:
		flash('Vous n\'avez pas l\'accès', 'danger')
		return redirect(url_for('admin.index'))
	
	# we are handling two forms in the same page through two bootstrap modals 
	declarationExists = db.session.query(CostDeclarationTable).filter_by(id=declaration_id).first()
	if declarationExists: #show update page else redirct with flash error
		add_form = Add_Cost_Line_Form()
		update_form = Update_Cost_Line_Form()
		currentDeclaration = db.session.query(CostDeclarationTable).filter(CostDeclarationTable.id==declaration_id).first()
		currentComplaint = db.session.query(ComplaintTable).filter(ComplaintTable.costtable_id==declaration_id).first()
		currentSupplier = db.session.query(Supplier).filter(Supplier.id == currentComplaint.supplier_id).first()	
		currentCostLines = db.session.query(CostType,CostDeclarationLine).join(CostDeclarationLine).filter(CostDeclarationLine.costtable_id==declaration_id).all()
		myDict = {
			'add_form':add_form,
			'update_form':update_form,
			'legend' : gettext("Declaration"),
			'menu' : {},
			'title' : 'Declaration',
		}

		#print("http post request from update_declaration")
		if add_form.submitadd.data and add_form.validate_on_submit: #post request
			#print(add_form.errors)
			flash('La nouvelle ligne de coûts a été ajoutée!','success')
			costTypeID = db.session.query(SuppCosts).filter(SuppCosts.id==add_form.code.data).first().costtype_id
			totalLineCost = (float(add_form.quantity.data)*float(add_form.unitcost.data)+float(add_form.othercost.data))*float(add_form.coefficient.data)
			newCostLine = CostDeclarationLine(lineCost=totalLineCost,costtype_id=costTypeID,costtable_id=int(declaration_id),hoursNumber=add_form.quantity.data,currency=currentSupplier.currency,lineComment=add_form.comment.data,coefficient=add_form.coefficient.data,unitcost=add_form.unitcost.data,othercost=add_form.othercost.data)
			db.session.add(newCostLine)
			updateDeclarationTotal(declaration_id)
			db.session.commit()
			return redirect(url_for('cost.update_declaration',declaration_id=declaration_id))
		elif update_form.submitupdate.data and update_form.validate_on_submit: #post request
			costLineID = int(update_form.identifier.data)
			costLine = db.session.query(CostDeclarationLine).filter(CostDeclarationLine.id==costLineID).first()
			costLine.hoursNumber = update_form.quantity.data
			costLine.unitcost = update_form.unitcost.data
			costLine.othercost = update_form.othercost.data
			costLine.lineComment = update_form.comment.data
			costLine.coefficient = update_form.coefficient.data
			costLine.lineCost = (float(update_form.quantity.data)*float(update_form.unitcost.data)+float(update_form.othercost.data))*float(update_form.coefficient.data)
			updateDeclarationTotal(declaration_id)
			db.session.commit()
			flash('La ligne de coûts a été mise à jour!','success')
			return redirect(url_for('cost.update_declaration',declaration_id=declaration_id))

		return render_template("cost/update_declaration.html",myDict=myDict,complaint_id=currentComplaint.id, complaint_number=currentComplaint.number,declaration=currentDeclaration,costs=currentCostLines,supplier=currentSupplier, roles=roles)
	else:
		flash("Cette déclaration de coûts n'existe pas!",'danger')
		return redirect(url_for('cost.view_declarations'))
		

#  COMPANY - CHANGE DECLARATION STATUS 
@cost.route("/declarations/<int:declaration_id>/update_status/<string:action>",methods=['GET','POST'])
@login_required
def update_declaration_status(declaration_id,action):
	declaration = db.session.query(CostDeclarationTable).filter_by(id=declaration_id).first()

	if declaration.status == "Brouillon" and action == "Soumettre":
		declaration.status = "Soumise"
		message = "La déclaration a été soumise au fournisseur!"
	elif declaration.status == "Validée" and action == "Facturer":
		numFacture = request.form.get("numFacture")
		declaration.billNumber = numFacture
		declaration.status = "Facturée"
		message = "La déclaration a été facturée!"
	elif declaration.status == "Facturée" and action == "Encaisser":
		pm = request.form.get("paymentMethod")
		declaration.paymentMethod = pm
		pn = request.form.get("paymentNumber")
		declaration.paymentNumber = pn
		declaration.status = "Encaissée"
		message = "La déclaration a été encaissée!"
	elif declaration.status == "Rejetée" and action == "Soumettre":
		declaration.status = "Soumise"
		message = "La déclaration a été soumise au fournisseur!"

	db.session.commit()
	flash(message,'success')
	return redirect(url_for('cost.update_declaration',declaration_id=declaration_id))

@cost.route("/declarations/<int:declaration_id>/delete/<int:line_id>",methods=['POST'])
@login_required
def delete_cost_line(line_id,declaration_id):
	myCostLine = db.session.query(CostDeclarationLine).filter(CostDeclarationLine.id==line_id and CostDeclarationLine.costtable_id==declaration_id).first()
	db.session.delete(myCostLine)
	updateDeclarationTotal(declaration_id)
	db.session.commit()
	flash('La ligne de coûts a été supprimée!', 'success')
	return redirect(url_for('cost.update_declaration',declaration_id=declaration_id))


# fetch supplier charges
@cost.route("/getdata/suppliercosts/<int:supplier_id>",methods=['GET'])
#@login_required
def getSupplierData(supplier_id):
	supplierCosts = db.session.query(CostType,SuppCosts).join(SuppCosts).filter(SuppCosts.supplier_id == supplier_id).all()
	supplier = db.session.query(Supplier).filter(Supplier.id==supplier_id).first()
	costs = []
	for c,s in supplierCosts:
		costs.append({
			'code':c.code,
			'description':c.description,
			'suppcostid':s.id,
			'unitcost':s.unitcost,
			'unit':c.unit
		})
	return jsonify(costs=costs,currency=supplier.currency)



# fetching cost line data 
@cost.route("/getdata/costline/<string:line_id>",methods=['GET'])
def getCostLineData(line_id):
	line_id = int(line_id)
	costLine = db.session.query(CostType,CostDeclarationLine).join(CostType,CostType.id == CostDeclarationLine.costtype_id).filter(CostDeclarationLine.id==line_id).first()
	return jsonify({
		'id':costLine.CostDeclarationLine.id,
		'description':costLine.CostType.description,
		'code':costLine.CostType.code,
		'unit':costLine.CostType.unit,
		'quantity':costLine.CostDeclarationLine.hoursNumber,
		'unitcost':costLine.CostDeclarationLine.unitcost,
		'comment':costLine.CostDeclarationLine.lineComment,
		'coefficient':costLine.CostDeclarationLine.coefficient,
		'currency':costLine.CostDeclarationLine.currency,
		'othercost':costLine.CostDeclarationLine.othercost
	})