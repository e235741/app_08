from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_migrate import Migrate
from forms import HomeworkForm, LessonForm
import os

app = Flask(__name__)

# Flaskに対する設定
app.config['SECRET_KEY'] = os.urandom(24)
base_dir = os.path.dirname(__file__)
database = 'sqlite:///' + os.path.join(base_dir, 'data.sqlite')
app.config['SQLALCHEMY_DATABASE_URI'] = database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# SQLAlchemyとMigrateの設定
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class Homework(db.Model):
    __tablename__ = 'homework'
    homework_id = db.Column(db.Integer, primary_key=True)
    contest = db.Column(db.String(120))
    day_of_week = db.Column(db.String(120))
    limit_time = db.Column(db.String(120))
    submission = db.Column(db.Integer)
    once_a_week = db.Column(db.Boolean)

class Lesson(db.Model):
    __tablename__ = 'lesson'
    lesson_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    homework_name= db.Column(db.String(120))
    number_absence = db.Column(db.Integer)

class LessonHomework(db.Model):
    __tablename__ = 'lesson_homework'
    lesson_homework_id = db.Column(db.Integer, primary_key=True)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lesson.lesson_id'))
    homework_id = db.Column(db.Integer, db.ForeignKey('homework.homework_id'))

class Chart(db.Model):
    __tablename__ = 'chart'
    time_id = db.Column(db.Integer, primary_key=True)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lesson.lesson_id'), nullable=True)
    start_time = db.Column(db.String(120), nullable=True)
    finish_time = db.Column(db.String(120), nullable=True)
    day_of_week = db.Column(db.String(120))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/new_homework', methods=['GET', 'POST'])
def new_homework():
    form = HomeworkForm()
    if form.validate_on_submit():
        # hour と minute フィールドから limit_time を HH:MM 形式で作成
        limit_time = f"{form.hour.data}:{form.minute.data}"
        homework = Homework(
            contest=form.contest.data,
            limit_time=limit_time,  # 更新された limit_time を使用
            submission=form.submission.data,
            once_a_week=form.once_a_week.data
        )
        db.session.add(homework)
        db.session.commit()
        flash('Homework added successfully!')
        return redirect(url_for('index'))
    return render_template('new_homework.html', form=form)


@app.route('/new_lesson', methods=['GET', 'POST'])
def new_lesson():
    form = LessonForm()
    if form.validate_on_submit():
        lesson = Lesson(
            name=form.name.data,
            homework_num=form.homework_num.data,
            number_absence=form.number_absence.data
        )
        db.session.add(lesson)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('new_lesson.html', form=form)

@app.route('/lessons')
def lesson_list():
    lessons = Lesson.query.all()
    return render_template('lesson_list.html', lessons=lessons)

@app.route('/homeworks')
def homework_list():
    homeworks = Homework.query.all()
    return render_template('homework_list.html', homeworks=homeworks)

# 実行
if __name__ == '__main__':
    app.run(debug=True)
