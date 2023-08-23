from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField
from wtforms.validators import DataRequired, ValidationError


class LevelProgramForm(FlaskForm):

    levels = [('', 'Select a level'), ('1', 'Level 100'), ('2', 'Level 200'), ('3', 'Level 300'), ('4', 'Level 400')]
    level = SelectField(label='Level: ', choices=levels, validators=[DataRequired()])
    major = SelectField(label='Major: ', validators=[DataRequired()])
    minor = SelectField(label='Minor: ', validators=[DataRequired()])
    submit = SubmitField()

    def validate_minor(self, field):
        if field.data == self.major.data:
            raise ValidationError("You cant have the same program as Major and Minor")
