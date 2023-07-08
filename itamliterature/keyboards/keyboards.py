from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from itamliterature.models.models import Category
from itamliterature import config

#region buttons content
button_allbooks = "📚 Все книги"
button_allcategories = "📔 Все категории"
button_nowreading = "📖 Сейчас читаем"
button_vote = "📝 Проголосовать"
button_results = "📊 Результаты голосования"
button_readbooks = "🗃 Прочитанные книги"
button_cancel = "❌ Отмена"
button_admin = "👤 Админка"
button_addbook = "➕ Добавить книгу"
button_addcategory = "➕ Добавить категорию"
button_startvoting = "📝 Начать голосование"
button_stopvoting = "📝 Закончить голосование"
button_addReadingDates = "📅 Добавить даты чтения"
#endregion

def get_categories_keyboard(
    current_category_index: int, categories_count: int, callback_prefix: str
) -> InlineKeyboardMarkup:
    prev_index = current_category_index - 1
    if prev_index < 0:
        prev_index = categories_count - 1
    next_index = current_category_index + 1
    if next_index > categories_count - 1:
        next_index = 0
    keyboard = [
        [
            InlineKeyboardButton("<", callback_data=f"{config.LITRA_CALLBACK_PREFIX}{callback_prefix}{prev_index}"),
            InlineKeyboardButton(
                f"{current_category_index + 1}/{categories_count}", callback_data=" "
            ),
            InlineKeyboardButton(
                ">",
                callback_data=f"{config.LITRA_CALLBACK_PREFIX}{callback_prefix}{next_index}",
            ),
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_books_voting_keyboard(categories: list[Category]) -> InlineKeyboardMarkup:
    keyboard = []
    for category in categories:
        keyboard.append(
            [
                InlineKeyboardButton(
                    category.name,
                    callback_data=f"{config.LITRA_CALLBACK_PREFIX}books_voting_{category.id}",
                )
            ]
        )
    keyboard.append(
            [
                InlineKeyboardButton(
                    button_cancel,
                    callback_data=f"{config.LITRA_CALLBACK_PREFIX}cancel",
                )
            ]
    )
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_main_keyboard(is_admin: bool) -> ReplyKeyboardMarkup:
    keyboard = [
        [
            KeyboardButton(button_allbooks),
            KeyboardButton(button_allcategories),
        ],
        [
            KeyboardButton(button_vote),
        ],
        [
            KeyboardButton(button_results),
        ],
        [
            KeyboardButton(button_readbooks),
            KeyboardButton(button_nowreading)
        ]
    ]
    if is_admin:
        keyboard.append(
            [
                KeyboardButton(button_admin),
            ]
        )
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

def get_cancel_keyboard() -> ReplyKeyboardMarkup:
    keyboard = [
        [
            KeyboardButton(button_cancel),
        ]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

def get_admin_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        InlineKeyboardButton(button_startvoting, callback_data=f"{config.LITRA_CALLBACK_PREFIX}start_voting"),
        InlineKeyboardButton(button_stopvoting, callback_data=f"{config.LITRA_CALLBACK_PREFIX}stop_voting"),
        InlineKeyboardButton(button_addbook, callback_data=f"{config.LITRA_CALLBACK_PREFIX}add_book"),
        InlineKeyboardButton(button_addcategory, callback_data=f"{config.LITRA_CALLBACK_PREFIX}add_category"),
        InlineKeyboardButton(button_addReadingDates, callback_data=f"{config.LITRA_CALLBACK_PREFIX}add_reading_dates")
    ]

    return InlineKeyboardMarkup(inline_keyboard=keyboard)