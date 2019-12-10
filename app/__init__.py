from flask import Flask, redirect, url_for, flash, render_template, jsonify, request
from flask_login import login_required, logout_user, current_user,login_user
from .config import Config
from .models import db, login_manager, Token, User, Product, Cart, OrderItem
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
                "code" : 1,
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
        return jsonify(success=False, code=2, message="Wrong password")


@app.route("/register", methods=['POST','GET'])
def register() :
    if request.method == "POST":
        data = request.get_json()
        if  User.query.filter_by(email=data['email']).first():
            return jsonify({
                "success":False,
                "message": "email already taken"
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


@app.route("/new_dish", methods=['POST', 'GET'])
@login_required
def new_dish() :
    user_id = current_user.id
    if request.method =='POST' :
        data= request.get_json()
        new_dish = Product(
            name=data['name'],
            seller_id = user_id,
            price= data['price'],
            img_url= "https://i-love-png.com/images/no-image-slide.png" if data['img_url']=="" else data['img_url'],
            description= data['description']
        )
        db.session.add(new_dish)
        db.session.commit()
        return jsonify({
            "success" : True
        })


@app.route("/get_products", methods=['GET','POST'])
def get_products():
    products = Product.query.all()

    data = {
        "dishes":[{
        "id" : product.id,
        "name" : product.name ,
        "img_url" : product.img_url,
        "description" : product.description,
        "seller" : User.query.filter_by(id=product.seller_id).first().name,
        "created" : product.created,
        "price" : product.price
                } for product in products ]
    }
    return jsonify(data)


@app.route("/detail/<id>", methods=['GET','POST'])
def single_product(id):
    product = Product.query.filter_by(id=id).first()
    data = {
        "id" : product.id,
        "name" : product.name ,
        "img_url" : product.img_url,
        "description" : product.description,
        "seller" : User.query.filter_by(id=product.seller_id).first().name,
        "created" : product.created,
        "price" : product.price
        }

    return jsonify(data)


@app.route("/add_cart", methods=['POST'])
@login_required
def add_cart():
    if request.method == 'POST':

        cur_cart = Cart.query.filter_by(user_id=current_user.id,  checkout = False).first()
        if not cur_cart :
            cur_cart= Cart(user_id = current_user.id, checkout = False)
            db.session.add(cur_cart)
            db.session.commit()
        data = request.get_json()
        num = data['quantity']
        product = Product.query.filter_by(id= data['product_id']).first()
        orderitems = []
        for i in range(num) :
            new = OrderItem(product_id = product.id ,
                            cart_id = cur_cart.id)
            orderitems.append(new)

        db.session.add_all(orderitems)
        db.session.commit()
        return jsonify({
            "success" : True
        })


@app.route("/get_cart/<id>", methods=['GET'])
def get_cart(id) :
    carts = Cart.query.filter_by(user_id=id, checkout=False).first()
    orderitems = OrderItem.query.filter_by(cart_id=carts.id).all()
    num_of_items = len(orderitems)
    cur_user = User.query.filter_by(id= id).first()

    data = {
        "cart" : {
            "user_id" : carts.user_id,
            "checkout" : carts.checkout,
            "items_cart" :[{
            "seller_name" : orderitem.product.user.name,
            "product_name" : orderitem.product.name
            } for orderitem in orderitems]
            }
        ,"count": num_of_items
    }

    return jsonify(data)
