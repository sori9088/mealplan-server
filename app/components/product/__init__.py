from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.models import db, login_manager, Token, User, Product, Cart, OrderItem,Comment


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

        products = Product.query.order_by(Product.out_of_stock.asc()).all()

        data = {
            "dishes":[{
            "id" : product.id,
            "name" : product.name ,
            "img_url" : product.img_url,
            "description" : product.description,
            "seller" : User.query.filter_by(id=product.seller_id).first().name,
            "created" : product.created,
            "price" : product.price,
            "status" : product.out_of_stock
                    } for product in products ]
        }

        return jsonify({
            "success" : True,
            "data" : data
        })


@pb.route("/get", methods=['GET','POST'])
def get_products():
    products = Product.query.order_by(Product.out_of_stock.asc()).all()

    data = {
        "dishes":[{
        "id" : product.id,
        "name" : product.name ,
        "img_url" : product.img_url,
        "description" : product.description,
        "seller" : User.query.filter_by(id=product.seller_id).first().name,
        "created" : product.created,
        "price" : product.price,
        "status" : "In stock" if product.out_of_stock==False else "Sold Out"
        } for product in products ]
    }
    return jsonify(data)


@pb.route("/seller", methods=['GET','POST'])
@login_required
def get_seller():
    products = Product.query.filter_by(seller_id = current_user.id).order_by(Product.out_of_stock.asc()).all()
    num = len(products)

    data = {
        "quantity" : num,
        "dishes":[{
        "id" : product.id,
        "name" : product.name ,
        "img_url" : product.img_url,
        "description" : product.description,
        "seller" : User.query.filter_by(id=product.seller_id).first().name,
        "created" : product.created,
        "price" : product.price,
        "status" : product.out_of_stock

                } for product in products ]
    }
    return jsonify(data)

@pb.route("/detail/<id>", methods=['GET','POST'])
def single_product(id):
    product = Product.query.filter_by(id=id).first()
    if product.out_of_stock == True : status = "Sold Out"
    else : status = "In stock"

    data = {
        "id" : product.id,
        "name" : product.name ,
        "img_url" : product.img_url,
        "description" : product.description,
        "seller" : User.query.filter_by(id=product.seller_id).first().name,
        "seller_id" : product.seller_id,
        "created" : product.created,
        "price" : product.price,
        "status" : status,
        "seller_img" : User.query.filter_by(id=product.seller_id).first().avatar_url

        }

    return jsonify(data)

@pb.route("/soldout", methods=['GET','POST'])
def soldout():
    if request.method== 'POST' :
        data = request.get_json()
        product = Product.query.filter_by(id = data['product_id']).first()
        product.out_of_stock = True
        db.session.commit()

        products = Product.query.filter_by(seller_id = current_user.id).order_by(Product.out_of_stock.asc()).all()
        num = len(products)

        data = {
            "quantity" : num,
            "dishes":[{
            "id" : product.id,
            "name" : product.name ,
            "img_url" : product.img_url,
            "description" : product.description,
            "seller" : User.query.filter_by(id=product.seller_id).first().name,
            "created" : product.created,
            "price" : product.price,
            "status" : "In stock" if product.out_of_stock==False else "Sold Out"
                    } for product in products ]
        }
        return jsonify(data)


@pb.route("/seller/info", methods=['GET','POST'])
@login_required
def get_sellerorder():
    if request.method == 'POST' :
        data = request.get_json()
        products = Product.query.filter_by(seller_id=data['id']).all()

        items=[]
        for product in products :
            orderlists = []
            for i in product.get_orders() :
                orderlists.append({
                    "product" : product.name,
                    "product_id" : product.id
                    })
            items.append(orderlists)

        return jsonify({
            "orders" : items,
            "count" : len(products)
            })


@pb.route("/comment/get/<id>" , methods=['GET'])
def get_comment(id):
    comments = Comment.query.filter_by(product_id=id).all()
    return jsonify({
            "success" : True,
            "comments" : [{
            "id" : comment.id,
            "body" : comment.body,
            "user_id" : comment.user_id,
            "user_name" : comment.user.name,
            "avatar_url" : comment.user.avatar_url,
            "rating" : comment.rating,
            "created" : comment.created
        }for comment in comments]
    })



@pb.route("/comment/getall" , methods=['GET'])
def all_comment():
    comments = Comment.query.all()
    return jsonify({
            "success" : True,
            "comments" : [{
            "id" : comment.id,
            "body" : comment.body,
            "user_id" : comment.user_id,
            "user_name" : comment.user.name,
            "avatar_url" : comment.user.avatar_url,
            "rating" : comment.rating,
            "created" : comment.created,
            "product_id" : comment.product_id
        }for comment in comments]
    })


@pb.route("/comment/new", methods=['GET','POST'])
@login_required
def new_comment():
    if request.method == 'POST' :
        data = request.get_json()
        new_comment= Comment(
            user_id = current_user.id,
            product_id = data['id'],
            body = data['comment']['comment'],
            rating = data['comment']['rating']
        )
        db.session.add(new_comment)
        db.session.commit()

        comments = Comment.query.filter_by(product_id=data['id']).all()
        return jsonify({
            "success" : True,
            "comments" : [{
                "id" : comment.id,
                "body" : comment.body,
                "user_id" : comment.user_id,
                "user_name" : comment.user.name,
                "avatar_url" : comment.user.avatar_url,
                "rating" : comment.rating,
                "created" : comment.created
            }for comment in comments]
        })

@pb.route("/comment/delete", methods=['GET','POST'])
@login_required
def delete_comment():
    if request.method == 'POST' :
        data = request.get_json()
        cur_comment = Comment.query.filter_by(id = data['id']).first()
        db.session.delete(cur_comment)
        db.session.commit()

        comments = Comment.query.filter_by(product_id=data['p_id']).all()
        return jsonify({
            "success" : True,
            "comments" : [{
                "id" : comment.id,
                "body" : comment.body,
                "user_id" : comment.user_id,
                "user_name" : comment.user.name,
                "avatar_url" : comment.user.avatar_url,
                "rating" : comment.rating,
                "created" : comment.created
            }for comment in comments]
        })