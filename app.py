from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import pandas as pd
import matplotlib.pyplot as plt
from io import StringIO
# import StringIO
import base64
from flask import Response
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import io
import random
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

@app.route('/train')
def plot_png():
    table = db.session.query(Consumption).all()
    ids = []
    years = []
    weeks = []
    meats = []
    veggies = []
    vegans = []
    headcounts = []
    wastes = []

    for row in table:
        ids.append(row.id)
        years.append(row.year)
        weeks.append(row.week)
        meats.append(row.meat)
        veggies.append(row.veggie)
        vegans.append(row.vegan)
        headcounts.append(row.headcount)
        wastes.append(row.waste)
    df = pd.DataFrame(
        {
            "id": ids,
            "year": years,
            "week": weeks,
            "meat": meats,
            "veggie": veggies,
            "vegan": vegans,
            "headcount": headcounts,
            "waste": wastes
        }
    )
    fig = create_figure(df['week'], df['vegan'])
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')

def create_figure(xs, ys):
    fig = Figure()
    axis = fig.add_subplot(1, 1, 1)
    axis.plot(xs, ys)
    return fig