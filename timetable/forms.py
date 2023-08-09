from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField
from wtforms.validators import DataRequired, ValidationError
from timetable.models import Program
from timetable import app


class LevelProgramForm(FlaskForm):
    def validate_major(self, field):
        if field.data == self.minor.data:
            raise ValidationError("You cant have the same program as Major and Minor")

    with app.app_context():
        all_programs = Program.query.all()

    levels = [('', 'Select a level'), ('1', 'Level 100'), ('2', 'Level 200'), ('3', 'Level 300'), ('4', 'Level 400')]
    programs = [(program.program_short_name, program.program_name) for program in all_programs]
    programs.insert(0, ('', 'Select a program'))

    level = SelectField(label='Level: ', choices=levels, validators=[DataRequired()])
    major = SelectField(label='Major: ', choices=programs, validators=[DataRequired()])
    minor = SelectField(label='Minor: ', choices=programs, validators=[DataRequired()])
    submit = SubmitField()
