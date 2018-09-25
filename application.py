import os

from flask import Flask, session, render_template, request
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

# Check for environment variable

os.environ['DATABASE_URL'] = 'postgres://lwjztjbjnthnna:d00fffb8b1c47ac7ba6d079060d26bb25d9f1472b1d9d90401bb6c34f49caed9@ec2-54-247-101-205.eu-west-1.compute.amazonaws.com:5432/d3k44c6n3ctdn5'
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/", methods=["GET"])
def index():
    # Відкриваєм сторінку з описом ресурсу і даєм можливість перейти на ЛОГІН си РЕЄСТРАЦІЯ
    # Відкрити форму для введення логіну ЛОГІН
    # - перевірка при логінування, якщо користувач відсутній в базі перенести на форма РЕЄСТРАЦІЯ
    # - після реєстрації повернути на ЛОГІН
    # Залогінилися
    # виставити кнопку вихід, щоб рзлогінитися-
    # - зберігати в seans дані користувача чи достатньо ID
    #
    #ПОШУК КНИГ - пошук по назві, по ісбн, по автору
    # по замовчування чи без параметра виводити перші 20 книг,
    # організувати перегляд по 20 книг, напр
    # Вибрали і переходим\відкриваєм тут же на сторінку ДАНІ ПРО КНИГУ
    # -заголовок
    # -автор
    # -рік публікації
    # -номер ісбн
    # - ВІДГУКИ які є
    return render_template('index.html')


@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()
    if request.method == "POST":
        pass
    else:
        return render_template('login.html', button_text='Submit')


@app.route('/logout')
def logout():
    session.clear()
    return render_template('index.html')


@app.route ('/registration')
def registration():
    return "render_template ('registration.html')"
