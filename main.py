from flask import Flask, render_template, redirect, url_for, flash, request, session, send_file, jsonify
from  flask_bootstrap import Bootstrap5
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import os 
from dotenv import load_dotenv
from calls import get_infos ,search, overall_calc
import json


load_dotenv()

app = Flask(__name__)
Bootstrap5(app)
app.config['SECRET_KEY']=os.environ.get('APP_KEY')

class InputCity(FlaskForm):
    city = StringField("", validators=[DataRequired()],render_kw={"placeholder": "Enter your city name"})
    submit = SubmitField("Explore data")

@app.route('/',methods=["GET", "POST"])
def index():
    form = InputCity()
    return render_template('index.html', form=form)

@app.route('/data')
def show_data():
    lat = request.args.get("lat", type=float)
    lon = request.args.get("lon", type=float)
    bbox_raw = request.args.get("bbox")
    bbox = json.loads(bbox_raw)
    print(f"bounding box selected = {bbox}")

    if lat is None or lon is None:
        return redirect(url_for("index"))


    name, iso, weather, air, mobility = get_infos(lat, lon, bbox)

    overall_score, overall_label = overall_calc(weather, air, mobility)

    return render_template('data.html', city=name, iso=iso, weather=weather, air=air, mobility=mobility, overall_score=overall_score, overall_label=overall_label)

@app.route("/search",  methods=["GET"])
def search_city():
    q = request.args.get("q", "").strip()

    if len(q) < 2:
        return jsonify([])

    results = search(q)  # calls.py
    return jsonify(results)


@app.route("/about")
def about():
    return render_template('infos.html')

@app.route("/contact")
def contact():
    return render_template('contact.html')



if __name__=="__main__":
    app.run(debug=True)
