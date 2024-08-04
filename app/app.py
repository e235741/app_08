from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, request, redirect, url_for, flash, abort
from flask_migrate import Migrate
from forms import HomeworkForm, LessonForm
import os
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from linebot.v3 import (
    WebhookHandler
)
from linebot.v3.exceptions import (
    InvalidSignatureError
)
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent
)

app = Flask(__name__)

# Flaskに対する設定
app.config['SECRET_KEY'] = os.urandom(24)
base_dir = os.path.dirname(__file__)
database = 'sqlite:///' + os.path.join(base_dir, 'data.sqlite')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', database)
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

@app.before_request
def before_first_request():
    try:
        # 簡単なクエリを実行してデータベース接続を確認
        db.session.execute('SELECT 1')
        app.logger.info('Database connection successful.')
    except Exception as e:
        app.logger.error(f'Database connection failed: {e}')

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
    
    lessons = Lesson.query.all()

    return render_template('index.html', uncompleted_homeworks=uncompleted_homeworks, completed_homeworks=completed_homeworks, delay_homeworks=delay_homeworks, homework_lessons=homework_lessons, lessons=lessons)

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

# LINE Messaging APIのチャンネルアクセストークンとチャンネルシークレットを設定します
LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
LINE_CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET')

configuration = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

@app.route("/callback", methods=['POST'])
def callback():
    # リクエストヘッダーから署名を取得
    signature = request.headers['X-Line-Signature']
    # リクエストボディを取得
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    # 署名を検証し、問題がなければハンドラーに渡す
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        app.logger.error("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    app.logger.info(f"Received message: {event.message.text} from user: {event.source.user_id}")
    user_message = event.message.text.lower()
    now = datetime.now()
    current_time = now.time()
    current_weekday = now.weekday()
    app.logger.info(f"Current time: {current_time}, Current weekday: {current_weekday}")

    time_slots = [
        {"start": "08:30", "end": "10:00", "lesson_offset": 0},
        {"start": "10:20", "end": "11:50", "lesson_offset": 1},
        {"start": "12:50", "end": "14:20", "lesson_offset": 2},
        {"start": "14:40", "end": "16:10", "lesson_offset": 3},
        {"start": "16:20", "end": "17:50", "lesson_offset": 4}
    ]

    reply_message = "時間外です"
    for slot in time_slots:
        start_time = datetime.strptime(slot["start"], "%H:%M").time()
        end_time = datetime.strptime(slot["end"], "%H:%M").time()
        app.logger.info(f"Checking time slot: {slot['start']} - {slot['end']}")
        if start_time <= current_time <= end_time:
            app.logger.info("Current time is within this slot")
            lesson = Chart.query.filter(Chart.time_id == (1 + slot["lesson_offset"] + current_weekday * 9)).first()
            if lesson:
                app.logger.info("Lesson found in database")
                if user_message == "出席":
                    reply_message = "出席が確認されました"
                else:
                    lesson_instance = Lesson.query.get(lesson.lesson_id)
                    lesson_instance.number_absence -= 1
                    db.session.commit()
                    reply_message = "出席が確認されていません。欠席として記録されました。"
                break
            else:
                app.logger.info("No lesson found for this time slot")

    app.logger.info(f"Reply message: {reply_message}")
    
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        try:
            response = line_bot_api.reply_message_with_http_info(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text=reply_message)]
                )
            )
            app.logger.info(f"Reply message sent: {response}")
        except Exception as e:
            app.logger.error(f"Error: {e}")
            try:
                line_bot_api.reply_message_with_http_info(
                    ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=[TextMessage(text="エラーが発生しました。もう一度試してください。")]
                    )
                )
            except Exception as e:
                app.logger.error(f"Failed to send error message: {e}")

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port)