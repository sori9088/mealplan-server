from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin
from flask_dance.consumer.storage.sqla import OAuthConsumerMixin
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
from sqlalchemy.sql import func




db = SQLAlchemy()


class User(UserMixin, db.Model):
    __tablename__='users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256))
    email = db.Column(db.String(80), unique= True)
    password = db.Column(db.String(200))
    avatar_url = db.Column(db.String, default='https://img.icons8.com/cotton/2x/person-male.png')
    seller = db.Column(db.Boolean, default=False)

    # relationships

    products = db.relationship('Product', backref='user', lazy=True)
    cartss = db.relationship('Cart', backref='user', lazy=True)
    orderitems = db.relationship('OrderItem', backref='user', lazy=True)
    comments = db.relationship('Comment', backref='user', lazy= True)

    def set_password(self, password) :
        self.password = generate_password_hash(password)

    def check_password(self,password) :
        return check_password_hash(self.password, password)

    def render(self):
        return {
                    "user_name":self.name,
                    "id":self.id,
                    "email":self.email,
                    "seller":self.seller,
                    "avatar_url" : self.avatar_url

                }

class OAuth(OAuthConsumerMixin, db.Model):
    provider_user_id = db.Column(db.String(256), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship(User)

class Token(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship(User)


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    seller_id= db.Column(db.Integer, db.ForeignKey('users.id'))
    name = db.Column(db.String(80), nullable=False)
    img_url = db.Column(db.String, default='https://i-love-png.com/images/no-image-slide.png')
    description = db.Column(db.Text)
    # store_name = db.Column(db.String(20), nullable=False)
    # location = db.Column(db.String(200), nullable=False)
    # orders = db.relationship('Order', backref='product', lazy=True)
    created = db.Column(db.DateTime(timezone=True), server_default=func.now())
    price = db.Column(db.Float, nullable=False)
    out_of_stock = db.Column(db.Boolean, default=False)

    #relationship
    order_items = db.relationship('OrderItem', backref="product", lazy="dynamic")
    comments = db.relationship('Comment', backref="product", lazy=True)

    def get_products(self):
        return Product.query.filter_by(seller_id=self.id).all()
    
    def get_rating(self) :
        a = Comment.query.with_entities((func.sum(Comment.rating)/func.count(Comment.rating)).label('average'),
                                         func.count(Comment.rating).label('count')).filter(Comment.product_id==self.id).first()
        return {
            "rating": a.average,
            "count" : a.count
        }

    def get_orders(self):
        return OrderItem.query.join(Cart).join(User).with_entities(
            Cart.id.label('id'),
            Cart.user_id.label('user_id'),
            User.name.label('user_name'),
            OrderItem.shipped.label('status'),
            func.count(Cart.id).label('quantity')
            ).filter(OrderItem.product_id == self.id).filter(User.id== Cart.user_id).filter(Cart.checkout==True).group_by(Cart.id,User.id, OrderItem.seller_id,OrderItem.shipped).all()


###  Got seller ID & cartID => find all orderitems with sellerID+cartID => loop set .shipped to true
### Check: if all items in [Carts where cartID = above] has shipped = True =>CartID.shipped = true




class Cart(db.Model):
    __tablename__='carts'
    id = db.Column(db.Integer, primary_key=True)
    user_id= db.Column(db.Integer, db.ForeignKey(User.id))
    order_items = db.relationship('OrderItem', backref="cart", lazy="dynamic")
    checkout = db.Column(db.Boolean, default=False)
    orderss = db.relationship('Order', backref="cart", lazy=True)
    shipped = db.Column(db.Boolean, default=False)

    def get_total(self):
        return OrderItem.query.join(Product).with_entities(
            func.count(Product.id).label('quantity'),
            func.sum(Product.price).label('amount'),
            (func.sum(Product.price)+3).label('ship')).filter(OrderItem.cart_id == self.id).all()

    def get_bill(self):
        return OrderItem.query.join(Product).join(User).with_entities(
            Product.id.label('id'),
            Product.name.label('name'),
            Product.price.label('price'),
            Product.img_url.label('img_url'),
            User.name.label('seller_name'),
            func.count(Product.id).label('quantity'),
            func.sum(Product.price).label('amount')
            ).filter(OrderItem.cart_id == self.id).filter(User.id == Product.seller_id).group_by(Product.id, User.name).all()




class OrderItem(db.Model):
    __tablename__="order_items"
    id = db.Column(db.Integer, primary_key=True)
    product_id= db.Column(db.Integer, db.ForeignKey(Product.id))
    cart_id =  db.Column(db.Integer, db.ForeignKey(Cart.id))
    seller_id = db.Column(db.Integer, db.ForeignKey(User.id))
    # status = db.Column(db.String, default = "Ordered")
    shipped = db.Column(db.Boolean, default=False)


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cart_id =  db.Column(db.Integer, db.ForeignKey(Cart.id))
    status = db.Column(db.String, default = "Ordered")
    created = db.Column(db.DateTime(timezone=True), server_default=func.now())
    add = db.relationship('Address', backref="order", lazy=True)
    shipped=  db.Column(db.Boolean, default=False)
    ## shipped = ........ default = false



### from seller : got id of cart





class Address(db.Model):
    id= db.Column(db.Integer, primary_key = True)
    order_id = db.Column(db.Integer, db.ForeignKey(Order.id))
    firstname = db.Column(db.String)
    lastname = db.Column(db.String)
    add1 = db.Column(db.String)
    add2 = db.Column(db.String)
    city = db.Column(db.String)
    zipcode = db.Column(db.Integer)


class Comment(db.Model) :
    id = db.Column(db.Integer, primary_key = True)
    product_id= db.Column(db.Integer, db.ForeignKey(Product.id))
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    body = db.Column(db.Text, default="No comment")
    rating = db.Column(db.Integer)
    created = db.Column(db.DateTime(timezone=True), server_default=func.now())




# setup login manager
login_manager = LoginManager()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@login_manager.request_loader
def load_user_from_request(request):
    api_key = request.headers.get('Authorization')
    if api_key:
        api_key = api_key.replace('Token ', '', 1)
        token = Token.query.filter_by(uuid=api_key).first()
        if token:
            return token.user
    return None
