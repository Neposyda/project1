import os

from flask import Flask, session
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

# Check for environment variable

# Host- ec2-54-247-101-205.eu-west-1.compute.amazonaws.com
# Database: d3k44c6n3ctdn5
# User- lwjztjbjnthnna
# Port- 5432
# Password- d00fffb8b1c47ac7ba6d079060d26bb25d9f1472b1d9d90401bb6c34f49caed9
# URI- postgres://lwjztjbjnthnna:d00fffb8b1c47ac7ba6d079060d26bb25d9f1472b1d9d90401bb6c34f49caed9@ec2-54-247-101-205.eu-west-1.compute.amazonaws.com:5432/d3k44c6n3ctdn5
# Heroku CLI: heroku pg:psql postgresql-infinite-40704 --app project-n1


if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def index():
    return "Project 1: TODO"
