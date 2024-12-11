import asyncio
from aiogram import Bot, Dispatcher, Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from aiogram.types.input_file import FSInputFile
from aiogram.methods import DeleteWebhook

import gen_image
import gen_audio
import os
bot = Bot(token="API_KEY")
dp = Dispatcher(storage=MemoryStorage())
router = Router()

class Generate(StatesGroup):
    _type = State()
    promt = State()

def main_kb():
    kb_list = [
        [KeyboardButton(text="Начать генерацию")]
    ]
    keyboard = ReplyKeyboardMarkup(keyboard=kb_list, resize_keyboard=True, one_time_keyboard=False)
    return keyboard

def gen_type_kb():
    kb_list = [
        [KeyboardButton(text="Изображение"), KeyboardButton(text='Аудио')]
    ]
    keyboard = ReplyKeyboardMarkup(keyboard=kb_list, resize_keyboard=True, one_time_keyboard=True)
    return keyboard

def generate_image(promt):
    print("Image generation is coming soon")

def generate_audio(promt):
    print("Audio generation is coming soon")

@router.message(Command('start'))
async def start_cmd(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        'Доступные команды:\n/generate - сгенерировать изображение или аудио', 
        reply_markup=main_kb()
    )





@router.message(Command('cancel'))
@router.message(F.text.casefold() == 'cancel')
async def cancel_command(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.clear()
    await message.answer(
        "Отменено",
        reply_markup=main_kb(),
    )    

@router.message(Command('generate'))
@router.message(F.text.casefold() == 'начать генерацию')
async def generate_image_command(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Что будем генерировать?", 
        reply_markup=gen_type_kb())
    await state.set_state(Generate._type)

@router.message(F.text.casefold() == 'изображение', Generate._type)
async def capture_img(message: types.Message, state: FSMContext):
    await state.update_data(_type=message.text.casefold())
    await message.answer("Введи промт")
    await state.set_state(Generate.promt)

@router.message(F.text.casefold() == 'аудио', Generate._type)
async def capture_audio(message: types.Message, state: FSMContext):
    await state.update_data(_type=message.text.casefold())
    await message.answer("Введи текст, который нужно озвучить")
    await state.set_state(Generate.promt)

@router.message(F.text, Generate._type)
async def invalid_type(message: types.Message):
    await message.answer("Я тебя не понял :(", reply_markup=gen_type_kb())

@router.message(F.text, Generate.promt)
async def capture_promt(message: types.Message, state: FSMContext, bot: Bot):
    await state.update_data(promt=message.text)
    data = await state.get_data()
    if (data.get('_type') == 'аудио'):
        # await message.answer("Скоро научусь генерировать аудио", reply_markup=main_kb())
        promt = data.get('promt')
        succes = gen_audio.text_to_speech(promt, f"{message.from_user.id}.mp3")

        if (succes):
            try:
                await bot.send_audio(chat_id=message.from_user.id, audio=FSInputFile(f"{message.from_user.id}.mp3"), caption=promt, reply_markup=main_kb())
            except:
                await message.answer("Произошла ошибка при отправке")
            try:
                os.remove(f"{message.from_user.id}.mp3")
            except:
                pass
        else:
            await message.answer("Что-то пошло не так :(", reply_markup=main_kb())

    elif (data.get('_type') == 'изображение'):
        # await message.answer("Скоро научусь генерировать изображения", reply_markup=main_kb())
        await message.answer("Начинаю генерацию. Это может занять 1-2 минуты", reply_markup=ReplyKeyboardRemove())
        promt = data.get('promt')
        succes = gen_image.gen(promt)
        # succes = 1
        if (succes):
            print("Generated")
            try:
            # await bot.delete_message(chat_id=message.chat.id, message_id=msg_id)
                await bot.send_photo(chat_id=message.from_user.id, photo=FSInputFile("image.jpg"), caption=promt, reply_markup=main_kb())
            except:
                await message.answer("Произошла ошибка при отправке")
            try:
                os.remove("image.jpg")
            except:
                pass
        else:
            await message.answer("Что-то пошло не так :(", reply_markup=main_kb())
    else:
        await message.answer("Что-то пошло не так")
    await state.clear()


@router.message(Command['get_github_url'])
async def get_github_url(message: types.Message):
    await message.answer("https://github.com/KhazraT/OOP--laba1", reply_markup=main_kb())





@router.message()
async def echo(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Неверная команда! Для получения списка команда напишите /start", 
        reply_markup=main_kb())


async def main():
    dp.include_router(router=router)
    await bot(DeleteWebhook(drop_pending_updates=True))
    await dp.start_polling(bot, allowed_updates=["message"])

asyncio.run(main())