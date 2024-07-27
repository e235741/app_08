from wtforms import Form, StringField, DateField, SelectField, BooleanField, IntegerField
from wtforms.validators import DataRequired

class TaskInfoForm(Form):
    content = StringField(validators=[DataRequired(message='授業名を入力してください')])
    submission = StringField(validators=[DataRequired(message='課題内容を入力してください')])
    day = DateField(validators=[DataRequired('提出日は必須入力です')], 
                        format="%Y-%m-%d", render_kw={"placeholder": "yyyy/mm/dd"})
    hour = SelectField(choices=[(str(h), f'{h:02}') for h in range(24)], validators=[DataRequired()])
    minute = SelectField(choices=[(str(m), f'{m:02}') for m in range(0, 60, 5)], validators=[DataRequired()])
    once_a_week = BooleanField('Once a Week')

class LessonInfoForm(Form):
    name = StringField(validators=[DataRequired()])
    number_absence = IntegerField(validators=[DataRequired()])

