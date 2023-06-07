from datetime import datetime
from flask import Flask, render_template, url_for, flash, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Table, Column, Integer, ForeignKey, LargeBinary, Float, func 
from sqlalchemy.orm import relationship
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from dev import db, login_manager, app, bcrypt
from flask_login import UserMixin

app = Flask(__name__)

app.config['SECRET_KEY'] = '4c399d093bc7a589475b74be367ab92d'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:azerty@127.0.0.1/srm'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
hashed_password = bcrypt.generate_password_hash('123456').decode('utf-8')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

########################### association AssignUserRole #############################

AssignUserRole = db.Table('AssignUserRole', db.metadata,
    db.Column('role_id', db.Integer, db.ForeignKey('role.id')),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'))
)

########################### user #############################

class User(db.Model, UserMixin):
    __tablename__= "user"
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    type = db.Column(db.String(20), unique=False, nullable=True )
    firstName = db.Column(db.String(60), unique=False, nullable=False )
    lastName = db.Column(db.String(60), unique=False, nullable=False )
    email = db.Column(db.String(120), unique=True, nullable=False )
    password = db.Column(db.String(60), nullable=True, default=hashed_password)
    phone = db.Column(db.String(12), nullable=True)
    language = db.Column(db.String(2), nullable=True)
    actif = db.Column(db.Boolean, default=True)
    super_admin = db.Column(db.Boolean, default=False)
    function_id = db.Column(db.Integer, db.ForeignKey('function.id'), nullable=True)
    vis_vis = db.relationship('VisAVis', backref='user', lazy=True)
    roles = db.relationship(
        "Role",
        secondary=AssignUserRole,
        backref="user")
    __mapper_args__ = {
           'polymorphic_identity': 'user',
           'polymorphic_on':type,
       }
    
    def __repr__(self):
        return f"{self.firstName} {self.lastName}"

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

########################### SysUser #############################

class SysUser(User):
    __tablename__= "sysuser"
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    site_id = db.Column(db.Integer, db.ForeignKey('site.id'), nullable=True)
    complaints = db.relationship("ComplaintTable", backref="sysuser", lazy=True)
    __mapper_args__ = {
           'polymorphic_identity': 'sysuser',
       }    

########################### SuppUser #############################

class SuppUser(User):
    __tablename__= "suppuser"
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey('supplier.id'), nullable=True)
    __mapper_args__ = {
           'polymorphic_identity': 'suppuser',
       }

########################### role #############################

class Role(db.Model):
    __tablename__= "role"
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(60), unique=True, nullable=False)
    description = db.Column(db.String(60), nullable=True)
    users = db.relationship(
        "User",
        secondary=AssignUserRole,
        backref="role")

    def __repr__(self):
        return f"{self.name}"

########################### function #############################

class Function(db.Model):
    __tablename__= "function"
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(60), unique=True, nullable=False)
    users = db.relationship("User", backref="function", lazy=True)

    def __repr__(self):
        return f"{self.name}"

########################### site #############################

class Site(db.Model):
    __tablename__= "site"
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(60), nullable=True)
    adresse = db.Column(db.String(60), nullable=True)
    city = db.Column(db.String(60), nullable=True)
    country = db.Column(db.String(60), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    fax = db.Column(db.String(20), nullable=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=True)
    sysusers = db.relationship('SysUser', backref='site', lazy=True)

    def __repr__(self):
        return f"{self.name}"

########################### company #############################

class Company(db.Model):
    __tablename__= "company"
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(60), nullable=True)
    adresse = db.Column(db.String(60), nullable=True)
    city = db.Column(db.String(60), nullable=True)
    country = db.Column(db.String(60), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    fax = db.Column(db.String(20), nullable=True)
    taxRegisration = db.Column(db.String(60), unique=True, nullable=True)
    logo = db.Column(db.String(200), nullable=True)
    sites = db.relationship('Site', backref='company', lazy=True)

    def __repr__(self):
        return f"{self.name}"

########################### supplier #############################

class Supplier(db.Model):
    __tablename__= "supplier"
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(60), nullable=True)
    adresse = db.Column(db.String(60), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    fax = db.Column(db.String(20), nullable=True)
    taxRegisration = db.Column(db.String(60), unique=True, nullable=True)
    status = db.Column(db.String(20), nullable=True)
    jalan3D = db.Column(db.Integer, nullable=True)
    jalan5D = db.Column(db.Integer, nullable=True)
    jalan8D = db.Column(db.Integer, nullable=True)
    logo = db.Column(db.String(200), nullable=True)
    currency = db.Column(db.String(12), nullable=True)
    initialResponse = db.Column(db.Integer, nullable=True)
    finalResponse = db.Column(db.Integer, nullable=True)
    category_id = db.Column(db.Integer, db.ForeignKey('suppcategory.id'), nullable=True)
    contacts = db.relationship('SuppContact', backref='supplier', lazy=True)
    certifications = db.relationship('SuppCertification', backref='supplier', lazy=True)
    qualityMans = db.relationship('QualityManual', backref='supplier', lazy=True)
    suppusers = db.relationship('SuppUser', backref='supplier', lazy=True)
    vis_vis = db.relationship('VisAVis', backref='supplier', lazy=True)
    suppCosts = db.relationship('SuppCosts', backref='supplier', lazy=True)
    complaints = db.relationship('ComplaintTable', backref='supplier', lazy=True)

    def __repr__(self):
        return f"{self.name}"

########################### suppcategory #############################

class SuppCategory(db.Model):
    __tablename__= "suppcategory"
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(60), unique=True, nullable=False )
    suppliers = db.relationship('Supplier', backref='suppcategory', lazy=True)

    def __repr__(self):
        return f"{self.name}"

########################### suppcontact #############################

class SuppContact(db.Model):
    __tablename__= "suppcontact"
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    firstName = db.Column(db.String(60), unique=False, nullable=False )
    lastName = db.Column(db.String(60), unique=False, nullable=False )
    email = db.Column(db.String(120), unique=True, nullable=False )
    phone = db.Column(db.String(20), nullable=True)
    function = db.Column(db.String(60), nullable=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey('supplier.id'), nullable=True)

    def __repr__(self):
        return f"{self.firstName} {self.lastName}"

########################### suppcertification #############################

class SuppCertification(db.Model):
    __tablename__= "suppcertification"
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(60), nullable=True)
    expirationDate = db.Column(db.DateTime(timezone=False), nullable=True)
    status = db.Column(db.String(12), nullable=True)
    attachement = db.Column(db.String(200), nullable=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey('supplier.id'), nullable=True)
    certificationType_id = db.Column(db.Integer, db.ForeignKey('certificationtype.id'), nullable=True)

    def __repr__(self):
        return f"{self.name}"

########################### certificationtype #############################

class CertificationType(db.Model):
    __tablename__= "certificationtype"
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(60), unique=True, nullable=True)
    description = db.Column(db.String(100), nullable=True)
    certifications = db.relationship('SuppCertification', backref='certificationtype', lazy=True)

    def __repr__(self):
        return f"{self.name}"

########################### qualitymanual #############################

class QualityManual(db.Model):
    __tablename__= "qualitymanual"
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(60), nullable=True)
    status = db.Column(db.String(12), nullable=True)
    attachement = db.Column(db.String(200), nullable=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey('supplier.id'), nullable=True)

    def __repr__(self):
        return f"{self.name}"

########################### documenttype #############################

class DocumentType(db.Model):
    __tablename__= "documenttype"
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(60), unique=True, nullable=True)
    vis_vis = db.relationship('VisAVis', backref='documenttype', lazy=True)

    def __repr__(self):
        return f"{self.name}"

########################### visavis #############################

class VisAVis(db.Model):
    __tablename__= "visavis"
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    supplier_id = db.Column(db.Integer, db.ForeignKey('supplier.id'), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    doctype_id = db.Column(db.Integer, db.ForeignKey('documenttype.id'), nullable=True)

########################### suppcosts #############################

class SuppCosts(db.Model):
    __tablename__= "suppcosts"
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    supplier_id = db.Column(db.Integer, db.ForeignKey('supplier.id'), nullable=True)
    costtype_id = db.Column(db.Integer, db.ForeignKey('costtype.id'), nullable=True)
    unitcost = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f"{self.unitcost}"

########################### costtype #############################

class CostType(db.Model):
    __tablename__= "costtype"
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    code = db.Column(db.String(60), unique=True, nullable=True)
    description = db.Column(db.String(100), nullable=True)
    unit = db.Column(db.String(20), nullable=True)
    suppCosts = db.relationship('SuppCosts', backref='costtype', lazy=True)
    costLines = db.relationship('CostDeclarationLine', backref='costtype', lazy=True)

    def __repr__(self):
        return f"{self.description}"

########################### costdeclarationline #############################

class CostDeclarationLine(db.Model):
    __tablename__= "costdeclarationline"
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    hoursNumber = db.Column(db.Float, nullable=False)
    unitcost = db.Column(db.Float, nullable=False)
    othercost = db.Column(db.Float, nullable=False)
    coefficient = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(20), nullable=True)
    lineCost = db.Column(db.Float, nullable=True)
    lineComment = db.Column(db.String(200), nullable=True)
    costtype_id = db.Column(db.Integer, db.ForeignKey('costtype.id'), nullable=True)
    costtable_id = db.Column(db.Integer, db.ForeignKey('costdeclarationtable.id'), nullable=True)

    def __repr__(self):
        return f"{self.lineCost}"

########################### costdeclarationtable #############################

class CostDeclarationTable(db.Model):
    __tablename__= "costdeclarationtable"
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    number = db.Column(db.String(60), unique=True, nullable=True)
    creationDate = db.Column(db.DateTime(timezone=False), nullable=True)
    totalCost = db.Column(db.Float, nullable=True)
    currency = db.Column(db.String(20), nullable=True)
    status = db.Column(db.String(20), nullable=True)
    paymentMethod = db.Column(db.String(30), nullable=True)
    paymentNumber = db.Column(db.String(30), unique=True, nullable=True)
    billNumber = db.Column(db.String(30), unique=True, nullable=True)
    comment = db.Column(db.String(200), nullable=True)
    costLines = db.relationship('CostDeclarationLine', backref='costdeclarationtable', lazy=True)
    complaint = db.relationship('ComplaintTable', uselist=False, backref='costdeclarationtable')

    def __repr__(self):
        return f"{self.totalCost}"

########################### complainttable #############################

class ComplaintTable(db.Model):
    __tablename__= "complainttable"
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    number = db.Column(db.String(60), unique=True, nullable=True)
    date = db.Column(db.DateTime(timezone=False), nullable=True)
    deliveryForm = db.Column(db.String(100), nullable=True)
    suspectQuantity = db.Column(db.Integer, nullable=True)
    detectionZone = db.Column(db.String(20), nullable=True)
    problemDescription = db.Column(db.String(250), nullable=True)
    verificationMethod = db.Column(db.String(100), nullable=True)
    status = db.Column(db.String(20), nullable=True)
    initialResponseDate = db.Column(db.DateTime(timezone=False), nullable=True)
    finalResponseDate = db.Column(db.DateTime(timezone=False), nullable=True)
    submissionDate = db.Column(db.DateTime(timezone=False), nullable=True)
    date3D = db.Column(db.DateTime(timezone=False), nullable=True)
    date5D = db.Column(db.DateTime(timezone=False), nullable=True)
    date8D = db.Column(db.DateTime(timezone=False), nullable=True)
    attachements = db.relationship('ComplaintAttachement', backref='complainttable', lazy=True)
    sysuser_id = db.Column(db.Integer, db.ForeignKey('sysuser.id'), nullable=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey('supplier.id'), nullable=True)
    costtable_id = db.Column(db.Integer, db.ForeignKey('costdeclarationtable.id'), nullable=True)
    article_id = db.Column(db.Integer, db.ForeignKey('article.id'), nullable=True)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=True)
    report8D_id = db.Column(db.Integer, db.ForeignKey('report8D.id'), nullable=True)

    def __repr__(self):
        return f"{self.number}"

########################### complaintattachement #############################

class ComplaintAttachement(db.Model):
    __tablename__= "complaintattachement"
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(60), unique=True, nullable=True)
    complaint_id = db.Column(db.Integer, db.ForeignKey('complainttable.id'), nullable=True)

    def __repr__(self):
        return f"{self.name}"

########################### article #############################

class Article(db.Model):
    __tablename__= "article"
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    internaltCode = db.Column(db.String(100), unique=True, nullable=True)
    externaltCode = db.Column(db.String(100), nullable=True)
    designation = db.Column(db.String(100), nullable=True)
    complaints = db.relationship('ComplaintTable', backref='article', lazy=True)

    def __repr__(self):
        return f"{self.designation}"

########################### client #############################

class Client(db.Model):
    __tablename__= "client"
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    code = db.Column(db.String(100), unique=True, nullable=True)
    name = db.Column(db.String(100), nullable=True)
    adresse = db.Column(db.String(100), nullable=True)
    complaints = db.relationship('ComplaintTable', backref='client', lazy=True)

    def __repr__(self):
        return f"{self.name}"

########################### project #############################

class Project(db.Model):
    __tablename__= "project"
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    code = db.Column(db.String(100), unique=True, nullable=True)
    name = db.Column(db.String(100), nullable=True)
    complaints = db.relationship('ComplaintTable', backref='project', lazy=True)

    def __repr__(self):
        return f"{self.name}"

########################### report8D #############################

class Report8D(db.Model):
    __tablename__= "report8D"
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    problemDescription = db.Column(db.String(250), nullable=True)
    startDate = db.Column(db.DateTime(timezone=False), nullable=True)
    contact = db.Column(db.String(250), nullable=True)
    deadLine = db.Column(db.DateTime(timezone=False), nullable=True)
    closed = db.Column(db.Boolean, nullable=True)
    closeDate = db.Column(db.DateTime(timezone=False), nullable=True)
    attachements = db.relationship('Attachement8D', backref='report8D', lazy=True)
    complaint = db.relationship('ComplaintTable', uselist=False, backref='report8D')
    teams = db.relationship('Team', backref='report8D', lazy=True)
    actions = db.relationship('Action', backref='report8D', lazy=True)
    causes = db.relationship('RootCause', backref='report8D', lazy=True)

    def __repr__(self):
        return f"{self.problemDescription}"

########################### attachement8D #############################

class Attachement8D(db.Model):
    __tablename__= "attachement8D"
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(60), unique=True, nullable=True)
    report8D_id = db.Column(db.Integer, db.ForeignKey('report8D.id'), nullable=True)

    def __repr__(self):
        return f"{self.path}"

########################### team #############################

class Team(db.Model):
    __tablename__= "team"
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    firstName = db.Column(db.String(30), nullable=True)
    lastName = db.Column(db.String(30), nullable=True)
    function = db.Column(db.String(60), nullable=True)
    report8D_id = db.Column(db.Integer, db.ForeignKey('report8D.id'), nullable=True)

    def __repr__(self):
        return f"{self.name}"

########################### action #############################

class Action(db.Model):
    __tablename__= "action"
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    description = db.Column(db.String(250), nullable=True)
    type = db.Column(db.String(20), nullable=True)
    type5D = db.Column(db.String(20), nullable=True)
    owner = db.Column(db.String(60), nullable=True)
    date = db.Column(db.DateTime(timezone=False), nullable=True)
    done = db.Column(db.Boolean, nullable=True)
    verified = db.Column(db.Boolean, nullable=True)
    verifiedDate = db.Column(db.DateTime(timezone=False), nullable=True)
    verifiedBy = db.Column(db.String(60), nullable=True)
    report8D_id = db.Column(db.Integer, db.ForeignKey('report8D.id'), nullable=True)

    def __repr__(self):
        return f"{self.description}"

########################### rootcause #############################

class RootCause(db.Model):
    __tablename__= "rootcause"
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    description = db.Column(db.String(250), nullable=True)
    verified = db.Column(db.Boolean, nullable=True)
    verifiedDate = db.Column(db.DateTime(timezone=False), nullable=True)
    verifiedBy = db.Column(db.String(60), nullable=True)
    report8D_id = db.Column(db.Integer, db.ForeignKey('report8D.id'), nullable=True)

    def __repr__(self):
        return f"{self.description}"





## DEV 
renew = False

if renew: 
    #db.drop_all()
    #db.create_all()
    #db.session.commit()
    print("Database has been sucessfully created")
    email = "admin@gmail.com"
    password = '123456'
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    
    admin_account = User(firstName="TEST",lastName="Test2", email=email,password=hashed_password)
    db.session.add(admin_account)
    db.session.commit()

    print("Connect using Email: {}, Password: {}",email,password)