from flask import Flask, redirect, url_for, flash, render_template, jsonify, request
from flask_login import login_required, logout_user, current_user,login_user
from .config import Config
from .models import db, login_manager, Token, User
from .oauth import blueprint
from .cli import create_db
from flask_migrate import Migrate
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import uuid



app = Flask(__name__)
CORS(app) # Add me after the above line
app.config.from_object(Config)
app.register_blueprint(blueprint, url_prefix="/login")
app.cli.add_command(create_db)
db.init_app(app)
migrate = Migrate(app, db) # this
login_manager.init_app(app)



@app.route("/logout", methods=['GET','POST'])
@login_required
def logout():
    token = Token.query.filter_by(user_id = current_user.id).first()
    if token:
        db.session.delete(token)
        db.session.commit()
 
    logout_user()
    flash("You have logged out")
    return jsonify({
        "success" : True
    })


@app.route("/")
def index():
    return render_template("home.html")


@app.route("/getuser", methods=['GET','POST'])
@login_required
def getuser():
    return jsonify({
        "success" : True,
        "user":{
        "user_id" : current_user.id,
        "user_name" : current_user.name ,
        "avatar_url" : current_user.avatar_url,
        "seller" : current_user.seller
                }
    })


@app.route('/login', methods=['POST'])
def login() :
    if request.method == "POST":
        data= request.get_json()
        user = User.query.filter_by(email=data['email']).first()
        if not user : 
            return jsonify({
                "success" : False,
                "message" : "You should sign up first"
            })
        if user.check_password(data['password']):
            login_user(user)
            #check token
            token = Token.query.filter_by(user_id=user.id).first()
            if not token:
                token = Token( user_id=user.id, uuid=str(uuid.uuid4().hex))
                db.session.add(token)
                db.session.commit()
            return jsonify(
                success=True,
                token=token.uuid,
                user=user.render()
            )
        return jsonify(success=False, message="Wrong password")


@app.route("/register", methods=['POST','GET'])
def register() :
    if request.method == "POST":
        data = request.get_json()
        if  User.query.filter_by(email=data['email']).first():
            return jsonify({
                "success":False,
                "message": "email taken"
            })
        new_user = User(
            name=data['name'],
            email=data['email'],
            avatar_url =  "https://img.icons8.com/cotton/2x/person-male.png" if data['avatar_url']== "" else  data['avatar_url'],
            seller=True if data['seller'] =='true' else False
        )
        new_user.set_password(data['password'])
        db.session.add(new_user)
        db.session.commit()
        return jsonify({
               "success" : True
        })