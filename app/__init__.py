from flask import Flask, jsonify, request, render_template
from flask_login import login_required, logout_user, current_user,login_user
from .config import Config
from .models import db, login_manager, Token, User, Product, Cart, OrderItem, Order, Address, OAuth
from .oauth import blueprint
from .cli import create_db
from flask_migrate import Migrate
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import stripe
import uuid
from dotenv import load_dotenv
load_dotenv()



app = Flask(__name__)
CORS(app) 
app.config.from_object(Config)
app.register_blueprint(blueprint, url_prefix="/login")
app.cli.add_command(create_db)
db.init_app(app)
migrate = Migrate(app, db) 
login_manager.init_app(app)




from .components.product import pb
app.register_blueprint(pb, url_prefix='/product')

from .components.cart import cb
app.register_blueprint(cb, url_prefix='/cart')


@app.route("/logout", methods=['GET','POST'])
@login_required
def logout():
    token = Token.query.filter_by(user_id = current_user.id).first()
    if token:
        db.session.delete(token)
        db.session.commit()

    logout_user()
    return jsonify({
        "success" : True
    })


@app.route("/")
def index():
    return render_template("home.html")


@app.route("/getuser", methods=['GET','POST'])
@login_required
def getuser():
    fb_id = OAuth.query.filter_by(user_id=current_user.id).first() 
    if fb_id :
        face_id = fb_id.provider_user_id
    face_id = ""       
    return jsonify({
        "success" : True,
        "user":{
                "user_id" : current_user.id,
                "user_name" : current_user.name ,
                "avatar_url" : current_user.avatar_url,
                "seller" : current_user.seller,
                "fb_id" : face_id

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


@app.route("/user/order/get" , methods=['GET'])
@login_required
def get_order():
    carts = Cart.query.filter_by(user_id=current_user.id, checkout=True).all()
    if carts :
        carts1 =[ {
            "cart_id": cart.id,
            "status" : cart.orderss[0].status,
            "ordered" : cart.orderss[0].created
            }for cart in carts]

        # import code; code.interact(local=dict(globals(), **locals()))
        new_carts=[]
        for cart in carts:
            orders = []
            for i in cart.get_bill() :
                orders.append({
                    "cart_id" : cart.id,
                    "status" : cart.orderss[0].status,
                    "ordered" : cart.orderss[0].created,
                    "seller_name" : i.seller_name,
                    "product_id" : i.id,
                    "product_name" : i.name,
                    "product_price" : i.price,
                    "img_url" : i.img_url,
                    "quantity" : i.quantity,
                    "each_total" : i.amount
                })
            new_carts.append(orders)

        return jsonify({
            "items" : new_carts
        })


@app.route("/seller/order", methods=['GET'])
@login_required
def get_sellerorder():
    products = Product.query.filter_by(seller_id=current_user.id).all()

    items=[]
    for product in products :
        orderlists = []
        for i in product.get_orders() :
            orderlists.append({
                "product" : product.name,
                "product_id" : product.id,
                "price" : product.price,
                "img_url" : product.img_url,
                "cart_id" : i.id,
                "user_id" : i.user_id,
                "user_name" : i.user_name,
                "quantity" : i.quantity
                })
        items.append(orderlists)

    return jsonify({
        "orders" : items
        })
