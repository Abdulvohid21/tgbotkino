from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart
from aiogram.exceptions import TelegramBadRequest
from config import MANDATORY_CHANNELS, ADMIN_IDS
import database

router = Router()

def get_subscription_keyboard() -> InlineKeyboardMarkup:
    """Generate keyboard with mandatory channels."""
    buttons = []
    for channel in MANDATORY_CHANNELS:
        buttons.append([InlineKeyboardButton(text=channel["name"], url=channel["url"])])
    
    buttons.append([InlineKeyboardButton(text="Obunani tekshirish", callback_data="check_sub")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

async def check_user_subscriptions(bot: Bot, user_id: int) -> bool:
    """Check if the user is subscribed to all mandatory channels."""
    if not MANDATORY_CHANNELS:
        return True # No mandatory channels configured
        
    for channel in MANDATORY_CHANNELS:
        try:
            member = await bot.get_chat_member(chat_id=channel["id"], user_id=user_id)
            if member.status in ["left", "kicked"]:
                return False
        except TelegramBadRequest:
            # Bot is likely not an admin in the channel, or channel ID is wrong
            print(f"Error checking channel {channel['id']}. Is the bot an admin?")
            return False
        except Exception as e:
            print(f"Unexpected error checking subscription: {e}")
            return False
            
    return True

@router.message(CommandStart())
async def cmd_start(message: Message, bot: Bot):
    is_subscribed = await check_user_subscriptions(bot, message.from_user.id)
    if not is_subscribed:
        await message.answer(
            "Botdan foydalanish uchun quyidagi kanallarga obuna bo'lishingiz shart!\n\nSiz shartlarni bajarmadingiz:",
            reply_markup=get_subscription_keyboard()
        )
        return

    await message.answer("Assalomu alaykum! Kino kodini yuboring:")

@router.callback_query(F.data == "check_sub")
async def check_sub_handler(callback: CallbackQuery, bot: Bot):
    is_subscribed = await check_user_subscriptions(bot, callback.from_user.id)
    
    if is_subscribed:
        await callback.message.delete()
        await callback.message.answer("Obuna tasdiqlandi! Endi kino kodini yuborishingiz mumkin.")
    else:
        await callback.answer("Siz barcha kanallarga obuna bo'lmadingiz!", show_alert=True)

@router.message(F.video)
async def handle_video_message(message: Message, bot: Bot):
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("❌ Sizda videolarni bazaga qo'shish huquqi yo'q!")
        return

    file_id = message.video.file_id
    caption = message.caption
    
    # Agar izohda faqat raqam (kod) yozilgan bo'lsa, bazaga saqlaymiz
    if caption and caption.strip().isdigit():
        code = caption.strip()
        # videoni bazaga qo'shish
        await database.add_movie(code=code, file_id=file_id, description=f"Kino kodi: {code}")
        await message.answer(f"✅ Video bazaga muvaffaqiyatli qo'shildi!\n\n🎬 Kod: {code}")
    else:
        # Kod yozilmagan bo'lsa, shunchaki file_id ni qaytaramiz
        await message.answer(
            f"📹 Video qabul qilindi!\n\n"
            f"Buning File ID raqami:\n`{file_id}`\n\n"
            f"💡 Maslahat: Videoni bazaga avtomatik qo'shish uchun, videoni botga yuborayotganda **izoh (caption)** qismiga faqat kino kodini (masalan: `111`) yozing.",
            parse_mode="Markdown"
        )

@router.message(F.text)
async def process_movie_code(message: Message, bot: Bot):
    code = message.text.strip()
    
    # 1. Check subscription first
    is_subscribed = await check_user_subscriptions(bot, message.from_user.id)
    if not is_subscribed:
        await message.answer(
            "Siz shartlarni bajarmadingiz! Quyidagi kanallarga obuna bo'ling:",
            reply_markup=get_subscription_keyboard()
        )
        return

    # 2. Check if movie exists in database
    movie = await database.get_movie(code)
    
    if movie:
        file_id = movie["file_id"]
        description = movie["description"]
        
        try:
            # Try to send as video first
            await message.answer_video(video=file_id, caption=description)
        except Exception:
            # If it fails (e.g. not a file_id but a link or text)
            await message.answer(f"{description}\n\nFayl/Havola: {file_id}")
    else:
        await message.answer("Bunday kod bilan kino topilmadi. Boshqa kod yuborib ko'ring.")
