from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os
import json
import requests
from datetime import datetime

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///fashion.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["UPLOAD_FOLDER"] = "static/uploads"

db = SQLAlchemy(app)

BOT_TOKEN = os.environ.get("8993845960:AAGkror8LMuQ9rb_kYmGbXtALo3p4xm5pFU")

ADMIN_IDS = [
    "1940136851",
    "910641302"
]


def send_admin_notification(text):
    if not BOT_TOKEN:
        return

    for admin_id in ADMIN_IDS:
        try:
            requests.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                data={
                    "chat_id": admin_id,
                    "text": text
                },
                timeout=5
            )
        except Exception as e:
            print("Telegram notify error:", e)


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
    products = Product.query.order_by(Product.id.desc()).all()

    return render_template(
        "index.html",
        sellers=sellers,
        products=products
    )


@app.route("/seller")
def seller_dashboard():
    sellers = Seller.query.all()
    products = Product.query.all()
    orders = Order.query.order_by(Order.id.desc()).all()

    return render_template(
        "seller.html",
        sellers=sellers,
        products=products,
        orders=orders
    )


@app.route("/my-shop")
def my_shop():
    sellers = Seller.query.all()
    products = Product.query.all()

    return render_template(
        "my_shop.html",
        sellers=sellers,
        products=products
    )


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

    send_admin_notification(
        f"🏪 NEW SHOP\n\n"
        f"Shop: {seller.shop_name}\n"
        f"Category: {seller.category}\n"
        f"Telegram: @{seller.telegram}"
    )

    return redirect("/my-shop")


@app.route("/delete-seller/<int:id>")
def delete_seller(id):
    seller = Seller.query.get_or_404(id)

    Product.query.filter_by(seller_id=seller.id).delete()

    db.session.delete(seller)
    db.session.commit()

    return redirect("/my-shop")


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

    send_admin_notification(
        f"👕 NEW ITEM\n\n"
        f"Shop: {seller.shop_name}\n"
        f"Item: {product.name}\n"
        f"Price: ${product.price}\n"
        f"Category: {product.category}"
    )

    return redirect("/my-shop")


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

    return render_template(
        "product.html",
        product=product
    )


@app.route("/search")
def search():
    q = request.args.get("q", "")

    sellers = Seller.query.filter(
        Seller.shop_name.contains(q)
    ).all()

    products = Product.query.filter(
        Product.name.contains(q)
    ).all()

    return render_template(
        "index.html",
        sellers=sellers,
        products=products
    )


@app.route("/admin")
def admin():
    products = Product.query.all()
    orders = Order.query.order_by(Order.id.desc()).all()
    users = User.query.order_by(User.id.desc()).all()
    sellers = Seller.query.all()

    return render_template(
        "admin.html",
        products=products,
        orders=orders,
        users=users,
        sellers=sellers
    )


@app.route("/delete-product/<int:id>")
def delete_product(id):
    product = Product.query.get_or_404(id)

    db.session.delete(product)
    db.session.commit()

    return redirect("/my-shop")


@app.route("/cart")
def cart():
    return render_template("cart.html")


@app.route("/create-order", methods=["POST"])
def create_order():
    items = request.form.get("items", "[]")
    payment = request.form.get("payment", "card")
    user_telegram_id = request.form.get("telegram_id", "")

    cart = json.loads(items)

    total = sum(
        int(item.get("price", 0))
        for item in cart
    )

    order = Order(
        user_telegram_id=user_telegram_id,
        items=items,
        total=total,
        payment=payment,
        status="pending"
    )

    db.session.add(order)
    db.session.commit()

    items_text = ""

    for item in cart:
        items_text += f"- {item.get('name')} — ${item.get('price')}\n"

    send_admin_notification(
        f"🛒 NEW ORDER #{order.id}\n\n"
        f"Total: ${total}\n"
        f"Payment: {payment}\n"
        f"User TG ID: {user_telegram_id}\n\n"
        f"Items:\n{items_text}\n"
        f"Admin: {os.environ.get('WEBAPP_URL', '')}/admin"
    )

    return redirect("/order-success")


@app.route("/order-success")
def order_success():
    return render_template("order_success.html")


@app.route("/my-orders")
def my_orders():
    telegram_id = request.args.get("telegram_id", "")

    if telegram_id:
        orders = Order.query.filter_by(
            user_telegram_id=telegram_id
        ).order_by(Order.id.desc()).all()
    else:
        orders = Order.query.order_by(Order.id.desc()).all()

    parsed_orders = []

    for order in orders:
        try:
            items = json.loads(order.items)
        except Exception:
            items = []

        parsed_orders.append({
            "order": order,
            "items": items
        })

    return render_template(
        "my_orders.html",
        parsed_orders=parsed_orders
    )


@app.route("/order/<int:id>")
def order_detail(id):
    order = Order.query.get_or_404(id)

    try:
        items = json.loads(order.items)
    except Exception:
        items = []

    return render_template(
        "order_detail.html",
        order=order,
        items=items
    )


@app.route("/order/<int:id>/status/<status>")
def update_order_status(id, status):
    order = Order.query.get_or_404(id)

    if status in ["pending", "paid", "shipped", "delivered"]:
        order.status = status
        db.session.commit()

        send_admin_notification(
            f"📦 ORDER #{order.id} STATUS UPDATED\n\n"
            f"New status: {order.status}"
        )

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

        send_admin_notification(
            f"💬 NEW CHAT MESSAGE\n\n"
            f"Shop: {shop}\n"
            f"Sender: {message.sender}\n"
            f"Text: {message.text}"
        )

        return redirect(f"/chat/{shop}")

    messages = Message.query.filter_by(shop=shop).order_by(Message.id.asc()).all()

    return render_template(
        "chat.html",
        messages=messages,
        shop=shop
    )


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


with app.app_context():
    db.create_all()

print("SERVER STARTED")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))

    app.run(
        host="0.0.0.0",
        port=port,
        debug=False
    )