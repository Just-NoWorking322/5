from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
import asyncio, logging
from config import token

logging.basicConfig(level=logging.INFO)
bot = Bot(token=token)
dp = Dispatcher()

CATEGORIES = {
    'Компьютеры': {
        'Ноутбук': 50000,
        'ПК': 70000,
        'Моноблок': 60000,
        'Планшет': 15000
    },
    'Комплектующие': {
        'Оперативная память': 3000,
        'Процессор': 7000,
        'Видеокарта': 15000,
        'Жесткий диск': 4000,
        'Материнская плата': 8000,
        'Мышка': 1000,
        'Клавиатура': 1500,
        'Блок питания': 2000,
        'Монитор': 5000,
        'Сетевой адаптер': 1000,
        'Система охлаждения': 2500,
        'USB хаб': 800
    },
    'Программное обеспечение': {
        'Windows 10': 2000,
        'Microsoft Office': 4000,
        'Антивирус': 1500,
        'Photoshop': 6000,
        'Autocad': 12000,
        '1C': 5000
    },
    'Телефоны': {
        'iPhone 14': 80000,
        'Samsung Galaxy S22': 55000,
        'Xiaomi Redmi Note 12': 18000,
        'Huawei P40': 40000
    },
    'Аксессуары': {
        'Чехол для телефона': 1000,
        'Зарядное устройство': 500,
        'Беспроводные наушники': 2500,
        'Флешка 64GB': 1000,
        'Пауэрбанк': 1500
    },
    'Техника для дома': {
        'Стиральная машина': 25000,
        'Холодильник': 30000,
        'Микроволновая печь': 7000,
        'Пылесос': 8000,
        'Кофемашина': 15000
    },
    'Игры и консоли': {
        'PlayStation 5': 50000,
        'Xbox Series X': 45000,
        'Nintendo Switch': 30000,
        'FIFA 23': 2500,
        'Call of Duty: Modern Warfare II': 3500
    },
    'Фото и видео': {
        'Камера Canon EOS 80D': 50000,
        'Фотоаппарат Nikon D3500': 25000,
        'Дрон DJI Mini 2': 35000,
        'Экшн-камера GoPro HERO10': 40000
    },
    'Музыка и звук': {
        'Гарнитура для ПК': 2000,
        'Стереосистема': 15000,
        'Акустическая система': 8000,
        'Микрофон для записи': 2500,
        'Портативная колонка': 3000
    },
    'Спортивные товары': {
        'Тренажер для дома': 15000,
        'Велосипед': 20000,
        'Ракетки для тенниса': 1500,
        'Мяч для футбола': 1000,
        'Кроссовки для бега': 3000
    },
    'Книги': {
        'Гарри Поттер и философский камень': 800,
        'Война и мир': 1200,
        '1984 Джорджа Оруэлла': 600,
        'Мастер и Маргарита': 900,
        'Преступление и наказание': 1000
    }
}

orders = {}

@dp.message(Command("start"))
async def start(message: types.Message):
    builder = InlineKeyboardBuilder()
    for category in CATEGORIES.keys():
        builder.button(text=category, callback_data=f"category_{category}")
    builder.adjust(1)

    await message.answer(
        "Добро пожаловать в онлайн-магазин! Выберите категорию товаров:",
        reply_markup=builder.as_markup()
    )

@dp.callback_query(F.data.startswith("category_"))
async def show_products(callback: types.CallbackQuery):
    category = callback.data.split("_")[1]
    products = CATEGORIES[category]

    builder = InlineKeyboardBuilder()
    for product, price in products.items():
        builder.button(text=f"{product} - {price} сом", callback_data=f"product_{category}_{product}")
    builder.adjust(1)

    await callback.message.answer(
        f"Категория: {category}. Выберите товар:",
        reply_markup=builder.as_markup()
    )

@dp.callback_query(F.data.startswith("product_"))
async def confirm_product(callback: types.CallbackQuery):
    _, category, product = callback.data.split("_")
    price = CATEGORIES[category][product]

    orders[callback.from_user.id] = {
        "category": category,
        "product": product,
        "price": price,
        "address": None,
        "phone": None
    }

    builder = InlineKeyboardBuilder()
    builder.button(text="Подтвердить заказ", callback_data="confirm_order")
    builder.button(text="Отмена", callback_data="cancel_order")
    builder.adjust(1)

    await callback.message.answer(
        f"Вы выбрали: {product} из категории {category}. Цена: {price} сом.\nПодтвердите заказ?",
        reply_markup=builder.as_markup()
    )

@dp.callback_query(F.data == "confirm_order")
async def get_shipping_info(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    if user_id in orders:
        order = orders[user_id]
        category, product, price = order["category"], order["product"], order["price"]

        await callback.message.answer("Введите адрес доставки:")

        @dp.message()
        async def get_address(message: types.Message):
            orders[user_id]["address"] = message.text
            await message.answer("Введите контактный номер телефона:")

            @dp.message()
            async def get_phone(message: types.Message):
                orders[user_id]["phone"] = message.text
                address = orders[user_id]["address"]
                phone = orders[user_id]["phone"]

                await message.answer(
                    f"Ваш заказ:\nКатегория: {category}\nТовар: {product}\nЦена: {price} сом\n"
                    f"Адрес доставки: {address}\nКонтактный номер: {phone}\n\nПодтвердите заказ?",
                    reply_markup=InlineKeyboardBuilder()
                        .button(text="Подтвердить", callback_data="final_confirm")
                        .button(text="Отменить", callback_data="cancel_order")
                        .adjust(1)
                        .as_markup()
                )

@dp.callback_query(F.data == "final_confirm")
async def final_confirm_order(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    if user_id in orders:
        order = orders[user_id]
        category, product, price = order["category"], order["product"], order["price"]
        address = order["address"]
        phone = order["phone"]

        del orders[user_id]

        await callback.message.answer(
            f"Ваш заказ подтверждён!\nКатегория: {category}\nТовар: {product}\nЦена: {price} сом\n"
            f"Адрес доставки: {address}\nКонтактный номер: {phone}\nСпасибо за покупку!"
        )

@dp.callback_query(F.data == "cancel_order")
async def cancel_order(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    if user_id in orders:
        del orders[user_id]
        await callback.message.answer("Ваш заказ отменён.")

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
