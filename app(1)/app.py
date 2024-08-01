from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_migrate import Migrate
from forms import HomeworkForm, LessonForm
import os
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler

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
    limit_time = db.Column(db.String(120))
    submission = db.Column(db.Integer)
    once_a_week = db.Column(db.Boolean)

class Lesson(db.Model):
    __tablename__ = 'lesson'
    lesson_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    homework_name = db.Column(db.String(120), nullable=True)
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

def check_due_dates():
    with app.app_context():
        now = datetime.now()
        homeworks = Homework.query.filter(Homework.submission == 0).all()
        for homework in homeworks:
            limit_time = datetime.strptime(homework.limit_time, "%Y-%m-%d %H:%M")
            if now > limit_time:
                homework.submission = 3
                db.session.commit()

scheduler = BackgroundScheduler()
scheduler.add_job(func=check_due_dates, trigger="interval", minutes=1)
scheduler.start()

@app.teardown_appcontext
def shutdown_scheduler(exception=None):
    if scheduler.running:
        scheduler.shutdown(wait=False)

@app.route('/')
def index():
    uncompleted_homeworks = Homework.query.filter_by(submission=0).all()
    completed_homeworks = Homework.query.filter_by(submission=1).all()
    delay_homeworks = Homework.query.filter_by(submission=3).all()

    homework_lessons = db.session.query(Homework, Lesson).join(LessonHomework, Homework.homework_id == LessonHomework.homework_id).join(Lesson, LessonHomework.lesson_id == Lesson.lesson_id).all()

    return render_template('index.html', uncompleted_homeworks=uncompleted_homeworks, completed_homeworks=completed_homeworks, delay_homeworks=delay_homeworks, homework_lessons=homework_lessons)

@app.route('/new_homework')
def new_homework():
    one = Chart.query.filter(Chart.time_id.in_([1, 10, 19, 28, 37])).all()
    two = Chart.query.filter(Chart.time_id.in_([2, 11, 20, 29, 38])).all()
    three = Chart.query.filter(Chart.time_id.in_([3, 12, 21, 30, 39])).all()
    four = Chart.query.filter(Chart.time_id.in_([4, 13, 22, 31, 40])).all()
    five = Chart.query.filter(Chart.time_id.in_([5, 14, 23, 32, 41])).all()
    six = Chart.query.filter(Chart.time_id.in_([6, 15, 24, 33, 42])).all()
    seven = Chart.query.filter(Chart.time_id.in_([7, 16, 25, 34, 43])).all()
    eight = Chart.query.filter(Chart.time_id.in_([8, 17, 26, 35, 44])).all()
    nine = Chart.query.filter(Chart.time_id.in_([9, 18, 27, 36, 45])).all()
    lessons = {lesson.lesson_id: lesson.name for lesson in Lesson.query.all()}
    return render_template('new_homework.html', one=one, two=two, three=three, four=four, five=five, six=six, seven=seven, eight=eight, nine=nine, lessons=lessons)

@app.route('/new_lesson/<int:time_id>', methods=['GET', 'POST'], endpoint='create_lesson')
def new_lesson(time_id):
    form = LessonForm()
    if form.validate_on_submit():
        lesson = Lesson(
            name=form.name.data,
            number_absence=form.number_absence.data
        )
        db.session.add(lesson)
        db.session.commit()  # lesson_id を取得するためにコミット

        # 指定された time_id を持つ Chart インスタンスを取得
        chart = Chart.query.filter_by(time_id=time_id).first()
        if chart:
            chart.lesson_id = lesson.lesson_id
            db.session.commit()  # Chart インスタンスをデータベースにコミット

        flash('Lesson added successfully!', 'success')
        return redirect(url_for('index'))

    return render_template('new_lesson.html', form=form)

@app.route('/new_homework/<int:lesson_id>', methods=['GET', 'POST'])
def new_homework_with_lesson_id(lesson_id):
    form = HomeworkForm()
    if form.validate_on_submit():
        # hour と minute フィールドから limit_time を HH:MM 形式で作成
        limit_time = f"{form.day.data:%Y-%m-%d} {form.hour.data}:{form.minute.data}"
        homework = Homework(
            contest=form.contest.data,
            limit_time=limit_time,  # 更新された limit_time を使用
            submission=0,
            once_a_week=form.once_a_week.data
        )

        db.session.add(homework)
        db.session.commit()  # homework_id を取得するためにコミット

        lessonhomework = LessonHomework(
            lesson_id=lesson_id,
            homework_id=homework.homework_id
        )
        db.session.add(lessonhomework)
        db.session.commit()

        flash('Homework added successfully!', 'success')
        return redirect(url_for('index'))

    return render_template('new_homework_with_lesson_id.html', form=form, lesson_id=lesson_id)

@app.route('/homeworks/<int:homework_id>/complete', methods=['POST'])
def complete_homework(homework_id):
    homework = Homework.query.get(homework_id)
    homework.submission = 1
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/homeworks/<int:homework_id>/uncomplete', methods=['POST'])
def uncomplete_homework(homework_id):
    homework = Homework.query.get(homework_id)
    homework.submission = 0
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/homeworks/<int:homework_id>/delete', methods=['POST'])
def delete_homework(homework_id):
    homework = Homework.query.get(homework_id)
    db.session.delete(homework)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/homeworks/<int:homework_id>/update', methods=['GET', 'POST'])
def update_homework(homework_id):
    homework = Homework.query.get(homework_id)
    if not homework:
        return redirect(url_for('index'))

    form = HomeworkForm(request.form)
    if request.method == 'POST' and form.validate():
        homework.contest = form.contest.data
        homework.limit_time = f"{form.day.data:%Y-%m-%d} {form.hour.data}:{form.minute.data}"
        homework.once_a_week = form.once_a_week.data
        db.session.commit()
        return redirect(url_for('index'))
    else:
        # GETリクエストの場合、フォームに初期値を設定
        limit_date, limit_time = homework.limit_time.split(' ')
        limit_hour, limit_minute = limit_time.split(':')
        form.contest.data = homework.contest
        form.day.data = limit_date
        form.hour.data = limit_hour
        form.minute.data = limit_minute
        form.once_a_week.data = homework.once_a_week

    return render_template('update_homework.html', form=form, homework=homework)

# 実行
if __name__ == '__main__':
    app.run(debug=True)