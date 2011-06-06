from flask import Flask, Response, request
from flaskext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bus.db'
db = SQLAlchemy(app)



