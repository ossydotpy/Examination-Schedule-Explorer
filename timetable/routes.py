from datetime import datetime, date, timedelta

from flask import render_template, request, redirect, url_for, flash

from timetable import app, db
from timetable.forms import LevelProgramForm
from timetable.models import Program, Exam

today = date.today()
tomorrow = today + timedelta(days=1)


def today_tomorrow_exams(day: str):
    with app.app_context():
        exams = Exam.query.all()
        for exam in exams:
            exam.Date = datetime.strptime(exam.Date, '%d-%b-%y').date()
        day_exams = {
            "today": list(filter(lambda x: x.Date == today, exams)),
            "tomorrow": list(filter(lambda x: x.Date == tomorrow, exams))
        }

    return day_exams[day]


today_exams = today_tomorrow_exams('today')
tomorrow_exams = today_tomorrow_exams('tomorrow')


@app.route('/', methods=["GET", 'POST'])
def index():
    form = LevelProgramForm()
    level = form.level.data
    major = form.major.data
    minor = form.minor.data

    if form.validate_on_submit():
        return redirect(url_for('results_page', level=level, major=major, minor=minor))
    flash('You cant have the same program as both a major and minor', category='danger')

    return render_template('index.html', form=form, today_exams=today_exams, tomorrow_exams=tomorrow_exams)


@app.route('/results', methods=['GET', 'POST'])
def results_page():
    major_short_name = request.args.get('major')
    minor_short_name = request.args.get('minor')
    level = request.args.get('level')
    if minor_short_name == major_short_name:
        return redirect(url_for('index'))

    with app.app_context():
        major = Program.query.filter_by(program_short_name=major_short_name).first()
        minor = Program.query.filter_by(program_short_name=minor_short_name).first()

        all_major_exams = (
            db.session.query(Exam).filter(Exam.exam_name.contains(major_short_name)).all()
        )

        all_minor_exams = (
            db.session.query(Exam).filter(Exam.exam_name.contains(minor_short_name)).all()
        )

        today_date = datetime.today().date()

        for exam in all_major_exams:
            exam.Date = datetime.strptime(exam.Date, '%d-%b-%y').date()
            exam.days_left = (exam.Date - today_date).days

        for exam in all_minor_exams:
            exam.Date = datetime.strptime(exam.Date, '%d-%b-%y').date()
            exam.days_left = (exam.Date - today_date).days

        major_exams = [x for x in all_major_exams if x.exam_name.split(' ')[1][0] == level]
        minor_exams = [x for x in all_minor_exams if x.exam_name.split(' ')[1][0] == level]

    flash(f'Selected Programs:\nMajor: {major}\nMinor: {minor}', category='success')
    return render_template('results.html', major_exams=major_exams, minor_exams=minor_exams, major=major, minor=minor,
                           today_date=today_date)


@app.route('/more_exams/<string:day>')
def more_exams(day):
    additional_exams = []
    if day == 'today':
        additional_exams = today_exams
    if day == 'tomorrow':
        additional_exams = tomorrow_exams

    return render_template('more_exams.html', additional_exams=additional_exams,
                           today_date=today, day=day.title())
