import os
import re
from unicodedata import name
from flask import Flask, render_template, request, flash, redirect, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import eagerload
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


ENV = "compc"

if ENV == "dev":
    app.debug = True
    # app.config[
    #     "SQLALCHEMY_DATABASE_URI"
    # ] = "postgresql://postgres:123456@localhost/clinc"
    app.config[
        "SQLALCHEMY_DATABASE_URI"
    ] = "postgres://elktwbviwldjhu:ea9394808d18361a86a583dba81e5a1d82a25c7a9a166a6e21e1ba99493632fb@ec2-35-171-250-21.compute-1.amazonaws.com:5432/dbs5ivltb9f5vc"
else:
    app.debug = False
    app.config["SQLALCHEMY_DATABASE_URI"] = uri
    # or other relevant config var

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

LIST = ["شعر", "نحافة", "سمنة", "بشرة"]
SUB_LIST = [
    "تفتيح البشرة",
    "حب الشباب",
    "تسمين الخدود",
    "كلف الحمل",
    "الهالات السوداء",
    "اثار الجروح",
    "ترطيب وتنعيم البشرة",
    "توحيد لون البشرة",
    "تساقط الشعر",
    "توحيد الشعر الشائب",
    "تطويل الشعر",
    "الثعلبة",
    "تقصف الشعر",
    "ملئ الفراغات",
    "ترطيب وتنعيم الشعر",
    "السمنة والنحافة",
]


class user(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(200), unique=True)
    name = db.Column(db.String(200))
    list = db.Column(db.Text())
    password = db.Column(db.Text())
    gender = db.Column(db.String(50))
    sub_list = db.Column(db.String(200))
    reg_date = db.Column(db.Date)

    def __init__(self, phone, name, list, password, gender, sub_list, reg_date):
        self.phone = phone
        self.name = name
        self.list = list
        self.password = password
        self.gender = gender
        self.sub_list = sub_list
        self.reg_date = reg_date


class instructions(db.Model):
    __tablename__ = "instructions"
    instr_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(200))
    instruct = db.Column(db.Text())
    instr_date = db.Column(db.Date())

    def __init__(self, user_id, instruct, instr_date):
        self.user_id = user_id
        self.instruct = instruct
        self.instr_date = instr_date


class details(db.Model):
    __tablename__ = "details"
    id = db.Column(db.Integer, primary_key=True)
    ddate = db.Column(db.Date())
    age = db.Column(db.Integer())
    tall = db.Column(db.Integer())
    wight = db.Column(db.Integer())
    fat = db.Column(db.Integer())
    water = db.Column(db.Integer())
    calories = db.Column(db.Integer())
    bone = db.Column(db.Integer())
    muscles = db.Column(db.Integer())
    user_id = db.Column(db.Integer())

    def __init__(
        self, ddate, age, tall, wight, fat, water, calories, bone, muscles, user_id
    ):
        self.ddate = ddate
        self.age = age
        self.tall = tall
        self.wight = wight
        self.fat = fat
        self.water = water
        self.calories = calories
        self.bone = bone
        self.muscles = muscles
        self.user_id = user_id


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
@login_required
def reg():
    if request.method == "POST":
        if request.form.get("password") != request.form.get("confirmation"):
            flash("Not Matched password!!", category="error")
            return render_template("/register.html", list=LIST, sublist=SUB_LIST)
        else:
            # hashed_pass = generate_password_hash(request.form.get('password'))
            hashed_pass = generate_password_hash(request.form.get("password"))
            password = request.form.get("password")
            name = request.form.get("name")
            phone = request.form.get("phone")
            # tall = request.form.get("tall")
            # wight = request.form.get("wight")
            # age = request.form.get("age")
            list = request.form.get("list")
            sub_list = request.form.get("sub_list")
            reg_date = request.form.get("reg_date")
            gander = request.form.get("gander")
            print(phone, name, list, password, gander, sub_list, reg_date)
            if db.session.query(user).filter(user.phone == phone).count() == 0:
                data = user(phone, name, list, password,
                            gander, sub_list, reg_date)
                db.session.add(data)
                db.session.commit()
                # flash("You Are Register Welcome!!!!!", category="succ")
                return render_template("login.html")
            flash("Phone Number Already Exist!!", category="error")
            return render_template("/register.html", list=LIST, sublist=SUB_LIST)
    else:
        return render_template("register.html", list=LIST, sublist=SUB_LIST)


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
            session["name"] = p[0].name
            # name = p[0].name
            # print("Name :- ", name)
            phone = session["user"]
            name = session["name"]
            return render_template("index.html")
    else:
        return render_template("login.html")


@app.route("/instruct", methods=["GET", "POST"])
@login_required
def inst():
    user_list = db.session.query(user).all()
    if request.method == "GET":
        return render_template("instruct.html", list=user_list)
    else:
        tel = request.form.get("phone")
        print("PHONE:_ ", tel)
        u_id = db.session.query(user).filter(user.phone == tel)[0].id
        print("|ID:_ ", u_id)
        age = request.form.get("age")
        tall = request.form.get("tall")
        bone = request.form.get("bone")
        muscles = request.form.get("muscles")
        weight = request.form.get("weight")
        fat = request.form.get("fat")
        water = request.form.get("water")
        calories = request.form.get("calories")
        struct = request.form.get("struct")
        date = request.form.get("date")
        adata = instructions(u_id, struct, date)
        bdata = details(
            date, age, tall, weight, fat, water, calories, bone, muscles, u_id
        )
        db.session.add(adata)
        db.session.add(bdata)
        db.session.commit()
        # flash("instructions Complate!!!!!", category="succ")
        return render_template("instruct.html", list=user_list)


@app.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    session.clear()
    return render_template("index.html")


@app.route("/profile", methods=["GET", "POST"])
@login_required
def test2():
    phone = session["user"]
    user_id = db.session.query(user).filter(user.phone == phone)[0].id
    instdata = db.session.query(instructions).filter(
        instructions.user_id == user_id
    )
    detdata = db.session.query(details).filter(details.user_id == user_id)
    usdata = db.session.query(user).filter(user.id == user_id)
    # print("instdata:- ")
    # print(instdata)
    # print("dedata:- ")
    # print(detdata)
    # print("usdata:- ")
    # print(usdata)
    return render_template("profile.html", usdata=usdata, instdata=instdata, detdata=detdata)


if __name__ == "__main__":
    app.run()
