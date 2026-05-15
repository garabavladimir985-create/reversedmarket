if __name__ == "__main__":
    import os

    with app.app_context():
        db.create_all()

    print("SERVER STARTED")

    port = int(os.environ.get("PORT", 8080))

    app.run(
        host="0.0.0.0",
        port=port,
        debug=False
    )