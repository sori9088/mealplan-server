from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.models import db, login_manager, Token, User, Product, Cart, OrderItem, Order, Address
import stripe
import os

stripe_keys = {
  'secret_key': os.environ['STRIPE_SECRET_KEY'],
  'publishable_key': os.environ['STRIPE_PUBLISHABLE_KEY']
}

stripe.api_key = stripe_keys['secret_key']


cb = Blueprint('cart', __name__)


@cb.route("/add", methods=['POST'])
@login_required
def add_cart():
    if request.method == 'POST':

        cur_cart = Cart.query.filter_by(user_id=current_user.id,  checkout = False).first()
        if not cur_cart :
            cur_cart= Cart(user_id = current_user.id, checkout = False)
            db.session.add(cur_cart)
            db.session.commit()
        data = request.get_json()
        num = int(data['quantity'])
        product = Product.query.filter_by(id= data['product_id']).first()
        orderitems = []
        for i in range(num) :
            new = OrderItem(product_id = product.id ,
                            cart_id = cur_cart.id,
                            seller_id = product.seller_id)
            orderitems.append(new)

        db.session.add_all(orderitems)
        db.session.commit()

        carts = Cart.query.filter_by(user_id=current_user.id, checkout=False).first()
        # items = OrderItem.query.filter_by(cart_id=carts.id).all()
        orderitems1 = carts.get_bill()
        num_of_items = len(orderitems1)
        b = carts.get_total()

        data = {
                "count": num_of_items,
                "user_id" : carts.user_id,
                "checkout" : carts.checkout,
                "items_cart" :[{
                "seller_name" : orderitem.seller_name,
                "product_id" : orderitem.id,
                "product_name" : orderitem.name,
                "product_price" : orderitem.price,
                "img_url" : orderitem.img_url,
                "quantity" : orderitem.quantity,
                "each_total" : orderitem.amount
                } for orderitem in orderitems1],
                "total" : b[0].amount,
                "whole" : b[0].quantity,
                "ship" : b[0].ship,
                "shipfee" : 3
        }
        return jsonify({
            "success" : True,
            "data" : data
        })


@cb.route("/get", methods=['GET'])
@login_required
def get_cart() :
    carts = Cart.query.filter_by(user_id=current_user.id, checkout=False).first()
    # items = OrderItem.query.filter_by(cart_id=carts.id).all()
    if(carts):
        orderitems = carts.get_bill()
        b = carts.get_total()
    

        data = {
                "cart_id" : carts.id,
                "user_id" : carts.user_id,
                "checkout" : carts.checkout,
                "items_cart" :[{
                "seller_name" : orderitem.seller_name,
                "product_id" : orderitem.id,
                "product_name" : orderitem.name,
                "product_price" : orderitem.price,
                "img_url" : orderitem.img_url,
                "quantity" : orderitem.quantity,
                "each_total" : orderitem.amount
                } for orderitem in orderitems],
                "total" : b[0].amount,
                "whole" : b[0].quantity,
                "ship" : b[0].ship,
                "shipfee" : 3
        }
        return jsonify(data)

    else :
        cur_cart= Cart(user_id = current_user.id, checkout = False)
        db.session.add(cur_cart)
        db.session.commit()

        carts = Cart.query.filter_by(user_id=current_user.id, checkout=False).first()
        orderitems = carts.get_bill()
        num_of_items = len(orderitems)
        b = carts.get_total()

        data = {
                "count": num_of_items,
                "cart_id" : carts.id,
                "user_id" : carts.user_id,
                "checkout" : carts.checkout,
                "items_cart" :[{
                "seller_name" : orderitem.seller_name,
                "product_id" : orderitem.id,
                "product_name" : orderitem.name,
                "product_price" : orderitem.price,
                "img_url" : orderitem.img_url,
                "quantity" : orderitem.quantity,
                "each_total" : orderitem.amount
                } for orderitem in orderitems],
                "total" : b[0].amount,
                "whole" : b[0].quantity,
                "ship" : b[0].ship,
                "shipfee" : 3

        }

        return jsonify(data)


@cb.route("/delete", methods=['POST','GET'])
@login_required
def delete_cart() :
        if request.method =='POST':
            data = request.get_json()
            carts = Cart.query.filter_by(user_id=current_user.id, checkout=False).first()
            item = OrderItem.query.filter_by(product_id=data['product_id'], cart_id=carts.id).delete()
            db.session.commit()

            orderitems1 = carts.get_bill()
            num_of_items = len(orderitems1)
            b = carts.get_total()

            data = {
                    "count": num_of_items,
                    "cart_id" : carts.id,
                    "user_id" : carts.user_id,
                    "checkout" : carts.checkout,
                    "items_cart" :[{
                    "seller_name" : orderitem.seller_name,
                    "product_id" : orderitem.id,
                    "product_name" : orderitem.name,
                    "product_price" : orderitem.price,
                    "img_url" : orderitem.img_url,
                    "quantity" : orderitem.quantity,
                    "each_total" : orderitem.amount
                    } for orderitem in orderitems1],
                    "total" : b[0].amount,
                    "whole" : b[0].quantity,
                    "ship" : b[0].ship,
                    "shipfee" : 3
            }

            return jsonify({
                "success" : True,
                "message" : "Something wrong!",
                "data" : data
            })


@cb.route("/charge", methods=['POST','GET'])
@login_required
def charge() :
    if request.method =='POST':
        data = request.get_json()
        cur_cart = Cart.query.filter_by(user_id=current_user.id, checkout = False).first()
        if (not cur_cart):
            return jsonify({
            "success": False,
            "message" : "There is no cart"
            })

        amount = data['price']

        stripe.Charge.create(
            amount= amount*100,
            currency= 'usd',
            card = data['token']
        )

        cur_cart.checkout = True

        new_order = Order(cart_id = cur_cart.id)
        db.session.add(new_order)
        db.session.commit()


        new_cart= Cart(user_id = current_user.id, checkout = False)
        db.session.add(new_cart)
        db.session.commit()

        carts = Cart.query.filter_by(user_id=current_user.id, checkout=False).first()
        orderitems1 = carts.get_bill()
        num_of_items = len(orderitems1)
        b = carts.get_total()

        data = {
                "count": num_of_items,
                "user_id" : carts.user_id,
                "checkout" : carts.checkout,
                "items_cart" :[{
                "seller_name" : orderitem.seller_name,
                "product_id" : orderitem.id,
                "product_name" : orderitem.name,
                "product_price" : orderitem.price,
                "img_url" : orderitem.img_url,
                "quantity" : orderitem.quantity,
                "each_total" : orderitem.amount
                } for orderitem in orderitems1],
                "total" : b[0].amount,
                "whole" : b[0].quantity,
                "ship" : b[0].ship,
                "shipfee" : 3
        }

        return jsonify({
            "success" : True,
            "data" : data
        })



@cb.route("/addAdd", methods=['POST','GET'])
@login_required
def addAdd():
    if request.method =='POST' :
        data = request.get_json()['data']
        cur_order = Order.query.filter_by(cart_id = data['cart_id']).first()
        data = data['form']
        new_add = Address(
            order_id = cur_order.id,
            firstname = data['fname'],
            lastname = data['lname'],
            add1= data['add1'],
            add2=data['add2'],
            city= data['city'],
            zipcode = data['zip']
        )
        db.session.add(new_add)
        db.session.commit()
    return jsonify({
        "success" : True
    })