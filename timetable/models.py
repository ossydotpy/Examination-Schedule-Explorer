import app
from timetable import db

exam_program_association = db.Table('exam_program_association',
                                    db.Column('exam_id', db.Integer, db.ForeignKey('exam.exam_id'), primary_key=True),
                                    db.Column('program_id', db.Integer, db.ForeignKey('program.program_id'),
                                              primary_key=True)
                                    )

program_relationship = db.Table(
    'program_relationship',
    db.Column('major_id', db.Integer, db.ForeignKey('program.program_id'), primary_key=True),
    db.Column('minor_id', db.Integer, db.ForeignKey('program.program_id'), primary_key=True)
)


class Program(db.Model):
    program_id = db.Column(db.Integer, primary_key=True)
    program_name = db.Column(db.String(length=60), unique=True)
    program_short_name = db.Column(db.String(length=10), unique=True)

    examinations = db.relationship('Exam', secondary=exam_program_association, back_populates='programs')

    majors = db.relationship(
        'Program',
        secondary=program_relationship,
        primaryjoin=(program_relationship.c.major_id == program_id),
        secondaryjoin=(program_relationship.c.minor_id == program_id),
        backref=db.backref('minors', lazy='dynamic'),
        lazy='dynamic'
    )

    def __repr__(self):
        return f'{self.program_name} ({self.program_short_name})'


class Exam(db.Model):
    exam_id = db.Column(db.Integer, primary_key=True)
    exam_name = db.Column(db.String(length=30))
    Date = db.Column(db.String(length=30), nullable=False)
    Day = db.Column(db.String(length=30), nullable=False)
    Start = db.Column(db.String(length=30), nullable=False)
    End = db.Column(db.String(length=30), nullable=False)
    Room = db.Column(db.String(length=1024), nullable=True)
    Capacity = db.Column(db.Integer, nullable=True)
    Instructor = db.Column(db.String(length=30), nullable=True)
    Student_Conflict = db.Column(db.String(length=30), nullable=True)
    Instructor_Conflict = db.Column(db.String(length=30), nullable=True)
    is_faculty_wide = db.Column(db.Boolean, default=False)

    programs = db.relationship('Program', secondary=exam_program_association, back_populates='examinations')

    def __repr__(self):
        return f'{self.exam_name}'

