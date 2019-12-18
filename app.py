from time import sleep

from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit

from celery_setup import make_celery

app = Flask(__name__)
app.config.update(
    CELERY_BROKER_URL='amqp://test:test@localhost',
    CELERY_RESULT_BACKEND='amqp://test:test@localhost'
)
celery = make_celery(app)
socketio = SocketIO(app, message_queue="amqp://test:test@localhost", cors_allowed_origins="*")


@app.route('/')
def home():
    return render_template('index.html')


@socketio.on('connect')
def socketio_connect():
    user_id = request.sid
    emit('connected', {'user_id': user_id}, room=user_id)


@celery.task()
def test_celery(user_id):
    for i in range(5, 0, -1):
        sleep(1)
        socketio.emit('message', {'message': "task over in "+str(i)}, room=user_id)
    socketio.emit('message', {'message': "task completed"}, room=user_id)


@socketio.on('start task')
def handle_message():
    user_id = request.sid
    celery_task = test_celery.delay(user_id=user_id)
    print(celery_task.status)


