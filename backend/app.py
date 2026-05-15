from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os
import json
from datetime import datetime

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///fashion.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["UPLOAD_FOLDER"] = "static/uploads"

db = SQLAlchemy(app)
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)


class Seller(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    shop_name = db.Column(db.String(120))
    description = db.Column(db.Text)
    category = db.Column(db.String(50))
    avatar = db.Column(db.String(500))
    telegram = db.Column(db.String(120))
    rating = db.Column(db.String(20), default="5.0")
    likes = db.Column(db.Integer, default=0)


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    seller_id = db.Column(db.Integer)
    name = db.Column(db.String(120))
    price = db.Column(db.Integer)
    category = db.Column(db.String(50))
    image = db.Column(db.String(500))
    description = db.Column(db.Text)
    size = db.Column(db.String(50))
    brand = db.Column(db.String(100))
    color = db.Column(db.String(50))
    condition = db.Column(db.String(100))
    stock = db.Column(db.Integer, default=1)
    vip = db.Column(db.Boolean, default=False)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    telegram_id = db.Column(db.String(120), unique=True)
    name = db.Column(db.String(120))
    username = db.Column(db.String(120))
    telegram = db.Column(db.String(120))
    city = db.Column(db.String(120))
    avatar = db.Column(db.String(500))
    is_vip = db.Column(db.Boolean, default=False)


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    shop = db.Column(db.String(120), default="general")
    sender = db.Column(db.String(120))
    text = db.Column(db.Text)
    image = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_telegram_id = db.Column(db.String(120))
    items = db.Column(db.Text)
    total = db.Column(db.Integer)
    payment = db.Column(db.String(50))
    status = db.Column(db.String(50), default="pending")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


def save_file(file):
    if not file or file.filename == "":
        return None
    filename = secure_filename(file.filename)
    path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(path)
    return "/static/uploads/" + filename


@app.route("/")
def home():
    sellers = Seller.query.all()
    return render_template("index.html", sellers=sellers)


@app.route("/seller")
def seller_dashboard():
    sellers = Seller.query.all()
    products = Product.query.all()
    orders = Order.query.order_by(Order.id.desc()).all()
    return render_template("seller.html", sellers=sellers, products=products, orders=orders)


@app.route("/add-seller", methods=["POST"])
def add_seller():
    file = request.files.get("avatar_file")
    uploaded_avatar = save_file(file)

    seller = Seller(
        shop_name=request.form["shop_name"],
        description=request.form.get("description", ""),
        category=request.form["category"],
        avatar=uploaded_avatar or request.form.get("avatar", ""),
        telegram=request.form.get("telegram", ""),
        rating="5.0",
        likes=0
    )

    db.session.add(seller)
    db.session.commit()

    return redirect("/seller")


@app.route("/delete-seller/<int:id>")
def delete_seller(id):
    seller = Seller.query.get_or_404(id)
    db.session.delete(seller)
    db.session.commit()
    return redirect("/seller")


@app.route("/add-seller-product", methods=["POST"])
def add_seller_product():
    file = request.files.get("image_file")
    uploaded_image = save_file(file)

    seller_id = int(request.form["seller_id"])
    seller = Seller.query.get_or_404(seller_id)

    product = Product(
        seller_id=seller_id,
        name=request.form["name"],
        price=int(request.form["price"]),
        category=seller.category,
        image=uploaded_image or request.form.get("image", ""),
        description=request.form.get("description", ""),
        size=request.form.get("size", ""),
        brand=request.form.get("brand", ""),
        color=request.form.get("color", ""),
        condition=request.form.get("condition", ""),
        stock=int(request.form.get("stock", 1)),
        vip=True if request.form.get("vip") == "on" else False
    )

    db.session.add(product)
    db.session.commit()

    return redirect("/seller")


@app.route("/shop/<int:seller_id>")
def shop(seller_id):
    seller = Seller.query.get_or_404(seller_id)
    products = Product.query.filter_by(seller_id=seller.id).all()

    return render_template(
        "shop.html",
        products=products,
        shop_name=seller.shop_name,
        rating=seller.rating,
        likes=seller.likes,
        description=seller.description
    )


@app.route("/product/<int:id>")
def product_page(id):
    product = Product.query.get_or_404(id)
    return render_template("product.html", product=product)


@app.route("/search")
def search():
    q = request.args.get("q", "")
    sellers = Seller.query.filter(Seller.shop_name.contains(q)).all()
    return render_template("index.html", sellers=sellers)


@app.route("/admin")
def admin():
    products = Product.query.all()
    orders = Order.query.order_by(Order.id.desc()).all()
    users = User.query.order_by(User.id.desc()).all()
    sellers = Seller.query.all()
    return render_template("admin.html", products=products, orders=orders, users=users, sellers=sellers)


@app.route("/delete-product/<int:id>")
def delete_product(id):
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    return redirect("/seller")


@app.route("/cart")
def cart():
    return render_template("cart.html")


@app.route("/create-order", methods=["POST"])
def create_order():
    items = request.form.get("items", "[]")
    payment = request.form.get("payment", "card")
    user_telegram_id = request.form.get("telegram_id", "")

    cart = json.loads(items)
    total = sum(int(item["price"]) for item in cart)

    order = Order(
        user_telegram_id=user_telegram_id,
        items=items,
        total=total,
        payment=payment,
        status="pending"
    )

    db.session.add(order)
    db.session.commit()

    return redirect("/order-success")


@app.route("/order-success")
def order_success():
    return render_template("order_success.html")


@app.route("/order/<int:id>")
def order_detail(id):
    order = Order.query.get_or_404(id)

    try:
        items = json.loads(order.items)
    except:
        items = []

    return render_template("order_detail.html", order=order, items=items)


@app.route("/order/<int:id>/status/<status>")
def update_order_status(id, status):
    order = Order.query.get_or_404(id)

    if status in ["pending", "paid", "shipped", "delivered"]:
        order.status = status
        db.session.commit()

    return redirect(f"/order/{id}")


@app.route("/chat/<shop>", methods=["GET", "POST"])
def chat(shop):
    if request.method == "POST":
        file = request.files.get("image_file")
        image_url = save_file(file)

        message = Message(
            shop=shop,
            sender=request.form.get("sender", "Buyer"),
            text=request.form.get("text", ""),
            image=image_url
        )

        db.session.add(message)
        db.session.commit()

        return redirect(f"/chat/{shop}")

    messages = Message.query.filter_by(shop=shop).order_by(Message.id.asc()).all()
    return render_template("chat.html", messages=messages, shop=shop)


@app.route("/chat")
def chat_redirect():
    return redirect("/chat/general")


@app.route("/profile")
def profile():
    return render_template("profile.html")


@app.route("/vip")
def vip():
    return render_template("vip.html")


@app.route("/pay-card")
def pay_card():
    return render_template("pay_card.html")


@app.route("/pay-crypto")
def pay_crypto():
    return render_template("pay_crypto.html")


@app.route("/favorites")
def favorites():
    return render_template("favorites.html")


@app.route("/favorites-products")
def favorites_products():
    return render_template("favorites_products.html")


if __name__ == "__main__":
    with app.app_context():
        db.create_all()

        if Seller.query.count() == 0:
            seller1 = Seller(
                shop_name="HOODIE SUPPLY",
                description="Premium hoodies and streetwear.",
                category="Hoodies",
                avatar="https://images.unsplash.com/photo-1523398002811-999ca8dec234",
                telegram="sellerhoodie",
                rating="4.9",
                likes=2183
            )

            seller2 = Seller(
                shop_name="SNEAKER NET",
                description="Sneakers and street fashion drops.",
                category="Sneakers",
                avatar="https://images.unsplash.com/photo-1542291026-7eec264c27ff",
                telegram="sneakernet",
                rating="4.8",
                likes=1261
            )

            db.session.add_all([seller1, seller2])
            db.session.commit()

        if Product.query.count() == 0:
            sellers = Seller.query.all()

            db.session.add_all([
                Product(
                    seller_id=sellers[0].id,
                    name="Black Hoodie",
                    price=120,
                    category="Hoodies",
                    image="https://images.unsplash.com/photo-1521572163474-6864f9cf17ab",
                    description="Black streetwear hoodie.",
                    size="M / L / XL",
                    brand="Reversed",
                    color="Black",
                    condition="New",
                    stock=24
                ),
                Product(
                    seller_id=sellers[1].id,
                    name="Red Sneakers",
                    price=340,
                    category="Sneakers",
                    image="https://images.unsplash.com/photo-1542291026-7eec264c27ff",
                    description="Premium red sneakers.",
                    size="40-45",
                    brand="Sneaker Net",
                    color="Red",
                    condition="New",
                    stock=13
                )
            ])

            db.session.commit()

    print("SERVER STARTED")
    app.run(debug=True)