from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.models import db, login_manager, Token, User, Product, Cart, OrderItem


pb = Blueprint('product', __name__)


@pb.route("/new", methods=['POST', 'GET'])
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

        return jsonify({
            "success" : True,
            "data" : data
        })


@pb.route("/get", methods=['GET','POST'])
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


@pb.route("/detail/<id>", methods=['GET','POST'])
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
