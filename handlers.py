from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart, Command
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

@router.message(Command("help"))
async def cmd_help(message: Message, bot: Bot):
    help_text = (
        "🤖 **Botdan foydalanish:**\n\n"
        "🎬 Kino qidirish uchun botga kino kodini yuboring (masalan: `123`).\n"
    )
    if message.from_user.id in ADMIN_IDS:
        help_text += (
            "\n👨‍💻 **Admin huquqlari:**\n"
            "➕ Kino qo'shish: Videoni yuboring va izohiga (caption) kodini yozing.\n"
            "🗑 Kino o'chirish: `/del kod` (masalan: `/del 123`)\n"
        )
    await message.answer(help_text, parse_mode="Markdown")

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
    
    # Agar izoh (caption) kiritilgan bo'lsa va uning birinchi so'zi raqam (kod) bo'lsa
    if caption:
        first_word = caption.split()[0]
        if first_word.isdigit():
            code = first_word
            description = caption.strip() # butun izohni saqlaymiz
            
            # videoni bazaga qo'shish
            await database.add_movie(code=code, file_id=file_id, description=description)
            await message.answer(f"✅ Video bazaga muvaffaqiyatli qo'shildi!\n\n🎬 Kod: {code}\n📝 Ma'lumotlar saqlandi.")
            return

    # Kod topilmasa yoki noto'g'ri bo'lsa
    await message.answer(
        f"📹 Video qabul qilindi lekin bazaga qo'shilmadi!\n\n"
        f"Buning File ID raqami:\n`{file_id}`\n\n"
        f"💡 Maslahat: Videoni bazaga avtomatik qo'shish uchun, videoni botga yuborayotganda **izoh (caption)** qismining eng boshiga **kino kodini** (masalan: `111`) yozing. Undan keyin pastidan kino nomi va boshqa ma'lumotlarni yozishingiz mumkin.",
        parse_mode="Markdown"
    )

@router.message(Command("del"))
async def cmd_delete_movie(message: Message, bot: Bot):
    if message.from_user.id not in ADMIN_IDS:
        return
        
    parts = message.text.split()
    if len(parts) != 2:
        await message.answer("❌ Xato format. Foydalanish: `/del kod` (masalan: `/del 123`)", parse_mode="Markdown")
        return
        
    code = parts[1]
    deleted = await database.delete_movie(code)
    
    if deleted:
        await message.answer(f"✅ {code}-kodli kino bazadan o'chirildi!")
    else:
        await message.answer(f"❌ {code}-kodli kino bazada topilmadi.")

@router.message(F.text)
async def process_movie_code(message: Message, bot: Bot):
    code = message.text.strip()
    
    # Agar matn "/" bilan boshlansa, uni kino kodi deb qabul qilmaymiz
    if code.startswith('/'):
        return
        
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
