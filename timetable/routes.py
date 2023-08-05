from flask import render_template
from timetable import app, db
from timetable.forms import LevelProgramForm
from timetable.models import Program, Exam


@app.route('/', methods=["GET", 'POST'])
def index():
    form = LevelProgramForm()
    return render_template('index.html', form=form)


@app.route('/results', methods=['GET', 'POST'])
def results_page():
    programs = db.session.query(Program).all()
    return render_template('results.html', programs=programs)
