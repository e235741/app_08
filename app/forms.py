from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, BooleanField, SubmitField, SelectField, DateField
from wtforms.validators import DataRequired, NumberRange

class HomeworkForm(FlaskForm):
    contest = StringField('課題内容', validators=[DataRequired(message='課題内容を入力してください')])
    day = DateField('提出日', validators=[DataRequired('提出日は必須入力です')], format="%Y-%m-%d", render_kw={"placeholder": "yyyy/mm/dd"})
    hour = SelectField('時', choices=[(str(h), f'{h:02}') for h in range(24)], validators=[DataRequired()])
    minute = SelectField('分', choices=[(str(m), f'{m:02}') for m in range(0, 60, 1)], validators=[DataRequired()])
    once_a_week = BooleanField('週に一度')
    submit = SubmitField('追加')

class LessonForm(FlaskForm):
    name = StringField('授業名', validators=[DataRequired()])
    number_absence = IntegerField('欠席数', validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField('追加')

