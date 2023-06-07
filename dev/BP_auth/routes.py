from flask import render_template, g, url_for, request, flash, Markup,  redirect, jsonify, abort, Blueprint, request, current_app
from flask_login import login_user, current_user, logout_user, login_required
from dev import db, bcrypt, app
from dev.models import *
from dev.BP_auth.forms import LoginForm
#from dev.BP_auth.utils import save_picture, senEmail, send_mail, send_reset_email
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadTimeSignature
from flask_babel import Babel, format_date, gettext
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from dev.BP_auth.utils import *
#from dev.flaskadmin import *
import traceback

auth = Blueprint('auth', __name__)

s=URLSafeTimedSerializer(app.config['SECRET_KEY'])


@auth.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    
    if current_user.is_authenticated:
        return redirect(url_for('admin.index'))
    
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user,remember=form.remember.data)
            return redirect(url_for('admin.index'))
        else:
            flash('Échec de la connexion!', 'danger')
    
    myDict = {
        'form' : form,
        'legend' : gettext("Interface d'authentification"),
        'menu' : {},
        'title' : 'Login Interface',
    }
    return render_template('authentification/login.html', myDict=myDict)

@auth.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('auth.login'))