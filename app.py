from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import pandas as pd
from flask import Response
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import io
import numpy as np
from sklearn.metrics import r2_score
import pickle
from flask import request

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

@app.route('/')
def home_page():
    return "Nothing to do here"

@app.route('/gather')
def gather_data():
    def add_data(year, w, m, veg, vegan, h, waste):
        c = Consumption(year=year, week=w, meat=m, veggie=veg, vegan=vegan, headcount=h, waste=waste)
        db.session.add(c)
        db.session.commit()

    for year in range(2020, 2025):
        x1 = np.linspace(0, np.pi*3, 52)
        n = np.random.normal(scale=5, size=len(x1))
        meats = 800 + (100 * np.sin(x1) + n)
        vegans = 800 + (50 * np.sin(x1) + n)
        vegs = 800 + (25 * np.sin(x1) + n)
        headcount = meats+vegans+vegs
        weeks = range(52)
        for w, m, veg, vegan, h in zip(weeks, meats, vegs, vegans, headcount):
            add_data(int(year), int(w), int(m), int(veg), int(vegan), int(h), np.random.randint(3, 8))

    return "data added!"

@app.route('/plot')
def plot_png():
    def create_figure(xs, ys):
        fig = Figure()
        axis = fig.add_subplot(1, 1, 1)
        axis.plot(xs, ys)
        return fig
    
    year = request.args.get('year', default = 2024, type = int)
    food = request.args.get('food', default = 'meat', type = str)

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
    df = df[df['year'] == year]
    fig = create_figure(df['week'], df[food])
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')


@app.route('/train')
def train_model():
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
    x_train = df.loc[:200, 'week']
    x_test = df.loc[200:, 'week']

    y_train_meat = df.loc[:200, 'meat']
    y_test_meat = df.loc[200:, 'meat']

    y_train_veggie = df.loc[:200, 'veggie']
    y_test_veggie = df.loc[200:, 'veggie']

    y_train_vegan = df.loc[:200, 'vegan']
    y_test_vegan = df.loc[200:, 'vegan']

    y_train_headcount = df.loc[:200, 'headcount']
    y_test_headcount = df.loc[200:, 'headcount']

    my_meat_model = np.poly1d(np.polyfit(x_train, y_train_meat, 4))
    my_veggie_model = np.poly1d(np.polyfit(x_train, y_train_veggie, 4))
    my_vegan_model = np.poly1d(np.polyfit(x_train, y_train_vegan, 4))
    my_headcount_model = np.poly1d(np.polyfit(x_train, y_train_headcount, 4))

    meat_r2 = f'{round(r2_score(y_test_meat, my_meat_model(x_test))*100, 2)} %'
    veggie_r2 = f'{round(r2_score(y_test_veggie, my_veggie_model(x_test))*100, 2)} %'
    vegan_r2 = f'{round(r2_score(y_test_vegan, my_vegan_model(x_test))*100, 2)} %'
    headcount_r2 = f'{round(r2_score(y_test_headcount, my_headcount_model(x_test))*100, 2)} %'

    output = f'<ul><li>R2 for Meat = {meat_r2}</li><li>R2 for Vegetarian = {veggie_r2}</li><li>R2 for Vegan = {vegan_r2}</li><li>R2 for Headcount = {headcount_r2}</li></ul>'
    with open('./meat.pkl', 'wb') as handle:
        pickle.dump(meat_r2, handle, protocol=pickle.HIGHEST_PROTOCOL)
    with open('./veggie.pkl', 'wb') as handle:
        pickle.dump(veggie_r2, handle, protocol=pickle.HIGHEST_PROTOCOL)
    with open('./vegan.pkl', 'wb') as handle:
        pickle.dump(vegan_r2, handle, protocol=pickle.HIGHEST_PROTOCOL)
    with open('./headcount.pkl', 'wb') as handle:
        pickle.dump(headcount_r2, handle, protocol=pickle.HIGHEST_PROTOCOL)

    return output