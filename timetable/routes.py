from datetime import datetime, date, timedelta

from flask import render_template, request, redirect, url_for, flash
from markupsafe import escape, Markup

from timetable import app, db
from timetable.forms import LevelProgramForm
from timetable.models import Program, Exam

from sqlalchemy import or_

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
    with app.app_context():
        all_programs = Program.query.all()
    programs = [(program.program_short_name, program.program_name) for program in all_programs]
    programs.insert(0, ('', 'Select a program'))

    form = LevelProgramForm()
    form.major.choices = programs
    form.minor.choices = programs

    level = form.level.data
    major = form.major.data
    minor = form.minor.data

    if form.validate_on_submit():
        return redirect(url_for('results_page', level=level, major=major, minor=minor))

    if request.method == 'POST':
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"{error}", category='danger')
    return render_template('index.html', form=form, today_exams=today_exams, tomorrow_exams=tomorrow_exams)


@app.route('/results', methods=['GET', 'POST'])
def results_page():
    try:
        major_short_name = request.args['major']
        minor_short_name = request.args['minor']
        level = request.args['level']
    except KeyError:
        flash('Invalid URL parameters. Please check the provided parameters.', category='danger')
        return redirect(url_for('index'))

    if minor_short_name == major_short_name:
        return redirect(url_for('index'))

    with app.app_context():
        try:
            major = Program.query.filter_by(program_short_name=major_short_name).first().program_name
            minor = Program.query.filter_by(program_short_name=minor_short_name).first().program_name
        except AttributeError:
            flash('Invalid selection. Please check the programs you chose.', category='danger')
            return redirect(url_for('index'))

        all_exams = Exam.query.filter(
            or_(
                Exam.exam_name.contains(major_short_name),
                Exam.exam_name.contains(minor_short_name),
                Exam.is_faculty_wide == True
            )
        ).all()
        combined = [x for x in all_exams if x.exam_name.split(' ')[1][0] == level]

        for exam in combined:
            exam.Date = datetime.strptime(exam.Date, '%d-%b-%y').date()
            exam.Start = datetime.strptime(exam.Start, "%I:%M %p").time()
            exam.End = datetime.strptime(exam.End, "%I:%M %p").time()

            exam_datetime = datetime.combine(exam.Date, exam.Start)
            time_left = exam_datetime - datetime.now()

            days_left = time_left.days
            seconds_left = time_left.seconds
            hours_left = seconds_left // 3600
            minutes_left = (seconds_left % 3600) // 60

            exam.time_left = f"{days_left} days, {hours_left} hours, {minutes_left} minutes left"
            now = datetime.now().time()

        try:
            message = Markup('<p>You have selected the following Programs: Major: <strong>{}</strong></p>Minor: '
                             '<strong>{}</strong></p>Selected level: Level <strong>{}00</strong>')
            flash(message.format(major, minor, level), category='info')
        except Exception as e:
            message = "An error occurred: {}".format(e)
            flash(message, category='info')  # Flash the error message here

    return render_template('results.html', all_exams=combined, major=major, minor=minor,
                           today_date=today, now=now)


@app.route('/more_exams/<string:day>')
def more_exams(day):
    day = escape(day)
    if day == 'today':
        additional_exams = today_exams
    elif day == 'tomorrow':
        additional_exams = tomorrow_exams
    else:
        flash('invalid day!', category='danger')
        return redirect(url_for('index'))

    return render_template('more_exams.html', additional_exams=additional_exams,
                           today_date=today, day=day.title())


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def page_not_found(e):
    return render_template('500.html'), 500
