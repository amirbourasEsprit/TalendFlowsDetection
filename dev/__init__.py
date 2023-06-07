# -*- coding: utf-8 -*-
from flask import Flask, g, request, redirect, url_for, session
from flask_login import current_user
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_mail import Mail, Message
from flask_login import LoginManager
from flask_babel import Babel, format_date, gettext
from datetime import datetime, timedelta
from flask_qrcode import QRcode
from flask_compress import Compress

#basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
#FILE_DIR = os.path.dirname(os.path.abspath(__file__))

app.config.from_pyfile('../../config.cfg')
Compress(app)

db = SQLAlchemy(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
mail = Mail(app)
# Initialize Flask-Babel
babel = Babel(app)


#qrcode = QRcode(app)

@babel.localeselector
def get_locale():
    return 'fr'

@app.before_request
def before_request():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=30)
    session.modified = True
    g.user = current_user


login_manager = LoginManager(app)
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'

from dev.BP_auth.routes import auth
from dev.BP_admin.routes import admin
from dev.BP_supplier.routes import supp
from dev.BP_cost.routes import cost
from dev.BP_complaint.routes import comp
app.register_blueprint(auth)
app.register_blueprint(admin)
app.register_blueprint(supp)
app.register_blueprint(cost)
app.register_blueprint(comp)

#app.register_blueprint(api, url_prefix='/api/v1/')