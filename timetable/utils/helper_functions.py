import csv
import openpyxl
from datetime import date, datetime, timedelta

import pandas as pd

from timetable import db, app
from timetable.models import Exam


def format_time(time_str):
    """
    Function to format time from '3:30a' or '3:30p'.
    """
    time_str = time_str.strip()
    try:
        if time_str.endswith('a'):
            dt = datetime.strptime(time_str[:-1], '%I:%M')
        elif time_str.endswith('p'):
            dt = datetime.strptime(time_str[:-1], '%I:%M') + timedelta(hours=12)
        else:
            raise ValueError
    except ValueError:
        app.logger.error(f"Error: Invalid time format for '{time_str}'. Skipping...")
        return None
    return dt.strftime('%I:%M %p')


def process_raw_data(raw_file):
    try:
        df = pd.read_csv(raw_file)
    except FileNotFoundError:
        app.logger.error(f"Error: File '{raw_file}' not found.")
        exit()
    except (pd.errors.ParserError, UnicodeDecodeError):
        try:
            df = pd.read_excel(raw_file)
        except FileNotFoundError:
            app.logger.error(f"Error: File '{raw_file}' not found.")
            return
        except Exception as e:
            app.logger.error(f"Error: Unable to read file '{raw_file}': {e}")
            return

    try:
        df = df.rename(columns={'Examination': 'exam_name', 'Date': 'Date', 'Day': 'Day',
                                'Room': 'Room', 'Capacity': 'Capacity', ' Instructor': 'Instructor',
                                ' Student\nConflicts': 'Student_Conflict',
                                ' Instructor\nConflicts': 'Instructor_Conflict'})
    except KeyError as e:
        app.logger.error(f"Error: Column '{e.args[0]}' not found in the data file.")

    df[["Start", "End"]] = df["Time"].str.split(' - ', expand=True)
    df['Start'] = df['Start'].apply(format_time)
    df['End'] = df['End'].apply(format_time)
    df = df.sort_values(by=['Date', 'Start'])
    df['is_faculty_wide'] = 0

    df.drop(columns=['Enrollment', 'Seating\nType', 'Time'], inplace=True)

    cols = ['exam_name', 'Date', 'Day', 'Start', 'End', 'Room', 'Capacity', 'Instructor',
            'Student_Conflict', 'Instructor_Conflict', 'is_faculty_wide']
    df = df.reindex(columns=cols)

    return df


def process_clean_data(df):
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input data must be a pandas DataFrame.")
    df = df.map(str)
    with app.app_context():
        db.session.query(Exam).delete()

        for index, row in df.iterrows():
            exam_data = row.to_dict()

            # Convert '0' and '1' to boolean values if applicable
            if exam_data['is_faculty_wide'] in ['0', '1']:
                exam_data['is_faculty_wide'] = bool(int(exam_data['is_faculty_wide']))
            exam = Exam(**exam_data)
            db.session.add(exam)

        db.session.commit()
        return True


def process_exam_datetime(exam):
    """
    Process the datetime attributes of an Exam object.

    Args:
        exam (Exam): The Exam object to process.
    """
    exam.Date = datetime.strptime(exam.Date, '%d-%b-%y')
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

