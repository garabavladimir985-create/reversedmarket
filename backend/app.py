from flask import Flask, render_template, request, redirect, jsonify
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

ADMIN_IDS = ["1940136851", "910641302"]
ADMIN_KEY = "admin123"

os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)


def is_admin(tg_id=""):
    return str(tg_id) in ADMIN_IDS


def is_admin_key(key=""):
    return str(key) == ADMIN_KEY


def notify_admins(text):
    if not BOT_TOKEN:
        return

    for admin_id in ADMIN_IDS:
        try:
            requests.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                data={"chat_id": admin_id, "text": text},
                timeout=5
            )
        except Exception as e:
            print("Notify error:", e)


class Seller(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    owner_telegram_id = db.Column(db.String(120))
    shop_name = db.Column(db.String(120))
    description = db.Column(db.Text)
    category = db.Column(db.String(50))
    avatar = db.Column(db.String(500))
    telegram = db.Column(db.String(120))
    rating = db.Column(db.String(20), default="5.0")
    likes = db.Column(db.Integer, default=0)
    verified = db.Column(db.Boolean, default=False)


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
    last_seen = db.Column(db.DateTime)
    id = db.Column(db.Integer, primary_key=True)
    telegram_id = db.Column(db.String(120), unique=True)
    name = db.Column(db.String(120))
    username = db.Column(db.String(120))
    telegram = db.Column(db.String(120))
    city = db.Column(db.String(120))
    avatar = db.Column(db.String(500))
    is_vip = db.Column(db.Boolean, default=False)
    is_verified = db.Column(db.Boolean, default=False)


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    shop = db.Column(db.String(120), default="general")
    sender = db.Column(db.String(120))
    sender_tg_id = db.Column(db.String(120))
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
    delivery = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


def save_file(file):
    if not file or file.filename == "":
        return None

    filename = secure_filename(file.filename)
    path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(path)

    return "/static/uploads/" + filename


@app.route("/api/telegram-auth", methods=["POST"])
def telegram_auth():
    data = request.get_json() or {}

    telegram_id = str(data.get("id", ""))
    name = data.get("first_name", "")
    username = data.get("username", "")
    avatar = data.get("photo_url", "")

    if not telegram_id:
        return jsonify({"ok": False})

    user = User.query.filter_by(telegram_id=telegram_id).first()

    if not user:
        user = User(
            telegram_id=telegram_id,
            name=name,
            username=username,
            telegram=username,
            avatar=avatar,
            is_vip=False,
            is_verified=False
        )
        db.session.add(user)
    else:
        user.name = name
        user.username = username
        user.telegram = username
        user.avatar = avatar
        user.last_seen = datetime.utcnow()
    db.session.commit()

    return jsonify({
        "ok": True,
        "telegram_id": user.telegram_id,
        "name": user.name,
        "username": user.username,
        "avatar": user.avatar,
        "is_vip": user.is_vip,
        "is_verified": user.is_verified,
        "is_admin": is_admin(user.telegram_id)
    })


@app.route("/")
def home():
    q = request.args.get("q", "")
    category = request.args.get("category", "")

    products_query = Product.query

    if q:
        products_query = products_query.filter(Product.name.contains(q))

    if category:
        products_query = products_query.filter(Product.category == category)

    products = products_query.order_by(Product.id.desc()).all()
    sellers = Seller.query.order_by(Seller.id.desc()).all()

    return render_template("index.html", products=products, sellers=sellers)


@app.route("/catalog")
def catalog():
    q = request.args.get("q", "")
    category = request.args.get("category", "")
    brand = request.args.get("brand", "")
    size = request.args.get("size", "")
    max_price = request.args.get("max_price", "")

    products_query = Product.query

    if q:
        products_query = products_query.filter(
            Product.name.contains(q) | Product.brand.contains(q)
        )

    if category:
        products_query = products_query.filter(Product.category == category)

    if brand:
        products_query = products_query.filter(Product.brand.contains(brand))

    if size:
        products_query = products_query.filter(Product.size.contains(size))

    if max_price:
        try:
            products_query = products_query.filter(Product.price <= int(max_price))
        except:
            pass

    products = products_query.order_by(Product.id.desc()).all()

    categories = db.session.query(Product.category).distinct().all()
    categories = [c[0] for c in categories if c[0]]

    brands = db.session.query(Product.brand).distinct().all()
    brands = [b[0] for b in brands if b[0]]

    return render_template(
        "catalog.html",
        products=products,
        categories=categories,
        brands=brands,
        q=q,
        category=category,
        brand=brand,
        size=size,
        max_price=max_price
    )


@app.route("/my-shop")
def my_shop():
    tg_id = request.args.get("tg_id", "")
    key = request.args.get("key", "")

    admin = is_admin(tg_id) or is_admin_key(key)

    user = User.query.filter_by(telegram_id=tg_id).first() if tg_id else None

    can_create = admin or (user and (user.is_vip or user.is_verified))

    seller = Seller.query.filter_by(owner_telegram_id=tg_id).first() if tg_id else None

    products = []

    if seller:
        products = Product.query.filter_by(
            seller_id=seller.id
        ).order_by(Product.id.desc()).all()

    return render_template(
        "my_shop.html",
        tg_id=tg_id,
        key=key,
        admin=admin,
        user=user,
        can_create=can_create,
        seller=seller,
        products=products
    )
@app.route("/create-shop", methods=["POST"])
def create_shop():
    tg_id = request.form.get("tg_id", "")
    key = request.form.get("key", "")

    user = User.query.filter_by(telegram_id=tg_id).first() if tg_id else None
    admin = is_admin(tg_id) or is_admin_key(key)

    if not admin and not (user and (user.is_vip or user.is_verified)):
        return "ACCESS DENIED", 403

    old = Seller.query.filter_by(owner_telegram_id=tg_id).first()
    if old:
        return redirect(f"/my-shop?tg_id={tg_id}")

    file = request.files.get("avatar_file")
    avatar = save_file(file)

    seller = Seller(
        owner_telegram_id=tg_id,
        shop_name=request.form.get("shop_name"),
        description=request.form.get("description", ""),
        category=request.form.get("category", "Fashion"),
        avatar=avatar or request.form.get("avatar", ""),
        telegram=request.form.get("telegram", ""),
        rating="5.0",
        likes=0,
        verified=admin
    )

    db.session.add(seller)
    db.session.commit()

    notify_admins(
        f"🏪 NEW SHOP\n\n"
        f"Shop: {seller.shop_name}\n"
        f"Owner TG: {tg_id}\n"
        f"Telegram: @{seller.telegram}"
    )

    return redirect(f"/my-shop?tg_id={tg_id}")


@app.route("/add-product", methods=["POST"])
def add_product():
    tg_id = request.form.get("tg_id", "")
    key = request.form.get("key", "")

    admin = is_admin(tg_id) or is_admin_key(key)

    seller_id = request.form.get("seller_id")

    if seller_id and admin:
        seller = Seller.query.get_or_404(int(seller_id))
    else:
        seller = Seller.query.filter_by(owner_telegram_id=tg_id).first()

    if not seller:
        return "NO SHOP", 403

    if not admin and str(seller.owner_telegram_id) != str(tg_id):
        return "ACCESS DENIED", 403

    file = request.files.get("image_file")
    uploaded_image = save_file(file)

    product = Product(
        seller_id=seller.id,
        name=request.form.get("name"),
        price=int(request.form.get("price", 0)),
        category=request.form.get("category", seller.category),
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

    notify_admins(
        f"👕 NEW PRODUCT\n\n"
        f"Shop: {seller.shop_name}\n"
        f"Product: {product.name}\n"
        f"Price: €{product.price}"
    )

    return redirect(f"/my-shop?tg_id={tg_id}")


@app.route("/delete-product/<int:id>")
def delete_product(id):
    tg_id = request.args.get("tg_id", "")
    key = request.args.get("key", "")

    product = Product.query.get_or_404(id)
    seller = Seller.query.get_or_404(product.seller_id)

    if not is_admin(tg_id) and not is_admin_key(key) and str(seller.owner_telegram_id) != str(tg_id):
        return "ACCESS DENIED", 403

    db.session.delete(product)
    db.session.commit()

    return redirect(f"/my-shop?tg_id={tg_id}")


@app.route("/shop/<int:seller_id>")
def shop(seller_id):
    seller = Seller.query.get_or_404(seller_id)
    products = Product.query.filter_by(seller_id=seller.id).order_by(Product.id.desc()).all()

    return render_template("shop.html", seller=seller, products=products)


@app.route("/product/<int:id>")
def product_page(id):
    product = Product.query.get_or_404(id)
    seller = Seller.query.get(product.seller_id)

    return render_template("product.html", product=product, seller=seller)


@app.route("/cart")
def cart():
    return render_template("cart.html")


@app.route("/create-order", methods=["POST"])
def create_order():
    items = request.form.get("items", "[]")
    payment = request.form.get("payment", "card")
    user_telegram_id = request.form.get("telegram_id", "")

    delivery = {
        "full_name": request.form.get("full_name", ""),
        "phone": request.form.get("phone", ""),
        "country": request.form.get("country", ""),
        "city": request.form.get("city", ""),
        "address": request.form.get("address", ""),
        "postal_code": request.form.get("postal_code", ""),
        "comment": request.form.get("comment", "")
    }

    cart = json.loads(items)

    total = sum(
        int(float(item.get("price", 0))) * int(item.get("qty", 1))
        for item in cart
    )

    order = Order(
        user_telegram_id=user_telegram_id,
        items=items,
        total=total,
        payment=payment,
        status="pending",
        delivery=json.dumps(delivery, ensure_ascii=False)
    )

    db.session.add(order)
    db.session.commit()

    items_text = ""
    for item in cart:
        items_text += f"- {item.get('name')} × {item.get('qty', 1)} — €{item.get('price')}\n"

    notify_admins(
        f"🛒 NEW ORDER #{order.id}\n\n"
        f"Total: €{total}\n"
        f"Payment: {payment}\n"
        f"TG ID: {user_telegram_id}\n\n"
        f"👤 {delivery['full_name']}\n"
        f"📞 {delivery['phone']}\n"
        f"📍 {delivery['country']}, {delivery['city']}, {delivery['address']}\n"
        f"Postal: {delivery['postal_code']}\n\n"
        f"Items:\n{items_text}"
    )

    return redirect("/order-success")


@app.route("/order-success")
def order_success():
    return render_template("order_success.html")


@app.route("/my-orders")
def my_orders():
    tg_id = request.args.get("telegram_id", "")
    orders = Order.query.filter_by(user_telegram_id=tg_id).order_by(Order.id.desc()).all() if tg_id else []

    parsed_orders = []

    for order in orders:
        try:
            items = json.loads(order.items)
        except:
            items = []

        parsed_orders.append({"order": order, "items": items})

    return render_template("my_orders.html", parsed_orders=parsed_orders)


@app.route("/order/<int:id>")
def order_detail(id):
    order = Order.query.get_or_404(id)

    try:
        items = json.loads(order.items)
    except:
        items = []

    try:
        delivery = json.loads(order.delivery or "{}")
    except:
        delivery = {}

    return render_template("order_detail.html", order=order, items=items, delivery=delivery)


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
            sender=request.form.get("sender", "Telegram User"),
            sender_tg_id=request.form.get("sender_tg_id", ""),
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


@app.route("/favorites-products")
def favorites_products():
    return render_template("favorites_products.html")


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


@app.route("/admin")
def admin():
    key = request.args.get("key", "")

    if not is_admin_key(key):
        return "ACCESS DENIED", 403

    from datetime import timedelta

    products = Product.query.order_by(Product.id.desc()).all()
    orders = Order.query.order_by(Order.id.desc()).all()
    users = User.query.order_by(User.id.desc()).all()
    sellers = Seller.query.order_by(Seller.id.desc()).all()

    online_users = User.query.filter(
        User.last_seen >= datetime.utcnow() - timedelta(minutes=5)
    ).count()

    total_users = User.query.count()

    return render_template(
        
        "admin.html",
        products=products,
        orders=orders,
        users=users,
        sellers=sellers,
        online_users=online_users,
        total_users=total_users,
        key=key
    )
@app.route("/user/<int:id>/vip/<status>")
def update_user_vip(id, status):
    key = request.args.get("key", "")

    if not is_admin_key(key):
        return "ACCESS DENIED", 403

    user = User.query.get_or_404(id)

    if status == "on":
        user.is_vip = True
    elif status == "off":
        user.is_vip = False

    db.session.commit()

    return redirect("/admin?key=admin123")


@app.route("/user/<int:id>/verified/<status>")
def update_user_verified(id, status):
    key = request.args.get("key", "")

    if not is_admin_key(key):
        return "ACCESS DENIED", 403

    user = User.query.get_or_404(id)

    if status == "on":
        user.is_verified = True
    elif status == "off":
        user.is_verified = False

    db.session.commit()

    return redirect("/admin?key=admin123")

def ensure_columns():
    with db.engine.connect() as conn:                               
        try:
            conn.exec_driver_sql("ALTER TABLE seller ADD COLUMN owner_telegram_id VARCHAR(120)")
        except:
            pass

        try:
            conn.exec_driver_sql("ALTER TABLE seller ADD COLUMN verified BOOLEAN DEFAULT 0")
        except:
            pass

        try:
            conn.exec_driver_sql("ALTER TABLE user ADD COLUMN is_verified BOOLEAN DEFAULT 0")
        except:
            pass

        try:
            conn.exec_driver_sql("ALTER TABLE message ADD COLUMN sender_tg_id VARCHAR(120)")
        except:
            pass

        try:
            conn.exec_driver_sql("ALTER TABLE \"order\" ADD COLUMN delivery TEXT")
        except:
            pass
        try:
            conn.exec_driver_sql("ALTER TABLE user ADD COLUMN last_seen DATETIME")
        except:
            pass


with app.app_context():
    db.create_all()
    ensure_columns()

print("SERVER STARTED")
@app.route("/api/stats")
def api_stats():
    total_users = User.query.count()
    return jsonify({
        "total_users": total_users
    })
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False)