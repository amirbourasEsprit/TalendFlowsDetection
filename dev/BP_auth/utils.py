import os
import secrets
from PIL import Image
from flask import url_for, current_app, render_template
from flask_mail import Message
from dev import mail, app
from threading import Thread


'''
def save_picture(form_picture,old_image):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.rotate(0).save(picture_path)
    #i.save(picture_path)
    if old_image != app.config['DEFAULT_PROFILE_IMAGE']:
        #'profile.png':
        picture_to_delete = os.path.join(app.root_path, 'static/profile_pics', old_image)
        os.remove(picture_to_delete)
    return picture_fn


def async_send_mail(app, msg):
    with app.app_context():
        mail.send(msg)
 
 
def send_mail(subject, recipient, template, **kwargs):
    msg = Message(subject, sender='regat.industrie@tunisia.gov.tn', recipients=[recipient], bcc=['regat.industrie@tunisia.gov.tn'])
    msg.html = render_template(template, **kwargs)
    thr = Thread(target=async_send_mail, args=[app, msg])
    thr.start()
    return thr


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request', sender='no-reply.industrie@tunisia.gov.tn', recipients=[user.email], bcc=['regat.industrie@tunisia.gov.tn'])
    msg.body = """
    To reset your password, visit the following link: {}
    If you did not make this request then simply ignore this email and no changes will be made.
    """.format(url_for('auth.Reset_token', token=token, _external=True))
    
    mail.send(msg)

def senEmail(v_subject, v_body, v_sender, v_recipients):
    #Message(subject, recipients, body, html, sender, cc, bcc, reply-to, date, charset, extra_headers, mail_options, rcpt_options)
    message = Message(v_subject, sender=v_sender, recipients=[v_recipients])
    message.body = v_body
    mail.send(message)
'''