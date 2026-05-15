from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    WebAppInfo,
    LabeledPrice,
    PreCheckoutQuery
)

import asyncio
import urllib.parse

TOKEN = "8993845960:AAFtOZ7hXtAnnnhDr0lswED5UdTKJyINCDQ"

WEBAPP_URL = "https://reversedmarket-production.up.railway.app"

bot = Bot(token=TOKEN)
dp = Dispatcher()


@dp.message(CommandStart())
async def start(message: types.Message):
    user_id = message.from_user.id
    first_name = message.from_user.first_name or "User"
    username = message.from_user.username or ""

    name_encoded = urllib.parse.quote(first_name)
    username_encoded = urllib.parse.quote(username)

    app_url = f"{WEBAPP_URL}/?tg_id={user_id}&name={name_encoded}&username={username_encoded}"

    kb = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(
                    text="🛍 Open Fashion App",
                    web_app=WebAppInfo(url=app_url)
                )
            ],
            [
                KeyboardButton(text="⭐ Buy VIP")
            ]
        ],
        resize_keyboard=True
    )

    await message.answer(
        "Fashion Marketplace 👕",
        reply_markup=kb
    )


@dp.message(lambda message: message.text == "⭐ Buy VIP")
async def vip_payment(message: types.Message):
    await message.answer_invoice(
        title="VIP Access",
        description="VIP доступ к приватным магазинам и товарам",
        payload="vip_access",
        provider_token="",
        currency="XTR",
        prices=[
            LabeledPrice(label="VIP", amount=100)
        ]
    )


@dp.pre_checkout_query()
async def pre_checkout(pre_checkout_query: PreCheckoutQuery):
    await pre_checkout_query.answer(ok=True)


@dp.message(lambda message: message.successful_payment is not None)
async def successful_payment(message: types.Message):
    await message.answer("✅ VIP успешно активирован!")


async def main():
    print("BOT STARTED")
    await dp.start_polling(bot)



asyncio.run(main())