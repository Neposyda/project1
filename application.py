import os
import requests

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
    session['status_log'] = 0
    session['status_reg'] = 0
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if session['status_log'] == 0:
        session['status_log'] = 1
        return render_template('login.html')
    #perev chy vvely name
    if request.method == "POST":
        if request.form.get('username'):
            session['username'] = request.form.get('username')
        else:
            return render_template('login.html')
    else:
        return render_template('login.html')
    #perev chy e user i
    if db.execute("SELECT * FROM users WHERE name= :name", {"name": session['username']}).rowcount == 0:
        #session['status_log'] = 1
        session['status_reg'] = 1
        return registr()
    else:
        # loginymsa
        db_user = db.execute("SELECT * FROM users WHERE name= :name", {"name": session['username']}).first()
        session['password']=request.form.get('password')
        if db_user['password'] == session['password']:
            session['status_log'] = 3
            session['books'] =  db.execute("SELECT * FROM books")
            return search()
        else:
            return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return index()


@app.route('/registr', methods=['GET', 'POST'])
def registr():
    if session['status_reg'] == 0:
        session['status_reg'] = 1
        return registr()
    #perev formu
    try:
        if not request.form.get('username'):
            return render_template("registr.html", confirm="Заповніть поле з іменем коритувача")
        session['username'] = request.form.get('username')
        if not request.form.get('password'):
            return render_template("registr.html", username=session['username'], confirm='Введіть пароль')
        session['password'] = request.form.get('password')
        if not request.form.get('password2'):
            return render_template('registr.html', username=session['username'], confirm='Введіть пароль повторно')
        if request.form.get('password') != request.form.get('password2'):
            return render_template('registr.html', username=session['username'], confirm='Паролі не співпадають')
    except ValueError:
        return index()
    #zapovn USERS
    #perev chy kor dze reestr
    if db.execute("SELECT * FROM users WHERE name= :name", {"name": session['username']}).rowcount > 0:
        return login()
    db.execute("INSERT INTO users (name, password) VALUES (:name, :password)",
               {"name": session['username'], "password": session['password']})
    db.commit()
    session['status_reg'] = 3
    return login()


@app.route("/search")
def search():
    str_sql = "SELECT * FROM books WHERE "
    count_likes = 0
    if request.form.get('isbn'):
        str_sql += "isbn LIKE '%" + request.form.get('isbn')+"%'"
        count_likes+=1
    if request.form.get('name'):
        if count_likes > 0:
            str_sql += "AND "
        count_likes += 1
        str_sql += "title LIKE '%" + request.form.get('title') + "%'"
    if request.form.get('name'):
        if count_likes > 0:
            str_sql += " AND "
        str_sql += "title LIKE '%" + request.form.get('title') + "%'"
    try:
        list_books = db.execute(str_sql)
        render_template('books.html', listbooks=list_books)
    except ValueError:
        return render_template('books.html')


@app.route('/book/<string:isbn>')
def book(isbn):

    book = db.execute("SELECT ")


    #res = requests.get("https://www.goodreads.com/book/review_counts.json",
    #                  params={"key": "ekllRCatW1xsWqwHp9nrg", "isbns": "9781632168146"})
    #print(res.json())