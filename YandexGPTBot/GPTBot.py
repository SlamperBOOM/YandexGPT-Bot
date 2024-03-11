import asyncio
import logging

import requests
from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart

from ModelParamsManager import paramsRouter, read_params_from_disk
from ModelRequestParser import modelRouter
from YandexTokenUtil import retrieve_iam_token

dp = Dispatcher()
dp.include_router(router=paramsRouter)
dp.include_router(router=modelRouter)
start_message = "Привет!\nЧтобы начать пользоваться YandexGPT, напиши о чем ты хочешь узнать."


@dp.message(CommandStart())
async def send_welcome(message: types.Message):
    await message.answer(start_message)


async def main():
    yandex_secret_for_bot_token = "e6qjl7dgihvitpagsshv"
    request = requests.get(
        url="https://payload.lockbox.api.cloud.yandex.net/lockbox/v1/secrets/"
            + yandex_secret_for_bot_token + "/payload",
        headers={'Authorization': 'Bearer ' + retrieve_iam_token()})
    bot = Bot(token=request.json()["entries"][0]["textValue"],
              default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, filename='bot.log',
                        filemode="a", format="%(asctime)s: %(levelname)s: %(message)s")
    read_params_from_disk()
    asyncio.run(main())
