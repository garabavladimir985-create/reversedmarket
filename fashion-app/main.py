import asyncio
import threading
import os

from bot import main as bot_main
from backend.app import app


def run_flask():
    port = int(os.environ.get("PORT", 8080))

    app.run(
        host="0.0.0.0",
        port=port,
        debug=False,
        use_reloader=False
    )


async def main():
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()

    await bot_main()


if __name__ == "__main__":
    asyncio.run(main())