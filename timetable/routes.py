from datetime import datetime, date, timedelta

from flask import render_template, request, redirect, url_for, flash
from markupsafe import escape, Markup

from timetable import app
from timetable.forms import LevelProgramForm, UploadForm
from timetable.models import Program, Exam
from .utils import process_csv_file, process_exam_datetime, calculate_time_left
from sqlalchemy import or_


today = date.today()
tomorrow = today + timedelta(days=1)


def today_tomorrow_exams(day: str):
    """
    Retrieve exams for today or tomorrow from the database.

    Args:
        day (str): 'today' or 'tomorrow'

    Returns:
        list: List of exams for the specified day.
    """
    with app.app_context():
        exams = Exam.query.all()
        for exam in exams:
            process_exam_datetime(exam)
        day_exams = {
            "today": list(filter(lambda x: x.Date == today, exams)),
            "tomorrow": list(filter(lambda x: x.Date == tomorrow, exams))
        }

    return day_exams[day]


today_exams = today_tomorrow_exams('today')
tomorrow_exams = today_tomorrow_exams('tomorrow')


@app.route('/', methods=["GET", 'POST'])
def index():
    """
    Handle requests to the index page.

    Returns:
        str: Rendered HTML template for the index page.
    """
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
    """
    Handle requests to the results page.

    Returns:
        str: Rendered HTML template for the results page.
    """
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
            process_exam_datetime(exam)
            calculate_time_left(exam)

        try:
            message = Markup('<p>You have selected the following Programs: Major: <strong>{}</strong></p>Minor: '
                             '<strong>{}</strong></p>Selected level: Level <strong>{}00</strong>')
            flash(message.format(major, minor, level), category='info')
        except Exception as e:
            message = "An error occurred: {}".format(e)
            flash(message, category='info')  # Flash the error message here

    return render_template('results.html', all_exams=combined, major=major, minor=minor,
                           today_date=today, now=datetime.now().time())


@app.route('/more_exams/<string:day>')
def more_exams(day):
    """
    Handle requests to the more_exams page.

    Args:
        day (str): 'today' or 'tomorrow'

    Returns:
        str: Rendered HTML template for the more_exams page.
    """
    day = escape(day)
    if day == 'today':
        additional_exams = today_exams
    elif day == 'tomorrow':
        additional_exams = tomorrow_exams
    else:
        flash('Invalid day!', category='danger')
        return redirect(url_for('index'))

    return render_template('more_exams.html', additional_exams=additional_exams,
                           today_date=today, day=day.title())


@app.route('/full_table', methods=['GET'])
def full_table():
    """
    Handle requests to the full_table page.

    Returns:
        str: Rendered HTML template for the full_table page.
    """
    with app.app_context():
        all_exams = Exam.query.all()

    for exam in all_exams:
        process_exam_datetime(exam)
        calculate_time_left(exam)

    flash('This page contains examinations for the entire faculty', category='info')
    return render_template('full_table.html', all_exams=all_exams, today_date=today, now=datetime.now().time())


@app.route('/settings', methods=['GET', 'POST'])
def settings():
    """
    Handle requests to the admin page. Used an obscure name so users don't wander there lol.

    Returns:
        str: Rendered HTML template for the settings page.
    """
    form = UploadForm()

    if request.method == 'POST' and form.validate_on_submit():
        try:
            file = form.csv_file.data

            if file and file.filename:
                if process_csv_file(file):
                    flash('CSV file uploaded and processed successfully!', 'success')
                else:
                    flash('Error updating the database. Please check the logs for more information.', 'danger')
            else:
                flash('No file uploaded. Please select a CSV file to upload.', 'danger')

        except Exception as e:
            app.logger.error(f'Error processing CSV file: {str(e)}')
            flash('Error processing CSV file. Please check the logs for more information.', 'danger')

        return redirect(url_for('settings'))

    return render_template('admin_dash.html', form=form)


@app.errorhandler(404)
def page_not_found(e):
    """
    Handle 404 errors.

    Args:
        e (Exception): The exception object.

    Returns:
        str: Rendered HTML template for the 404 error page.
    """
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    """
    Handle 500 errors.

    Args:
        e (Exception): The exception object.

    Returns:
        str: Rendered HTML template for the 500 error page.
    """
    return render_template('500.html'), 500