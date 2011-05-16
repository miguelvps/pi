from datetime import datetime, timedelta
from functools import wraps

from flask import Module, request, session, g, render_template, redirect, \
                  make_response, url_for
from flaskext.wtf import Form, TextField, PasswordField, BooleanField, \
                         Required, Length, EqualTo, ValidationError
from werkzeug import generate_password_hash, check_password_hash

from concierge import db

from sqlalchemy.orm import backref

auth = Module(__name__, 'auth')


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(256), unique=True)
    password = db.Column(db.String(54)) # enough for sha1$hash
    created = db.Column(db.DateTime, default=datetime.utcnow)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, username, password):
        self.username = username
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)


class HistoryEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created = db.Column(db.DateTime, default=datetime.utcnow)
    query = db.Column(db.String(50))

    user = db.relationship(User, backref=backref('user_history', order_by=created))



class RegisterForm(Form):
    username = TextField('Username', validators=[Required(),
                                                 Length(min=1, max=256)])
    password = PasswordField('Password', validators=[Required(),
                                                     EqualTo('confirm'),
                                                     Length(min=4, max=256)])
    confirm = PasswordField('Confirm Password', validators=[Required()])
    remember = BooleanField('Remember me')

    def validate_username(form, field):
        if User.query.filter_by(username=form.username.data).first():
            raise ValidationError('Username already in use')


class LoginForm(Form):
    username = TextField('Username', validators=[Required()])
    password = PasswordField('Password', validators=[Required()])
    remember = BooleanField('Remember me')


def requires_auth(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        if not session.get('auth') and not hasattr(g, 'user'):
            session['referrer'] = request.url
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorator


@auth.before_app_request
def before_request():
    if session.get('auth'):
        user = User.query.filter_by(username=session['username']).first()
        if user:
            g.user = user
        else:
            session.pop('auth', None)


@auth.after_app_request
def after_request(response):
    if hasattr(g, 'user'):
        if not request.cookies.get('online'):
            time = datetime.utcnow()
            response.set_cookie('online', value='1', max_age=None,
                                expires=time+timedelta(minutes=5))
            g.user.last_seen = datetime.utcnow()
            db.session.merge(g.user)
            db.session.commit()
    return response


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if form.validate_on_submit():
        user = User(form.username.data, form.password.data)
        db.session.add(user)
        db.session.commit()
        g.user = user
        session['id'] = user.id
        session['username'] = user.username
        session['auth'] = True
        session.permanent = form.remember.data
        referrer = session.pop('referrer', None)
        if referrer:
            return redirect(referrer)
        return redirect('/')
    return render_template('register.html', form=form)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            g.user = user
            session['id'] = user.id
            session['username'] = user.username
            session['auth'] = True
            session.permanent = form.remember.data
            referrer = session.pop('referrer', None)
            if referrer:
                return redirect(referrer)
            return redirect('/')

    form.username.data = session.get('username')
    return render_template('login.html', form=form)


@auth.route('/logout')
@requires_auth
def logout():
    session.pop('auth')
    response = make_response(redirect('/'))
    response.delete_cookie('online')
    return response
