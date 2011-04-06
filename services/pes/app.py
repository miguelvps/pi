from flask import Flask
from flaskext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pes.db'
db = SQLAlchemy(app)

if __name__ == "__main__":
    app.run(debug=True)
