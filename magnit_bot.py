from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters import Text
from aiofiles import os
from main import Parser, CITY_CODES

bot = Bot(token='Token')
dp = Dispatcher(bot)


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    start_buttons = CITY_CODES.keys()
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*start_buttons)
    await message.answer(f'Please select a City', reply_markup=keyboard)


@dp.message_handler(Text(equals=CITY_CODES.keys()))
async def sending_data(message: types.Message):
    await message.answer(f'Please waiting...   {message.text}')
    city_code = CITY_CODES[message.text]
    file = Parser().run(city_code=city_code)
    chat_id = message.chat.id
    await bot.send_document(chat_id=chat_id, document=open(file, 'rb'))
    await os.remove(file)


if __name__ == '__main__':
    executor.start_polling(dp)
