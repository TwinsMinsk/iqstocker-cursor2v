"""
Handler для обучающих материалов

Просмотр уроков и обучающего контента
"""

from aiogram import Router
from aiogram.types import CallbackQuery

from src.bot.keyboards.factories import get_back_keyboard, get_lessons_keyboard
from src.bot.lexicon.lexicon_ru import LEXICON_RU
from src.config.logging import get_logger

logger = get_logger(__name__)
router = Router(name=__name__)


@router.callback_query(lambda c: c.data == "lessons")
async def callback_lessons(callback: CallbackQuery):
    """Обработчик раздела уроков"""
    await callback.message.edit_text(
        LEXICON_RU["lessons_start"],
        reply_markup=get_lessons_keyboard(),
    )
    await callback.answer()


@router.callback_query(lambda c: c.data.startswith("lesson_"))
async def callback_lesson_content(callback: CallbackQuery):
    """Обработчик просмотра урока"""
    lesson_map = {
        "lesson_basics": {
            "title": "Основы Adobe Stock",
            "content": "Регистрация и первые шаги, требования к контенту, процесс модерации",
            "key_points": "• Регистрация в Adobe Stock\n• Требования к контенту\n• Процесс модерации",
            "homework": "Зарегистрируйся и загрузи свой первый контент",
        },
        "lesson_optimization": {
            "title": "Оптимизация портфолио",
            "content": "Правильный выбор тем, теггинг и SEO, анализ конкурентов",
            "key_points": "• Выбор актуальных тем\n• SEO оптимизация\n• Анализ конкурентов",
            "homework": "Оптимизируй свои первые 10 активов",
        },
        "lesson_sales": {
            "title": "Увеличение продаж",
            "content": "Тренды рынка, маркетинг стоков, работа с коллекциями",
            "key_points": "• Следи за трендами\n• Создавай коллекции\n• Оптимизируй теги",
            "homework": "Создай свою первую коллекцию",
        },
        "lesson_technical": {
            "title": "Технические навыки",
            "content": "Обработка фото/видео, векторная графика, AI-генерация",
            "key_points": "• Обработка контента\n• Векторная графика\n• AI-генерация",
            "homework": "Освой один из инструментов обработки",
        },
    }
    
    lesson_data = lesson_map.get(callback.data)
    if not lesson_data:
        await callback.answer("Урок не найден", show_alert=True)
        return
    
    await callback.message.edit_text(
        LEXICON_RU["lesson_content"].format(
            lesson_title=lesson_data["title"],
            lesson_content=lesson_data["content"],
            key_points=lesson_data["key_points"],
            homework=lesson_data["homework"],
        ),
        reply_markup=get_back_keyboard("lessons"),
    )
    await callback.answer()

