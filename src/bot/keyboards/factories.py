"""
Keyboard factories для IQStocker v2.0

Фабрики для создания inline клавиатур
"""

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.bot.lexicon.lexicon_ru import LEXICON_COMMANDS_RU


def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    """Главное меню"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(
            text=LEXICON_COMMANDS_RU["profile"],
            callback_data="profile"
        ),
        InlineKeyboardButton(
            text=LEXICON_COMMANDS_RU["analytics"],
            callback_data="analytics"
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text=LEXICON_COMMANDS_RU["themes"],
            callback_data="themes"
        ),
        InlineKeyboardButton(
            text=LEXICON_COMMANDS_RU["lessons"],
            callback_data="lessons"
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text=LEXICON_COMMANDS_RU["calendar"],
            callback_data="calendar"
        ),
        InlineKeyboardButton(
            text=LEXICON_COMMANDS_RU["faq"],
            callback_data="faq"
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text=LEXICON_COMMANDS_RU["referral"],
            callback_data="referral"
        ),
        InlineKeyboardButton(
            text=LEXICON_COMMANDS_RU["support"],
            callback_data="support"
        ),
    )
    
    return builder.as_markup()


def get_profile_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура профиля"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(
            text=LEXICON_COMMANDS_RU["my_subscription"],
            callback_data="subscription"
        ),
        InlineKeyboardButton(
            text=LEXICON_COMMANDS_RU["tariffs"],
            callback_data="tariffs"
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text=LEXICON_COMMANDS_RU["main_menu"],
            callback_data="main_menu"
        ),
    )
    
    return builder.as_markup()


def get_subscription_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура подписок"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(
            text=LEXICON_COMMANDS_RU["buy_pro"],
            callback_data="buy_pro"
        ),
        InlineKeyboardButton(
            text=LEXICON_COMMANDS_RU["buy_ultra"],
            callback_data="buy_ultra"
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text=LEXICON_COMMANDS_RU["back"],
            callback_data="profile"
        ),
    )
    
    return builder.as_markup()


def get_analytics_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура аналитики"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(
            text=LEXICON_COMMANDS_RU["new_analysis"],
            callback_data="new_analysis"
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text=LEXICON_COMMANDS_RU["my_reports"],
            callback_data="my_reports"
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text=LEXICON_COMMANDS_RU["main_menu"],
            callback_data="main_menu"
        ),
    )
    
    return builder.as_markup()


def get_theme_categories_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура категорий тем"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(
            text=LEXICON_COMMANDS_RU["theme_vectors"],
            callback_data="theme_vectors"
        ),
        InlineKeyboardButton(
            text=LEXICON_COMMANDS_RU["theme_photos"],
            callback_data="theme_photos"
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text=LEXICON_COMMANDS_RU["theme_videos"],
            callback_data="theme_videos"
        ),
        InlineKeyboardButton(
            text=LEXICON_COMMANDS_RU["theme_audio"],
            callback_data="theme_audio"
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text=LEXICON_COMMANDS_RU["theme_templates"],
            callback_data="theme_templates"
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text=LEXICON_COMMANDS_RU["main_menu"],
            callback_data="main_menu"
        ),
    )
    
    return builder.as_markup()


def get_lessons_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура уроков"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(
            text=LEXICON_COMMANDS_RU["lessons_basics"],
            callback_data="lesson_basics"
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text=LEXICON_COMMANDS_RU["lessons_optimization"],
            callback_data="lesson_optimization"
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text=LEXICON_COMMANDS_RU["lessons_sales"],
            callback_data="lesson_sales"
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text=LEXICON_COMMANDS_RU["lessons_technical"],
            callback_data="lesson_technical"
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text=LEXICON_COMMANDS_RU["main_menu"],
            callback_data="main_menu"
        ),
    )
    
    return builder.as_markup()


def get_faq_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура FAQ"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(
            text=LEXICON_COMMANDS_RU["faq_how_start"],
            callback_data="faq_1"
        ),
        InlineKeyboardButton(
            text=LEXICON_COMMANDS_RU["faq_csv"],
            callback_data="faq_2"
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text=LEXICON_COMMANDS_RU["faq_metrics"],
            callback_data="faq_3"
        ),
        InlineKeyboardButton(
            text=LEXICON_COMMANDS_RU["faq_referral"],
            callback_data="faq_referral"
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text=LEXICON_COMMANDS_RU["main_menu"],
            callback_data="main_menu"
        ),
    )
    
    return builder.as_markup()


def get_referral_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура рефералов"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(
            text=LEXICON_COMMANDS_RU["get_referral_link"],
            callback_data="get_referral_link"
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text=LEXICON_COMMANDS_RU["referral_balance"],
            callback_data="referral_balance"
        ),
        InlineKeyboardButton(
            text=LEXICON_COMMANDS_RU["use_points"],
            callback_data="use_points"
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text=LEXICON_COMMANDS_RU["main_menu"],
            callback_data="main_menu"
        ),
    )
    
    return builder.as_markup()


def get_use_points_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для обмена баллов"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(
            text=LEXICON_COMMANDS_RU["exchange_25_discount"],
            callback_data="exchange_25"
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text=LEXICON_COMMANDS_RU["exchange_50_discount"],
            callback_data="exchange_50"
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text=LEXICON_COMMANDS_RU["exchange_pro_free"],
            callback_data="exchange_pro"
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text=LEXICON_COMMANDS_RU["exchange_ultra_free"],
            callback_data="exchange_ultra"
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text=LEXICON_COMMANDS_RU["exchange_channel_access"],
            callback_data="exchange_channel"
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text=LEXICON_COMMANDS_RU["back"],
            callback_data="referral"
        ),
    )
    
    return builder.as_markup()


def get_channel_subscription_keyboard(channel_link: str) -> InlineKeyboardMarkup:
    """Клавиатура проверки подписки на канал"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(
            text=LEXICON_COMMANDS_RU["subscribe_channel"],
            url=channel_link
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text=LEXICON_COMMANDS_RU["check_subscription"],
            callback_data="check_subscription"
        ),
    )
    
    return builder.as_markup()


def get_payment_keyboard(payment_url: str) -> InlineKeyboardMarkup:
    """Клавиатура оплаты"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(
            text=LEXICON_COMMANDS_RU["pay_now"],
            url=payment_url
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text=LEXICON_COMMANDS_RU["back"],
            callback_data="tariffs"
        ),
    )
    
    return builder.as_markup()


def get_back_keyboard(callback_data: str = "main_menu") -> InlineKeyboardMarkup:
    """Кнопка Назад"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(
            text=LEXICON_COMMANDS_RU["back"],
            callback_data=callback_data
        ),
    )
    
    return builder.as_markup()

