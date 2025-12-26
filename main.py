from flask import Flask, render_template, redirect, url_for, flash, request, session, send_file, jsonify
from  flask_bootstrap import Bootstrap5
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import os 
from dotenv import load_dotenv
from calls import get_infos ,search


load_dotenv()

app = Flask(__name__)
Bootstrap5(app)
app.config['SECRET_KEY']=os.environ.get('APP_KEY')

class InputCity(FlaskForm):
    city = StringField("", validators=[DataRequired()],render_kw={"placeholder": "Enter your city name"})
    submit = SubmitField("Explore data")

@app.route('/', methods=['GET', 'POST'])
def index():
    form = InputCity()
    results = search(form.city.data)

    if form.validate_on_submit():
       city = form.city.data
       return redirect(url_for('show_data', city=city ,results=results))

    return render_template('index.html', form=form, results=results)

@app.route('/data/<city>')
def show_data(city):
    name, iso, weather , air , mobility = get_infos(city.title())
   

    return render_template('data.html', city=name, iso=iso, weather=weather ,air=air, mobility=mobility)


if __name__=="__main__":
    app.run(debug=True)
