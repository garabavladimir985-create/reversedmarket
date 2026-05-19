from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardRemove,
    LabeledPrice,
    PreCheckoutQuery
)

import asyncio
import os
import requests


TOKEN = os.environ.get("BOT_TOKEN")

WEBAPP_URL = os.environ.get(
    "WEBAPP_URL",
    "https://reversedmarket.onrender.com"
)

ADMIN_IDS = [
    "1940136851",
    "910641302"
]


async def update_bot_description(bot: Bot):
    while True:
        try:
            res = requests.get(
                f"{WEBAPP_URL}/api/stats",
                timeout=10
            )

            data = res.json()
            total_users = data.get("total_users", 0)

            await bot.set_my_description(
                description=f"👥 {total_users} users in Mini App"
            )

        except Exception as e:
            print("Description update error:", e)

        await asyncio.sleep(300)


async def main():
    bot = Bot(token=TOKEN)
    dp = Dispatcher()

    asyncio.create_task(update_bot_description(bot))

    @dp.message(CommandStart())
    async def start(message: types.Message):
        await message.answer(
            "Меню обновлено ✅",
            reply_markup=ReplyKeyboardRemove()
        )

        kb = ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text="⭐ Buy VIP")
                ]
            ],
            resize_keyboard=True
        )

        await message.answer(
            "ReversedMarket 💎",
            reply_markup=kb
        )

    @dp.message(lambda message: message.text == "/userid")
    async def user_id(message: types.Message):
        await message.answer(
            f"Your Telegram ID:\n\n{message.from_user.id}"
        )

    @dp.message(lambda message: message.text == "/stats")
    async def stats(message: types.Message):
        if str(message.from_user.id) not in ADMIN_IDS:
            await message.answer("⛔ Access denied")
            return

        try:
            res = requests.get(
                f"{WEBAPP_URL}/api/stats",
                timeout=10
            )
            data = res.json()

            await message.answer(
                f"📊 ReversedMarket Stats\n\n"
                f"👥 Users: {data.get('total_users', 0)}"
            )

        except Exception as e:
            await message.answer(f"Stats error: {e}")

    @dp.message(lambda message: message.text == "⭐ Buy VIP")
    async def vip_payment(message: types.Message):
        await message.answer_invoice(
            title="VIP Access",
            description="VIP access to private shops and products",
            payload="vip_access",
            provider_token="",
            currency="XTR",
            prices=[
                LabeledPrice(
                    label="VIP",
                    amount=100
                )
            ]
        )

    @dp.message(lambda message: message.text == "/vip")
    async def vip_command(message: types.Message):
        await vip_payment(message)

    @dp.pre_checkout_query()
    async def pre_checkout(pre_checkout_query: PreCheckoutQuery):
        await pre_checkout_query.answer(ok=True)

    @dp.message(lambda message: message.successful_payment is not None)
    async def successful_payment(message: types.Message):
        await message.answer(
            "✅ VIP activated successfully!"
        )

    print("BOT STARTED")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())