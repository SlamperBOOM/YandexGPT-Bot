import asyncio
import logging

from aiogram import Router, types

from MDToHTMLParser import telegram_format
from YandexGPTAPI import YaGPTApi
from YandexTokenUtil import retrieve_iam_token
from ModelParamsManager import get_params_for_chat

modelRouter = Router()
max_msg_size = 4096


def parse_msg(message):
    result = []
    msg = ""
    for line in message.split("\n"):
        if len(line) > max_msg_size:
            for word in line.split(" "):
                if len(msg + word) > max_msg_size:
                    result.append(msg)
                    msg = ""
                msg += word + " "
        if len(msg + line) > max_msg_size:
            result.append(msg)
            msg = ""
        msg += line + "\n"
    if len(msg) > 0:
        result.append(msg)
    return result


@modelRouter.message()
async def model_request(message: types.Message):
    timed_msg = await message.answer("Модель генерирует ответ")
    logging.info("User message: " + message.text)
    settings = get_params_for_chat(message.chat.id)
    yandexgpt = YaGPTApi(message.text, retrieve_iam_token(), settings.model_name, settings.temp, settings.context)
    yandexgpt.start()
    while True:
        await asyncio.sleep(3)
        if yandexgpt.retrieve_error() is not None:
            await timed_msg.delete()
            await message.answer("Возникла ошибка при выполнении запроса к модели, попробуйте позже")
            break
        elif yandexgpt.retrieve_result() is None:
            await message.chat.do("typing")
        else:
            break
    answer = ""
    if yandexgpt.retrieve_result() is not None:
        answer = yandexgpt.retrieve_result()
    try:
        await timed_msg.delete()
        if len(answer) == 0:
            await message.answer("Модель ничего не ответила. Задайте другой вопрос")
        elif len(answer) > max_msg_size:
            split_msg = parse_msg(answer)
            for part in split_msg:
                part = telegram_format(part)
                if len(part) > 0:
                    logging.info("Writing part: " + part)
                    await message.answer(part)
        else:
            answer = telegram_format(answer)
            logging.debug("Writing answer: " + answer)
            await message.answer(answer)
    except Exception as err:
        logging.warning(err, exc_info=True)
        await message.answer("Возникла ошибка при обработке ответа. Попробуйте задать вопрос по-другому")
