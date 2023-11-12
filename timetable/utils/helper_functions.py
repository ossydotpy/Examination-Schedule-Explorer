import csv
from timetable import db, app
from timetable.models import Exam
from datetime import datetime


def process_csv_file(file):
    try:
        with file.stream as csvfile:
            content = csvfile.read().decode('utf-8-sig').splitlines()
            reader = csv.reader(content, delimiter=',', quotechar='"')

            with app.app_context():
                db.session.query(Exam).delete()

                header = next(reader)
                for row in reader:
                    exam_data = dict(zip(header, row))

                    # Convert '0' and '1' to boolean values
                    exam_data['is_faculty_wide'] = bool(int(exam_data['is_faculty_wide']))

                    exam = Exam(
                        exam_id=exam_data['exam_id'],
                        exam_name=exam_data['exam_name'],
                        Date=exam_data['Date'],
                        Day=exam_data['Day'],
                        Start=exam_data['Start'],
                        End=exam_data['End'],
                        Room=exam_data['Room'],
                        Capacity=exam_data['Capacity'],
                        Instructor=exam_data['Instructor'],
                        Student_Conflict=exam_data['Student_Conflict'],
                        Instructor_Conflict=exam_data['Instructor_Conflict'],
                        is_faculty_wide=exam_data['is_faculty_wide']
                    )
                    db.session.add(exam)

                db.session.commit()
                return True

    except Exception as e:
        app.logger.error(f'Error committing to the database: {str(e)}')
        return False


def process_exam_datetime(exam):
    """
    Process the datetime attributes of an Exam object.

    Args:
        exam (Exam): The Exam object to process.
    """
    exam.Date = datetime.strptime(exam.Date, '%d-%b-%y').date()
    exam.Start = datetime.strptime(exam.Start, "%I:%M %p").time()
    exam.End = datetime.strptime(exam.End, "%I:%M %p").time()


def calculate_time_left(exam):
    """
    Calculate the time left for an exam.

    Args:
        exam (Exam): The Exam object.

    Returns:
        time: The current time.
    """
    exam_datetime = datetime.combine(exam.Date, exam.Start)
    time_left = exam_datetime - datetime.now()

    days_left = time_left.days
    seconds_left = time_left.seconds
    hours_left = seconds_left // 3600
    minutes_left = (seconds_left % 3600) // 60

    exam.time_left = f"{days_left} days, {hours_left} hours, {minutes_left} minutes left"
    now = datetime.now().time()

    return now
