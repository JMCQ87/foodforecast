from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///canteen.db'

db = SQLAlchemy(app)
migrate = Migrate(app, db)

class Consumption(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # Time
    year = db.Column(db.Integer, nullable=False)
    week = db.Column(db.Integer, nullable=False)

    # MEALS
    meat = db.Column(db.Integer)
    veggie = db.Column(db.Integer)
    vegan = db.Column(db.Integer)
    
    headcount = db.Column(db.Integer) # total number of employees that could have gotten a meal
    waste = db.Column(db.Integer) # the leftover trash