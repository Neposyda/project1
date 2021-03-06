import os
import requests
from datetime import datetime

from flask import Flask, session, render_template, request, jsonify
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
    # по замовчування чи без параметра виводити перші 20 книг,
    # організувати перегляд по 20 книг, напр
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
        session['status_reg'] = 0
        return registr()
    else:
        # loginymsa
        db_user = db.execute("SELECT * FROM users WHERE name= :name", {"name": session['username']}).first()
        session['password']=request.form.get('password')
        if db_user['password'] == session['password']:
            session['status_log'] = 3
            session['search'] = 0
            session['user_id'] = db_user['id']
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
        return render_template("registr.html", confirm="Користувач " + session['username']+" в базі відсутній.")
    #perev formu
    try:
        if not request.form.get('username'):
            return render_template("registr.html", confirm="Заповніть поле з іменем користувача")
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


@app.route("/search", methods=['get', 'post'])
def search():
    if session['search'] != 1:
        session['search'] = 1
        return render_template('search.html')
    str_sql = ""
    count_likes = 0
    if request.form.get('isbn'):
        str_sql += "isbn LIKE '%" + request.form.get('isbn')+"%'"
        count_likes += 1
    if request.form.get('title'):
        if count_likes > 0:
            str_sql += "AND "
        count_likes += 1
        str_sql += "title LIKE '%" + request.form.get('title') + "%'"
    if request.form.get('author'):
        if count_likes > 0:
            str_sql += " AND "
        str_sql += "author LIKE '%" + request.form.get('author') + "%'"
    if str_sql != "":
        str_sql="SELECT * FROM books WHERE "+str_sql
    else:
        session['search'] = 0
        return search()
    try:
        session['search'] = 2
        list_books = db.execute(str_sql)
        return render_template('search.html', listbooks=list_books)
    except ValueError:
        session['search'] = 1
        return render_template('search.html')


@app.route('/API/<string:isbn>')
def str_json(isbn):
    book_j = db.execute("SELECT * FROM books WHERE isbn= :isbn",{"isbn": isbn}).first()
    session['book_id'] = book_j['id']
    qoodread = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "ekllRCatW1xsWqwHp9nrg", "isbns": isbn}).json()
    return jsonify({
        "title": book_j['title'],
        "author": book_j['author'],
        "year": book_j['year'],
        "isbn": book_j['isbn'],
        "review_count": qoodread['books'][0]['reviews_count'],
        "average_score": qoodread['books'][0]['average_rating']
    })


@app.route('/book/<string:isbn>', methods=['get'])
def book(isbn):
    #informaciya pro knyzky
    session['book_id'] = ""
    session['book_isbn'] = isbn
    book_app = str_json(isbn).json
    #vidguky
    reviews_app = db.execute("SELECT * FROM reviews WHERE book_id= :bookid", {'bookid': session['book_id']})
    session['check_user'] = False
    if db.execute("SELECT id FROM reviews WHERE user_id= :userid AND book_id= :bookid",
                  {"userid": session['user_id'], "bookid": session['book_id']}).rowcount == 0:
        session['check_user'] = True
    if reviews_app.rowcount != 0:
        return render_template("book.html", book=book_app, reviews=reviews_app)
    return render_template("book.html", book=book_app)


@app.route('/review_add', methods=['post'])
def reviews_add():
    if request.form.get('review_text'):
       db.execute("INSERT INTO reviews (user_id, content, date_time, book_id) "
                  "VALUES (:user_id, :content, :date_time , :book_id)",
                  {"user_id": session['user_id'], "content": request.form.get('review_text'),
                   "date_time": datetime.now(), "book_id": session['book_id']})
       db.commit()
    return book(session['book_isbn'])
