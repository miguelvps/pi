from datetime import datetime

from flask import Module, request, session, render_template, redirect
from flaskext.wtf import Form, TextField, PasswordField, Required, \
                         Length, EqualTo, ValidationError
from werkzeug import generate_password_hash, check_password_hash

from concierge import db


auth = Module(__name__, 'auth')


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(256), unique=True)
    password = db.Column(db.String(256))
    created = db.Column(db.DateTime)

    def __init__(self, username, password):
        self.username = username
        self.password = generate_password_hash(password)
        self.created = datetime.utcnow()

    def check_password(self, password):
        return check_password_hash(self.password, password)


class RegisterForm(Form):
    username = TextField('Username', validators=[Required(),
                                                 Length(min=1, max=256)])
    password = PasswordField('Password', validators=[Required(),
                                                     EqualTo('confirm'),
                                                     Length(min=4, max=256)])
    confirm = PasswordField('Confirm Password', validators=[Required()])

    def validate_username(form, field):
        if User.query.filter_by(username=form.username.data).first():
            raise ValidationError('Username already in use')


class LoginForm(Form):
    username = TextField('Username', validators=[Required()])
    password = PasswordField('Password', validators=[Required()])


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if form.validate_on_submit():
        db.session.add(User(form.username.data, form.password.data))
        db.session.commit()
        session['username'] = form.username.data
        session['auth'] = True        
        return redirect('/')
    return render_template('register.html', form=form)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        print user.username
        print user.password
        if user and user.check_password(form.password.data):
            session['username'] = form.username.data
            session['auth'] = True
            return redirect('/')
    return render_template('login.html', form=form)


@auth.route('/logout')
def logout():
    session.pop('auth', None)
    return redirect('/')


