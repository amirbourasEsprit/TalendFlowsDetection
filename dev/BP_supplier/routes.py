from flask import render_template, g, url_for, request, flash, Markup, send_file, send_from_directory, redirect, jsonify, abort, Blueprint, request, current_app
from flask_login import login_user, current_user, logout_user, login_required
from dev import db, bcrypt, app
from dev.models import *
from dev.BP_auth.forms import LoginForm
#from dev.BP_auth.utils import save_picture, senEmail, send_mail, send_reset_email
from dev.BP_supplier.forms import *
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadTimeSignature
from flask_babel import Babel, format_date, gettext
from datetime import datetime, timedelta
from sqlalchemy.exc import IntegrityError
from werkzeug.utils import secure_filename
from dev.BP_supplier.utils import *
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


supp = Blueprint('supp', __name__)
s=URLSafeTimedSerializer(app.config['SECRET_KEY'])
SUPP_LOGO_PATH='C:/Users/boura/Desktop/testflask/SRM-Project/SRM-MAIN/app/dev/static/img/SupplierLogo'
SUPP_LOGO_ALLOWED_EXT={'jpeg', 'jpg', 'png', 'gif'}
CERTIF_ATT_PATH ='C:/Users/boura/Desktop/testflask/SRM-Project/SRM-MAIN/app/dev/documents_directory/certif_doc'
ALLOWED_EXTENSIONS = { 'pdf','jpeg', 'jpg', 'png', 'gif'}
QM_ATT_PATH ='C:/Users/boura/Desktop/testflask/SRM-Project/SRM-MAIN/app/dev/documents_directory/qualitymanual_doc'
ALLOWED_EXTENSIONS = { 'pdf','jpeg', 'jpg', 'png', 'gif'}


@supp.route("/supplier", methods=['GET', 'POST'])
@login_required
def supplier():
	roles = []
	for i in range(len(current_user.roles)):
		roles.append(current_user.roles[i].name)
	if current_user.type != 'sysuser' and 'super_admin' not in roles and 'supplier_level1' not in roles and 'supplier_level2' not in roles:
		flash('Vous n\'avez pas l\'accès', 'danger')
		return redirect(url_for('admin.index'))

	form = Add_Excel_Form()
	suppliers = db.session.query(Supplier).all()

	myDict = {
		'form' : form,
        'legend' : gettext("Supplier"),
        'menu' : {},
		'title' : 'Supplier',
    }
	return render_template("supplier/supplier.html", myDict=myDict, suppliers=suppliers, roles=roles)

@supp.route("/add_supplier", methods=['GET', 'POST'])
@login_required
def add_supplier():
	roles = []
	for i in range(len(current_user.roles)):
		roles.append(current_user.roles[i].name)
	if 'super_admin' not in roles and 'supplier_level2' not in roles:
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
			name = feuille.cell_value(rowx=i, colx=0)
			adresse = feuille.cell_value(rowx=i, colx=1)
			phone = feuille.cell_value(rowx=i, colx=2)
			taxRegisration = feuille.cell_value(rowx=i, colx=3)
			supp = db.session.query(Supplier).filter(Supplier.taxRegisration==taxRegisration).first()
			if not supp:
				supplier = Supplier(name=name, adresse=adresse, phone=phone, taxRegisration=taxRegisration)
				db.session.add(supplier)
				db.session.commit()						
		os.remove(filename)
		return redirect(url_for('supp.supplier'))

@supp.route("/supplier_profile/<int:supplier_id>", methods=['GET', 'POST'])
@login_required
def supplier_profile(supplier_id):
	roles = []
	for i in range(len(current_user.roles)):
		roles.append(current_user.roles[i].name)
	if 'super_admin' not in roles and 'supplier_level1' not in roles and 'supplier_level2' not in roles:
		flash('Vous n\'avez pas l\'accès', 'danger')
		return redirect(url_for('admin.index'))

	supplier = db.session.query(Supplier).filter(Supplier.id==supplier_id).first()
	category = db.session.query(SuppCategory).filter(SuppCategory.id==supplier.category_id).first()
	contacts = db.session.query(SuppContact).filter(SuppContact.supplier_id==supplier_id).all()
	certificats = db.session.query(SuppCertification).filter(SuppCertification.supplier_id==supplier_id).all()
	qualitymanuals = db.session.query(QualityManual).filter(QualityManual.supplier_id==supplier_id).all()
	visavis = db.session.query(VisAVis).filter(VisAVis.supplier_id==supplier_id).all()
	f2 = Update_Logo_Form()

	def user_name(param_id):
		u = db.session.query(User).filter(User.id==param_id).first()
		return u

	def doc_name(param_id):
		d = db.session.query(DocumentType).filter(DocumentType.id==param_id).first()
		return d.name

	myDict = {
		'f2': f2,
        'legend' : gettext("Supplier Profile"),
        'menu' : {},
		'title' : 'Supplier Profile',
    }
	return render_template("supplier/supplier_profile.html", myDict=myDict, supplier=supplier, category=category, contacts=contacts, certificats=certificats, qualitymanuals=qualitymanuals, visavis=visavis, user_name=user_name, doc_name=doc_name, roles=roles)

@supp.route("/update_supplierprofile/<int:supplier_id>", methods=['GET', 'POST'])
@login_required
def update_supplierprofile(supplier_id):
    roles = []
    for i in range(len(current_user.roles)):
        roles.append(current_user.roles[i].name)
    if current_user.type!='suppuser' or 'supplier_level2' not in roles:
        flash('Vous n\'avez pas l\'accès', 'danger')
        return redirect(url_for('admin.index'))

    supplier = db.session.query(Supplier).filter(Supplier.id == supplier_id).first()
    form = Update_Supp_profile_Form()

    if form.validate_on_submit():
        supplier.name = form.name.data
        supplier.adresse = form.adresse.data
        supplier.phone = form.phone.data
        supplier.fax = form.fax.data
        supplier.currency = form.currency.data
        supplier.jalan3D=form.jalan3D.data
        supplier.jalan5D=form.jalan5D.data
        supplier.jalan8D=form.jalan8D.data
        supplier.initialResponse=form.initialResponse.data
        supplier.finalResponse=form.finalResponse.data
        db.session.commit()
        flash('Données utilisateurs sont bien mises à jour', 'success')
        return redirect(url_for('supp.supplier_profile', supplier_id=supplier_id))

    elif request.method == 'GET':
        form.uniqueIdentifier.data = supplier.id
        form.uniqueIdentifier.render_kw = {'disabled': 'disabled'}
        form.name.data = supplier.name
        form.adresse.data = supplier.adresse
        form.phone.data = supplier.phone
        form.fax.data = supplier.fax
        form.currency.data = supplier.currency
        form.taxRegisration.data = supplier.taxRegisration
        form.taxRegisration.render_kw = {'disabled': 'disabled'}
        form.jalan3D.data= supplier.jalan3D
        form.jalan5D.data= supplier.jalan5D
        form.jalan8D.data= supplier.jalan8D
        form.initialResponse.data= supplier.initialResponse
        form.finalResponse.data= supplier.finalResponse

    myDict = {
        'form': form,
        'legend': gettext("Mettre à jour le fournisseur"),
        'menu': {},
        'title': 'Mettre à jour le fournisseur',
    }
    return render_template("supplier/update_supplierprofile.html", myDict=myDict, supplier_id=supplier_id, roles=roles)

@supp.route("/update_supplierprofile2/<int:supplier_id>", methods=['GET', 'POST'])
@login_required
def update_supplierprofile2(supplier_id):
    roles = []
    for i in range(len(current_user.roles)):
        roles.append(current_user.roles[i].name)
    if current_user.type!='sysuser' or 'supplier_level2' not in roles:
        flash('Vous n\'avez pas l\'accès', 'danger')
        return redirect(url_for('admin.index'))

    supplier = db.session.query(Supplier).filter(Supplier.id == supplier_id).first()
    form = Update_Supp_profile_Form2(category=supplier.category_id)
    form.category.choices = [(str(s.id), s.name) for s in db.session.query(SuppCategory).all()]

    if form.validate_on_submit():
        supplier.status=form.status.data
        supplier.category_id=form.category.data
        db.session.commit()
        flash('Données utilisateurs sont bien mises à jour', 'success')
        return redirect(url_for('supp.supplier_profile', supplier_id=supplier_id))

    elif request.method == 'GET':
        form.status.data = supplier.status

    myDict = {
        'form': form,
        'legend': gettext("Mettre à jour le fournisseur"),
        'menu': {},
        'title': 'Mettre à jour le fournisseur',
    }
    return render_template("supplier/update_supplierprofile2.html", myDict=myDict, supplier_id=supplier_id, roles=roles)

@supp.route("/edit_visavis/<int:supplier_id>", methods=['GET', 'POST'])
@login_required
def edit_visavis(supplier_id):
    roles = []
    for i in range(len(current_user.roles)):
        roles.append(current_user.roles[i].name)
    if current_user.type!='suppuser' or 'supplier_level2' not in roles:
        flash('Vous n\'avez pas l\'accès', 'danger')
        return redirect(url_for('admin.index'))
    
    v1=db.session.query(VisAVis).filter(VisAVis.supplier_id==supplier_id, VisAVis.doctype_id==1).all()
    v2=db.session.query(VisAVis).filter(VisAVis.supplier_id==supplier_id, VisAVis.doctype_id==2).all()
    v3=db.session.query(VisAVis).filter(VisAVis.supplier_id==supplier_id, VisAVis.doctype_id==3).all()
    
    liste_ssy1 = []
    liste_ssp1 = []
    for x in range(len(v1)):
        if db.session.query(User).filter(User.id==v1[x].user_id).first().type=="sysuser":
            liste_ssy1.append(v1[x].user_id)
        elif db.session.query(User).filter(User.id==v1[x].user_id).first().type=="suppuser":
            liste_ssp1.append(v1[x].user_id)
    liste_ssy2 = []
    liste_ssp2 = []
    for x in range(len(v2)):
        if db.session.query(User).filter(User.id==v2[x].user_id).first().type=="sysuser":
            liste_ssy2.append(v2[x].user_id)
        elif db.session.query(User).filter(User.id==v2[x].user_id).first().type=="suppuser":
            liste_ssp2.append(v2[x].user_id)
    liste_ssy3 = []
    liste_ssp3 = []
    for x in range(len(v3)):
        if db.session.query(User).filter(User.id==v3[x].user_id).first().type=="sysuser":
            liste_ssy3.append(v3[x].user_id)
        elif db.session.query(User).filter(User.id==v3[x].user_id).first().type=="suppuser":
            liste_ssp3.append(v3[x].user_id)
    
    form = Edit_VisVis_Form(sys_user1=liste_ssy1, supp_user1=liste_ssp1, sys_user2=liste_ssy2, supp_user2=liste_ssp2, sys_user3=liste_ssy3, supp_user3=liste_ssp3)

    form.sys_user1.choices=[(str(s.id), s.firstName +" "+ s.lastName) for s in db.session.query(SysUser).all()]
    form.supp_user1.choices=[(str(s.id), s.firstName +" "+ s.lastName) for s in db.session.query(SuppUser).filter(SuppUser.supplier_id==supplier_id).all()]
    form.sys_user2.choices=[(str(s.id), s.firstName +" "+ s.lastName) for s in db.session.query(SysUser).all()]
    form.supp_user2.choices=[(str(s.id), s.firstName +" "+ s.lastName) for s in db.session.query(SuppUser).filter(SuppUser.supplier_id==supplier_id).all()]
    form.sys_user3.choices=[(str(s.id), s.firstName +" "+ s.lastName) for s in db.session.query(SysUser).all()]
    form.supp_user3.choices=[(str(s.id), s.firstName +" "+ s.lastName) for s in db.session.query(SuppUser).filter(SuppUser.supplier_id==supplier_id).all()]
    
    if form.validate_on_submit():
        v = db.session.query(VisAVis).filter(VisAVis.supplier_id==supplier_id).all()
        for x in range(len(v)):
            db.session.delete(v[x])
            db.session.commit()
        sys_user1_list = request.form.getlist('sys_user1')
        supp_user1_list = request.form.getlist('supp_user1')
        sys_user2_list = request.form.getlist('sys_user2')
        supp_user2_list = request.form.getlist('supp_user2')
        sys_user3_list = request.form.getlist('sys_user3')
        supp_user3_list = request.form.getlist('supp_user3')
        for i in sys_user1_list:
            visavis = VisAVis(supplier_id=supplier_id, user_id=i, doctype_id=1)
            db.session.add(visavis)
            db.session.commit()
        for i in supp_user1_list:
            visavis = VisAVis(supplier_id=supplier_id, user_id=i, doctype_id=1)
            db.session.add(visavis)
            db.session.commit()
        for i in sys_user2_list:
            visavis = VisAVis(supplier_id=supplier_id, user_id=i, doctype_id=2)
            db.session.add(visavis)
            db.session.commit()
        for i in supp_user2_list:
            visavis = VisAVis(supplier_id=supplier_id, user_id=i, doctype_id=2)
            db.session.add(visavis)
            db.session.commit()
        for i in sys_user3_list:
            visavis = VisAVis(supplier_id=supplier_id, user_id=i, doctype_id=3)
            db.session.add(visavis)
            db.session.commit()
        for i in supp_user3_list:
            visavis = VisAVis(supplier_id=supplier_id, user_id=i, doctype_id=3)
            db.session.add(visavis)
            db.session.commit()
        flash('Données utilisateurs sont bien mises à jour', 'success')
        return redirect(url_for('supp.supplier_profile', supplier_id=supplier_id))
    myDict = {
        'form' : form,
        'legend': gettext("Certificat"),
        'menu': {},
        'title': 'Certificat',
    }
    
    return render_template("supplier/edit_visavis.html", myDict=myDict, supplier_id=supplier_id, roles=roles)


@supp.route("/update_supplierprofile/<int:supplier_id>/update_logo", methods=['GET', 'POST'])
@login_required
def update_logo_supplier(supplier_id):
	roles = []
	for i in range(len(current_user.roles)):
		roles.append(current_user.roles[i].name)
	if current_user.type!='suppuser' or 'supplier_level2' not in roles:
		flash('Vous n\'avez pas l\'accès', 'danger')
		return redirect(url_for('admin.index'))

	f2 = Update_Logo_Form()
	supplier = db.session.query(Supplier).filter(Supplier.id==supplier_id).first()

	if f2.validate_on_submit():
		if supplier.logo:
			file = SUPP_LOGO_PATH + "/" + supplier.logo
			os.remove(file)
		f = request.files['file']
		filename = secure_filename(f.filename)
		name = str(supplier_id)+"_"+filename	
		supplier.logo= name	
		f.save(os.path.join(SUPP_LOGO_PATH, name))
		db.session.commit()
		return redirect(url_for('supp.supplier_profile', supplier_id=supplier_id))
	else:
		flash('vérifiez le type de l\'image', 'danger')
		return redirect(url_for('supp.supplier_profile', supplier_id=supplier_id))

@supp.route("/add_qualitymanual/<int:supplier_id>", methods=['GET', 'POST'])
@login_required
def add_qualitymanual(supplier_id):
    roles = []
    for i in range(len(current_user.roles)):
        roles.append(current_user.roles[i].name)
    if current_user.type!='suppuser' or 'supplier_level2' not in roles:
        flash('Vous n\'avez pas l\'accès', 'danger')
        return redirect(url_for('admin.index'))

    form = Add_qualitymanual_Form()
    if form.validate_on_submit():
        qualitymanual = QualityManual(name=form.name.data, status='créé', supplier_id=supplier_id)
        db.session.add(qualitymanual)
        db.session.flush()
        db.session.refresh(qualitymanual)
        qm_id = qualitymanual.id
        f = request.files['attachement']
        if f:
            filename = secure_filename(f.filename)
            file_name = str(qm_id) + "_" + filename
            f.save(os.path.join(QM_ATT_PATH, file_name))
        qualitymanual.attachement=file_name
        db.session.commit()
        flash('Manuel de qualité est ajouté avec succés', 'success')
        return redirect(url_for('supp.supplier_profile', supplier_id=supplier_id))

    myDict = {
        'form': form,
        'legend': gettext("Ajouter un manuel de qualité"),
        'menu': {},
        'title': 'Ajouter un manuel de qualité',
    }
    return render_template('supplier/add_qualitymanual.html', myDict=myDict, supplier_id=supplier_id, roles=roles)

@supp.route("/qualitymanual", methods=['GET', 'POST'])
@login_required
def qualitymanual():
    roles = []
    for i in range(len(current_user.roles)):
        roles.append(current_user.roles[i].name)
    if 'super_admin' not in roles:
        flash('Vous n\'avez pas l\'accès', 'danger')
        return redirect(url_for('admin.index'))

    qualitymanuals = db.session.query(QualityManual).all()

    def select_sup(param_id):
        sup = db.session.query(Supplier).filter(Supplier.id==param_id).first()
        return sup

    myDict = {
        'legend': gettext("Certificat"),
        'menu': {},
        'title': 'Certificat',
    }
    return render_template("supplier/quality_manual.html", myDict=myDict, qualitymanuals=qualitymanuals, select_sup=select_sup, roles=roles)


@supp.route("/valid_qualitymanual/<int:qualitymanual_id>", methods=['GET', 'POST'])
@login_required
def valid_qualitymanual(qualitymanual_id):
	roles = []
	for i in range(len(current_user.roles)):
		roles.append(current_user.roles[i].name)
	if  current_user.type!="sysuser" or 'supplier_level2' not in roles:
		flash('Vous n\'avez pas l\'accès', 'danger')
		return redirect(url_for('admin.index'))

	qualitymanual = db.session.query(QualityManual).filter(QualityManual.id==qualitymanual_id).first()
	qualitymanual.status='validé'
	db.session.commit()	
	return redirect(url_for('supp.qualitymanual'))

@supp.route("/consult_qualitymanual/<int:qualitymanual_id>", methods=['GET', 'POST'])
@login_required
def consult_qualitymanual(qualitymanual_id):
	roles = []
	for i in range(len(current_user.roles)):
		roles.append(current_user.roles[i].name)
	if 'supplier_level1' not in roles and 'supplier_level2' not in roles:
		flash('Vous n\'avez pas l\'accès', 'danger')
		return redirect(url_for('admin.index'))

	qm = db.session.query(QualityManual).filter(QualityManual.id==qualitymanual_id).first()
	return send_from_directory(QM_ATT_PATH, qm.attachement)

@supp.route("/certificate", methods=['GET', 'POST'])
@login_required
def certificate():
    roles = []
    for i in range(len(current_user.roles)):
        roles.append(current_user.roles[i].name)
    if 'super_admin' not in roles:
        flash('Vous n\'avez pas l\'accès', 'danger')
        return redirect(url_for('admin.index'))

    certificates = db.session.query(SuppCertification,CertificationType,Supplier).join(SuppCertification,SuppCertification.certificationType_id==CertificationType.id).join(Supplier,SuppCertification.supplier_id==Supplier.id).all()    
    myDict = {
        'legend': gettext("Certificat"),
        'menu': {},
        'title': 'Certificat',
    }
    return render_template("supplier/certificate.html", myDict=myDict, certificates=certificates, supplier=supplier, roles=roles)

@supp.route("/add_certificate/<int:supplier_id>", methods=['GET', 'POST'])
@login_required
def add_certificate(supplier_id):
    roles = []
    for i in range(len(current_user.roles)):
        roles.append(current_user.roles[i].name)
    if current_user.type!='suppuser' or 'supplier_level2' not in roles:
        flash('Vous n\'avez pas l\'accès', 'danger')
        return redirect(url_for('admin.index'))

    form = Add_certificate_Form()
    form.type.choices = [(str(s.id), s.name) for s in db.session.query(CertificationType).all()]
    if form.validate_on_submit():
        certificate = SuppCertification(name=form.name.data, expirationDate=form.expirationDate.data,status="créée",supplier_id=supplier_id , certificationType_id=form.type.data)
        db.session.add(certificate)
        db.session.flush()
        db.session.refresh(certificate)
        certif_id = certificate.id
        f = request.files['attachement']
        if f:
            filename = secure_filename(f.filename)
            file_name = str(certif_id) + "_" + filename
            f.save(os.path.join(CERTIF_ATT_PATH, file_name))
        certificate.attachement=file_name
        db.session.commit()
        flash('Certificat est créée avec succés', 'success')
        return redirect(url_for('supp.supplier_profile', supplier_id=supplier_id))

    myDict = {
        'form': form,
        'legend': gettext("Ajouter une certificat"),
        'menu': {},
        'title': 'Ajouter une certificat',
    }
    return render_template('supplier/add_certificate.html', myDict=myDict,supplier_id=supplier_id, roles=roles)

@supp.route("/certificate/<int:certificate_id>/delete", methods=['POST'])
@login_required
def delete_certificate(certificate_id):
    roles = []
    for i in range(len(current_user.roles)):
        roles.append(current_user.roles[i].name)
    if 'super_admin' not in roles:
        flash('Vous n\'avez pas l\'accès', 'danger')
        return redirect(url_for('admin.index'))

    cmp = db.session.query(SuppCertification).filter(SuppCertification.id == certificate_id).first()
    db.session.delete(cmp)
    db.session.commit()
    flash('Certificat supprimée', 'success')
    return redirect(url_for('supp.certificate'))

@supp.route("/valid_certificate/<int:certificate_id>", methods=['GET', 'POST'])
@login_required
def valid_certificate(certificate_id):
	roles = []
	for i in range(len(current_user.roles)):
		roles.append(current_user.roles[i].name)
	if 'super_admin' not in roles:
		flash('Vous n\'avez pas l\'accès', 'danger')
		return redirect(url_for('admin.index'))

	certificate = db.session.query(SuppCertification).filter(SuppCertification.id==certificate_id).first()
	certificate.status='validée'
	db.session.commit()
	return redirect(url_for('supp.certificate'))

@supp.route("/consult_certificate/<int:certificate_id>", methods=['GET', 'POST'])
@login_required
def consult_certificate(certificate_id):
	roles = []
	for i in range(len(current_user.roles)):
		roles.append(current_user.roles[i].name)
	if 'super_admin' not in roles:
		flash('Vous n\'avez pas l\'accès', 'danger')
		return redirect(url_for('admin.index'))

	certif = db.session.query(SuppCertification).filter(SuppCertification.id==certificate_id).first()
	return send_from_directory(CERTIF_ATT_PATH, certif.attachement)

@supp.route("/add_suppContact/<int:supplier_id>", methods=['GET', 'POST'])
@login_required
def add_suppContact(supplier_id):
    roles = []
    for i in range(len(current_user.roles)):
        roles.append(current_user.roles[i].name)
    if current_user.type!='suppuser' or 'supplier_level2' not in roles:
        flash('Vous n\'avez pas l\'accès', 'danger')
        return redirect(url_for('admin.index'))

    form = Add_suppContact_Form()

    if form.validate_on_submit():
        suppcontact = SuppContact(firstName=form.firstName.data, lastName=form.lastName.data,email=form.email.data, phone=form.phone.data, function=form.function.data, supplier_id=supplier_id)
        db.session.add(suppcontact)
        db.session.commit()
        flash('Contact est créée avec succés', 'success')
        return redirect(url_for('supp.supplier_profile', supplier_id=supplier_id))

    myDict = {
        'form': form,
        'legend': gettext("Ajouter un contact"),
        'menu': {},
        'title': 'Ajouter un contact',
    }
    return render_template('supplier/add_suppContact.html', myDict=myDict,supplier_id=supplier_id, roles=roles)
    
@supp.route("/delete_suppContact/<int:contact_id>/delete/<int:supplier_id>", methods=['POST'])
@login_required
def delete_suppContact(contact_id,supplier_id):
    roles = []
    for i in range(len(current_user.roles)):
        roles.append(current_user.roles[i].name)
    if current_user.type!='suppuser' or 'supplier_level2' not in roles:
        flash('Vous n\'avez pas l\'accès', 'danger')
        return redirect(url_for('admin.index'))

    cmp = db.session.query(SuppContact).filter(SuppContact.id == contact_id).first()
    db.session.delete(cmp)
    db.session.commit()
    flash('Contact supprimée', 'success')
    return redirect(url_for('supp.supplier_profile', supplier_id=supplier_id))

@supp.route("/update_suppContact/<int:contact_id>/<int:supplier_id>", methods=['GET', 'POST'])
@login_required
def update_suppContact(contact_id,supplier_id):
    roles = []
    for i in range(len(current_user.roles)):
        roles.append(current_user.roles[i].name)
    if current_user.type!='suppuser' or 'supplier_level2' not in roles:
        flash('Vous n\'avez pas l\'accès', 'danger')
        return redirect(url_for('admin.index'))

    Contact = db.session.query(SuppContact).filter(SuppContact.id == contact_id).first()
   
    form = Update_Supp_contact_Form()

    if form.validate_on_submit():
        Contact.firstName = form.firstName.data
        Contact.lastName = form.lastName.data
        Contact.function=form.function.data
        Contact.email=form.email.data
        Contact.phone = form.phone.data

        db.session.commit()
        flash('Données Contact sont bien mises à jour', 'success')
        return redirect(url_for('supp.supplier_profile', supplier_id=supplier_id))
    elif request.method == 'GET':
        form.firstName.data = Contact.firstName
        form.lastName.data = Contact.lastName
        form.function.data = Contact.function
        form.email.data = Contact.email
        form.phone.data = Contact.phone

    myDict = {
        'form': form,
        'legend': gettext("Mettre à jour le contact"),
        'menu': {},
        'title': 'Mettre à jour le contact',
    }
    return render_template("supplier/update_suppContact.html", myDict=myDict,supplier_id=supplier_id, roles=roles)

@supp.route("/update_certificate/<int:certificat_id>/<int:supplier_id>", methods=['GET', 'POST'])
@login_required
def update_certificate(certificat_id,supplier_id):
    roles = []
    for i in range(len(current_user.roles)):
        roles.append(current_user.roles[i].name)
    if current_user.type!='suppuser' or 'supplier_level2' not in roles:
        flash('Vous n\'avez pas l\'accès', 'danger')
        return redirect(url_for('admin.index'))

    certif = db.session.query(SuppCertification).filter(SuppCertification.id == certificat_id).first()
   
    form = Update_Supp_certificate_Form()

    if form.validate_on_submit():
        certif.name = form.name.data
       

        db.session.commit()
        flash('Données Contact sont bien mises à jour', 'success')
        return redirect(url_for('supp.supplier_profile', supplier_id=supplier_id))
    elif request.method == 'GET':
        form.name.data = certif.name
      
    myDict = {
        'form': form,
        'legend': gettext("Mettre à jour le certificat"),
        'menu': {},
        'title': 'Mettre à jour le certificat',
    }
    return render_template("supplier/update_suppCertif.html", myDict=myDict,supplier_id=supplier_id, roles=roles)

@supp.route("/supplier_profile/<int:supplier_id>/charges",methods=['GET','POST'])
@login_required
def view_supplier_charges(supplier_id):
	roles = []
	for i in range(len(current_user.roles)):
		roles.append(current_user.roles[i].name)
	if 'super_admin' not in roles and 'supplier_level1' not in roles and 'supplier_level2' not in roles:
		flash('Vous n\'avez pas l\'accès', 'danger')
		return redirect(url_for('admin.index'))

	charges = db.session.query(CostType).all()
	##suppCharges = db.session.query(SuppCosts).filter(SuppCosts.supplier_id == supplier)
	suppCharges = db.session.query(CostType,SuppCosts).join(SuppCosts).filter(SuppCosts.supplier_id == supplier_id).all()

	mySupplier = db.session.query(Supplier).filter(Supplier.id==supplier_id).first()
	myDict = {
		'form': {},
		'legend' : gettext("Frais Fournisseur"),
		'menu' : {},
		'title' : 'Frais Fournisseur',
	}
	return render_template("supplier/supplierCharges.html",myDict=myDict,charges=charges,suppCharges=suppCharges,mySupplier=mySupplier, roles=roles)

@supp.route("/supplier_profile/<int:supplier_id>/charges/add",methods=['GET','POST'])
@login_required
def add_supplier_charge(supplier_id):
	roles = []
	for i in range(len(current_user.roles)):
		roles.append(current_user.roles[i].name)
	if current_user.type!='sysuser' or 'supplier_level2' not in roles:
		flash('Vous n\'avez pas l\'accès', 'danger')
		return redirect(url_for('admin.index'))

	form = Add_Supplier_Charge_Form()
	# sql query 
	charges = db.session.execute('SELECT * FROM CostType WHERE CostType.id NOT IN (SELECT SuppCosts.costtype_id FROM SuppCosts WHERE SuppCosts.supplier_id='+str(supplier_id)+')')
	#charges = db.session.query(CostType).filter(CostType.id.notin_((db.session.query(SuppCosts.costtype_id).filter(SuppCosts.supplier_id==supplier_id))))
	form.code.choices = [(charge.id, charge.code + ' - ' + charge.description) for charge in charges]
	supplier = db.session.query(Supplier).filter(Supplier.id==supplier_id).first()
	supplier_name = supplier.name
	form.currency.data = supplier.currency
	
	if form.validate_on_submit():
		charge = db.session.query(CostType).filter(CostType.id==form.code.data).first()
		
		newSupplierCharge = SuppCosts(supplier_id=supplier_id,costtype_id=charge.id,unitcost=form.unitcost.data)
		db.session.add(newSupplierCharge)
		db.session.commit()
		flash('Le frais '+charge.code+' a été ajouté à liste des frais de ce fournisseur!', 'success')
		return redirect(url_for('supp.view_supplier_charges',supplier_id=supplier_id))
    
	myDict = {
		'form' : form,
		'legend' : gettext("Ajout Frais"),
		'menu' : {},
		'title' : 'Ajout Frais',
	}

	return render_template("supplier/add_suppliercharge.html",myDict=myDict,supplier_id=supplier_id,supplier_name=supplier_name, roles=roles)


@supp.route('/charge/<charge_id>')
def getChargeDetails(charge_id):
	charge = db.session.query(CostType).filter(CostType.id==charge_id).first()
	return jsonify({'id':charge.id,'code':charge.code,'unit':charge.unit,'description':charge.description})

@supp.route("/supplier_profile/<int:supplier_id>/charges/<int:suppCharge_id>/update",methods=['GET','POST'])
@login_required
def update_supplier_charge(supplier_id,suppCharge_id):
	roles = []
	for i in range(len(current_user.roles)):
		roles.append(current_user.roles[i].name)
	if current_user.type!='sysuser' or 'supplier_level2' not in roles:
		flash('Vous n\'avez pas l\'accès', 'danger')
		return redirect(url_for('admin.index'))

	form = Update_Supplier_Charge_Form()
	supplier = db.session.query(Supplier).filter(Supplier.id==supplier_id).first()
	suppcharge = db.session.query(SuppCosts).filter(SuppCosts.id==suppCharge_id).first()
	charge = db.session.query(CostType).filter(CostType.id==suppcharge.costtype_id).first()

	if form.validate_on_submit():
		suppcharge.unitcost = form.unitcost.data
		db.session.commit()
		flash('La valeur du frais '+charge.code+' a été mise à jour!', 'success')
		return redirect(url_for('supp.view_supplier_charges',supplier_id=supplier_id))
	elif request.method == 'GET':
		form.code.data = charge.code + ' - ' + charge.description
		form.unit.data = charge.unit
		form.currency.data = supplier.currency
		form.unitcost.data = suppcharge.unitcost

	myDict = {
		'form' : form,
        'legend' : gettext("Modifier Frais"),
        'menu' : {},
		'title' : 'Modifier Frais',
    }

	return render_template("supplier/update_suppliercharge.html",myDict=myDict,supplier_id=supplier_id,supplier_name=supplier.name,charge_code=charge.code, roles=roles)

@supp.route("/supplier_profile/<int:supplier_id>/supplierCharges/<int:suppCharge_id>/delete",methods=['GET','POST'])
@login_required
def delete_supplier_charge(suppCharge_id,supplier_id):
	roles = []
	for i in range(len(current_user.roles)):
		roles.append(current_user.roles[i].name)
	if current_user.type!='sysuser' or 'supplier_level2' not in roles:
		flash('Vous n\'avez pas l\'accès', 'danger')
		return redirect(url_for('admin.index'))

	myCharge = db.session.query(SuppCosts).filter(SuppCosts.id==suppCharge_id).first()
	db.session.delete(myCharge)
	db.session.commit()
	flash('Le frais a été supprimé de la liste!', 'success')
	return redirect(url_for('supp.view_supplier_charges',supplier_id=supplier_id))

# GET SUPPLIER CHARGES / fetch
@supp.route("/getdata/suppliercosts/<int:supplier_id>",methods=['GET'])
@login_required
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

# for fetching cost line data 
@supp.route("/getdata/costline/<string:line_id>",methods=['GET'])
@login_required
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
