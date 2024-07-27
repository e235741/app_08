import os
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from forms import TaskInfoForm, LessonInfoForm

app = Flask(__name__)

app.config['SECRET_KEY'] = os.urandom(24)
base_dir = os.path.dirname(__file__)
database = 'sqlite:///' + os.path.join(base_dir, 'data.sqlite')
app.config['SQLALCHEMY_DATABASE_URI'] = database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
Migrate(app, db)

class Task(db.Model):
    __tablename__ = 'tasks'
    homework_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    content = db.Column(db.String(120))
    submission = db.Column(db.Integer)
    limit_time = db.Column(db.String(120))
    once_a_week = db.Column(db.Boolean)
    is_completed = db.Column(db.Boolean, default=False)
    

    # def __str__(self):
    #     return f'課題ID：{self.id} 内容：{self.content}'
class Lesson(db.Model):
    __tablename__ = 'lesson'
    lesson_id = db.Column(db.Integer, primary_key=True,  autoincrement=True)
    name = db.Column(db.String(120))
    number_absence = db.Column(db.Integer)


@app.route('/')
def index():
    uncompleted_tasks = Task.query.filter_by(is_completed=False).all()
    completed_tasks = Task.query.filter_by(is_completed=True).all()
    lessons = Lesson.query.all()  # 授業情報を取得
    return render_template('index.html', uncompleted_tasks=uncompleted_tasks, completed_tasks=completed_tasks, lessons=lessons)

@app.route('/new_task', methods=['GET', 'POST'])
def new_task():
    form = TaskInfoForm(request.form)
    if request.method == 'POST' and form.validate():
        limit_time = f"{form.day.data}:{form.hour.data}:{form.minute.data}"
        task = Task(
            content=form.content.data,
            limit_time=limit_time,
            submission=form.submission.data,
            once_a_week=form.once_a_week.data
        )
        db.session.add(task)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('new_task.html', form=form)

@app.route('/new_lesson', methods=['GET', 'POST'])
def new_lesson():
    form = LessonInfoForm(request.form)
    if request.method == 'POST' and form.validate():
        lesson = Lesson(
            name=form.name.data,
            number_absence=form.number_absence.data
        )
        db.session.add(lesson)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('new_lesson.html', form=form)

@app.route('/tasks/<int:task_id>/complete', methods=['POST'])
def complete_task(task_id):
    task = Task.query.get(task_id)
    task.is_completed = True
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/tasks/<int:task_id>/uncomplete', methods=['POST'])
def uncomplete_task(task_id):
    task = Task.query.get(task_id)
    task.is_completed = False
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/tasks/<int:task_id>/delete', methods=['POST'])
def delete_task(task_id):
    task = Task.query.get(task_id)
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/tasks/<int:task_id>/update', methods=['GET', 'POST'])
def update_task(task_id):
    task = Task.query.get(task_id)
    if not task:
        return redirect(url_for('index'))
    
    form = TaskInfoForm(request.form)
    if request.method == 'POST' and form.validate():
        task.content = form.content.data
        task.submission = form.submission.data
        task.limit_time = f"{form.day.data}:{form.hour.data}:{form.minute.data}"
        task.once_a_week = form.once_a_week.data
        db.session.commit()
        return redirect(url_for('index'))
    else:
        # GETリクエストの場合、フォームに初期値を設定
        limit_date, limit_hour, limit_minute = task.limit_time.split(':')
        form.content.data = task.content
        form.submission.data = task.submission
        form.day.data = limit_date
        form.hour.data = limit_hour
        form.minute.data = limit_minute
        form.once_a_week.data = task.once_a_week

    return render_template('update_task.html', form=form, task=task)
if __name__ == '__main__':
    app.run(debug=True)