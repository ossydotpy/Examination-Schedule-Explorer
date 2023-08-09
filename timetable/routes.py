from datetime import datetime, date, timedelta

from flask import render_template, request, redirect, url_for, flash
from markupsafe import escape, Markup

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

    if request.method == 'POST':
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"{error}", category='danger')
    return render_template('index.html', form=form, today_exams=today_exams, tomorrow_exams=tomorrow_exams)


@app.route('/results', methods=['GET', 'POST'])
def results_page():
    major_short_name = request.args.get('major')
    minor_short_name = request.args.get('minor')
    level = request.args.get('level')
    if minor_short_name == major_short_name:
        return redirect(url_for('index'))

    with app.app_context():
        major = Program.query.filter_by(program_short_name=major_short_name).first().program_name
        minor = Program.query.filter_by(program_short_name=minor_short_name).first().program_name

        all_major_exams = db.session.query(Exam).filter(Exam.exam_name.contains(major_short_name)).all()
        all_minor_exams = db.session.query(Exam).filter(Exam.exam_name.contains(minor_short_name)).all()

        def process_exams(exams):
            return [
                x for x in exams if x.exam_name.split(' ')[1][0] == level
            ]

        major_exams = process_exams(all_major_exams)
        minor_exams = process_exams(all_minor_exams)

        for exam in all_major_exams + all_minor_exams:
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
            message = Markup('<p>You have selected the following Programs: Major: <strong>{}</strong></p>Minor: '
                             '<strong>{}</strong></p>Selected level: Level <strong>{}</strong>00')
    flash(message.format(major, minor, level), category='info')
    return render_template('results.html', major_exams=major_exams, minor_exams=minor_exams, major=major, minor=minor,
                           today_date=today, now=now)


@app.route('/more_exams/<string:day>')
def more_exams(day):
    day = escape(day)
    additional_exams = []
    if day == 'today':
        additional_exams = today_exams
    if day == 'tomorrow':
        additional_exams = tomorrow_exams

    return render_template('more_exams.html', additional_exams=additional_exams,
                           today_date=today, day=day.title())
