import os
import secrets
from PIL import Image
from flask import url_for, current_app, render_template
from flask_mail import Message, Mail
from dev import mail, app
from threading import Thread
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadTimeSignature

s=URLSafeTimedSerializer(app.config['SECRET_KEY'])
mail = Mail(app)

def send_mail(email):

    msg = Message('Inscription à ADEX', sender='riabimoutii@hotmail.fr', recipients=[email])
    link = url_for('auth.login',_external=True)
    msg.body = 'Bienvenue à la plateforme des échanges des documents administratif "ADEX". votre mot de passe : 123456 vous pouvez acceder à la plateforme via ce lien {}' .format(link)
    mail.send(msg)