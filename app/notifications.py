from aiogram import Bot
from config import ADMIN_IDS

async def notify_admins(bot: Bot, message: str):
    """Отправить сообщение всем админам"""
    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(admin_id, message, parse_mode='Markdown')
        except Exception:
            pass  # Админ заблокировал бота или неверный ID


async def notify_new_user(bot: Bot, user):
    """Новый пользователь"""
    text = (
        f"👤 *Новый пользователь*\n\n"
        f"ID: `{user.id}`\n"
        f"Имя: {user.full_name}\n"
        f"Username: @{user.username or 'нет'}"
    )
    await notify_admins(bot, text)


async def notify_payment(bot: Bot, user, product: str, amount: float):
    """Успешная оплата"""
    product_names = {'report': '📄 Отчёт', 'consult': '📞 Консультация'}
    
    text = (
        f"💰 *Оплата получена!*\n\n"
        f"Пользователь: {user.full_name} (@{user.username or 'нет'})\n"
        f"ID: `{user.id}`\n"
        f"Товар: {product_names.get(product, product)}\n"
        f"Сумма: {amount} ₽"
    )
    await notify_admins(bot, text)


async def notify_error(bot: Bot, user, error: str):
    """Ошибка"""
    text = (
        f"⚠️ *Ошибка*\n\n"
        f"Пользователь: {user.full_name} (@{user.username or 'нет'})\n"
        f"ID: `{user.id}`\n"
        f"Ошибка: {error}"
    )
    await notify_admins(bot, text)