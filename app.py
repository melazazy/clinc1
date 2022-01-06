import os
import re
from flask import Flask, render_template, request, flash, redirect, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine

from login import login_required

from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from flask_session import Session


app = Flask(__name__)
app.secret_key = "sd4322@$#*(DChdwd"
uri = os.getenv("DATABASE_URL")  # or other relevant config var
if uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


ENV = "prod"

if ENV == "dev":
    app.debug = True
    app.config[
        "SQLALCHEMY_DATABASE_URI"
    ] = "postgresql://postgres:123456@localhost/clinc"
else:
    app.debug = False
    app.config["SQLALCHEMY_DATABASE_URI"] = uri
    # or other relevant config var

    # uri = os.getenv("DATABASE_URL")  # or other relevant config var
    # if uri.startswith("postgres://"):
    #     uri = uri.replace("postgres://", "postgresql://", 1)
    # SQLALCHEMY_DATABASE_URI=uri
    uri = os.getenv("DATABASE_URL")
    if uri.startswith("postgres://"):
        uri = uri.replace("postgres://", "postgresql://")
    engine = create_engine(uri, echo=True)


app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

LIST = ["hair", "fit", "weight", "skin"]


class user(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(200), unique=True)
    name = db.Column(db.String(200))
    age = db.Column(db.Integer)
    tall = db.Column(db.Integer)
    wight = db.Column(db.Integer)
    list = db.Column(db.Text())
    password = db.Column(db.Text())

    def __init__(self, phone, name, age, tall, wight, list, password):
        self.phone = phone
        self.name = name
        self.age = age
        self.tall = tall
        self.wight = wight
        self.list = list
        self.password = password


class instructions(db.Model):
    __tablename__ = "instructions"
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(200))
    instruct = db.Column(db.Text())

    def __init__(self, user, instruct):
        self.user = user
        self.instruct = instruct


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def reg():
    if request.method == "POST":
        if request.form.get("password") != request.form.get("confirmation"):
            flash("Not Matched password!!", category="error")
            return render_template("/register.html", list=LIST)
        else:
            # hashed_pass = generate_password_hash(request.form.get('password'))
            hashed_pass = generate_password_hash(request.form.get("password"))
            password = request.form.get("password")
            name = request.form.get("name")
            phone = request.form.get("phone")
            tall = request.form.get("tall")
            wight = request.form.get("wight")
            age = request.form.get("age")
            list = request.form.get("list")
            # print(phone, password, name, age, tall, wight, list)
            if db.session.query(user).filter(user.phone == phone).count() == 0:
                data = user(phone, name, age, tall, wight, list, password)
                db.session.add(data)
                db.session.commit()
                # flash("You Are Register Welcome!!!!!", category="succ")
                return render_template("login.html")

            flash("Phone Number Already Exist!!", category="error")
            return render_template("/register.html", list=LIST)
    else:
        return render_template("register.html", list=LIST)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        phone = request.form.get("phone")
        password = request.form.get("password")
        p = db.session.query(user).filter(user.phone == phone)
        if p.count() != 1 or p[0].password != password:
            flash("Phone Number Or Password Is Wrong!!", category="error")
            return redirect("/")
        else:
            # flash("Welcome In!", category="succ")
            session["user"] = p[0].phone
            # session["user_id"] = p[0]["id"]
            return render_template("profile.html")
    else:
        return render_template("login.html")


@app.route("/instruct", methods=["GET", "POST"])
def inst():
    if request.method == "GET":
        user_list = db.session.query(user).all()
        return render_template("instruct.html", list=user_list)
    else:
        phone = request.form.get("list")
        user_id = db.session.query(user).filter(user.phone == phone)[0].id
        struct = request.form.get("instruct")
        # date = request.form.get("date")
        data = instructions(user_id, struct)
        db.session.add(data)
        db.session.commit()
        # flash("instructions Complate!!!!!", category="succ")
        # return render_template("instruct.html")
        return redirect("/")


@app.route("/profile", methods=["GET", "POST"])
@login_required
def prof():
    if request.method == "GET":
        phone = session["user"]
        user_id = db.session.query(user).filter(user.phone == phone)[0].id
        pdata = db.session.query(instructions).filter(instructions.user == user_id)
        # print(phone)
        # print(user_id)

        return render_template("profile.html", pdata=pdata)
    else:

        return render_template("profile.html")


@app.route("/logout", methods=["GET", "POST"])
def logout():
    session.clear()
    return render_template("index.html")


if __name__ == "__main__":
    app.run()
