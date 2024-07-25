from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired

class HomeworkForm(FlaskForm):
    contest = StringField('Contest', validators=[DataRequired()])
    hour = SelectField('Hour', choices=[(str(h), f'{h:02}') for h in range(24)], validators=[DataRequired()])
    minute = SelectField('Minute', choices=[(str(m), f'{m:02}') for m in range(0, 60, 5)], validators=[DataRequired()])
    submission = StringField('Submission', validators=[DataRequired()])
    once_a_week = BooleanField('Once a Week')
    submit = SubmitField('Add Homework')

class LessonForm(FlaskForm):
    name = StringField('Lesson Name', validators=[DataRequired()])
    homework_num = IntegerField('Number of Homeworks', validators=[DataRequired()])
    number_absence = IntegerField('Number of Absences', validators=[DataRequired()])
    submit = SubmitField('Add Lesson')

