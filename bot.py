import logging
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

logging.basicConfig(level=logging.INFO)
API_TOKEN = '8507662803:AAG8-XD2VjqqZYyvB7zrlShBaZVTbODw8yg'
UPI_ID = '7229934438@axl'
SUPPORT_USERNAME = 'CHEAT_VIPPP'
ADMIN_ID = 6649097946

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

users_db = {} 
used_utrs = set()
stock_db = {
    "phantom_x": ["KEY_PHTX_1", "KEY_PHTX_2"],
    "silent_x": ["KEY_SLTX_1"],
    "x_rag": [],
    "troll_mods": ["KEY_TRL_1"],
    "drip_wire": ["KEY_DRP_1"],
    "panthom_reg": ["KEY_REG_1"],
    "bala_mods": ["KEY_BALA_1"]
}

class BotStates(StatesGroup):
    entering_utr = State()
    custom_amount = State()

def init_user(user_id):
    if user_id not in users_db:
        users_db[user_id] = {"balance": 0.0, "total_spent": 0.0, "keys": [], "ref_by": None}

def get_main_menu(balance=0.0):
    buttons = [
        [InlineKeyboardButton(text="🛍️ Shop / Store Product", callback_data="shop_menu")],
        [InlineKeyboardButton(text="🔄 Check Update", callback_data="check_update"),
         InlineKeyboardButton(text="➕ Add Balance", callback_data="add_balance")],
        [InlineKeyboardButton(text="👤 My Profile + Key History", callback_data="my_profile")],
        [InlineKeyboardButton(text="🔗 Referral", callback_data="referral"),
         InlineKeyboardButton(text="📖 How To Use", callback_data="how_to_use")],
        [InlineKeyboardButton(text="🚀 Upgrade To Reseller", callback_data="upgrade_reseller")],
        [InlineKeyboardButton(text="📞 Support", callback_data="support"),
         InlineKeyboardButton(text="🎁 Lucky", callback_data="lucky_spin")],
        [InlineKeyboardButton(text="🌐 Language", callback_data="language_menu")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_device_menu():
    buttons = [
        [InlineKeyboardButton(text="🔹 ANDROID NONROOT", callback_data="dev_nonroot")],
        [InlineKeyboardButton(text="🔹 ANDROID ROOT", callback_data="dev_root")],
        [InlineKeyboardButton(text="🔹 IOS", callback_data="dev_ios")],
        [InlineKeyboardButton(text="🔙 Back", callback_data="back_to_main")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_products_menu(device_type):
    p_xtra = "🔴 Out of Stock • " if not stock_db["x_rag"] else ""
    buttons = [
        [InlineKeyboardButton(text="🤖 Phantom Mods NonRoot", callback_data="plan_phantom_x")],
        [InlineKeyboardButton(text="🤫 Silent X FF All", callback_data="plan_silent_x")],
        [InlineKeyboardButton(text=f"{p_xtra}⚡ X Reg NonRoot", callback_data="plan_x_rag")],
        [InlineKeyboardButton(text="👹 Troll Mods NonRoot", callback_data="plan_troll_mods")],
        [InlineKeyboardButton(text="🕸️ Drip Client Wire", callback_data="plan_drip_wire")],
        [InlineKeyboardButton(text="📱 Panthom Regular", callback_data="plan_panthom_reg")],
        [InlineKeyboardButton(text="🛠️ Bala Mods NonRoot", callback_data="plan_bala_mods")],
        [InlineKeyboardButton(text="🔙 Back", callback_data="shop_menu")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_plans_keyboard(prod_id):
    if prod_id == "bala_mods":
        plans = [("1h • ₹15.00", "15"), ("3h • ₹30.00", "30"), ("6h • ₹58.00", "58"), ("12h • ₹88.00", "88"), ("1 Day • ₹100.00", "100")]
    elif prod_id == "panthom_reg":
        plans = [("1h • ₹13.00", "13"), ("3h • ₹20.00", "20"), ("6h • ₹30.00", "30"), ("12h • ₹60.00", "60"), ("1 Day • ₹95.00", "95")]
    else:
        plans = [("6h • ₹20.00", "20"), ("12h • ₹60.00", "60"), ("1 Day • ₹100.00", "100"), ("3 Day • ₹149.00", "149"), ("7 Day • ₹200.00", "200")]

    buttons = []
    for text, amt in plans:
        buttons.append([InlineKeyboardButton(text=f"🟢 Buy {text}", callback_data=f"buy_confirm_{prod_id}_{amt}", style="success")])
    buttons.append([InlineKeyboardButton(text="🔙 Back", callback_data="shop_menu")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    init_user(user_id)
    if user_id == ADMIN_ID:
        await message.answer("👑 **प्रणाम मालिक!** आप बोट के मुख्य एडमिन हैं। आपके लिए सीक्रेट एडमिन पैनल एक्टिवेट कर दिया गया है।")
    welcome_text = (
        f"🔐 **ANGRY SHOP STORE** 🔐\n\n"
        f"💰 **Your Balance:** ₹{users_db[user_id]['balance']:.2f}\n\n"
        f"👇 Select an option from the menu below:"
    )
    await message.answer(welcome_text, reply_markup=get_main_menu(users_db[user_id]['balance']))

@dp.callback_query()
async def handle_callbacks(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    init_user(user_id)
    data = callback.data

    if data in ["back_to_main", "main_menu"]:
        await callback.message.edit_text("👇 Select an option from the menu below:", reply_markup=get_main_menu(users_db[user_id]['balance']))
    elif data == "shop_menu":
        await callback.message.edit_text("🛒 **PRODUCT STORE - SHOP**\n\nSelect your device type:", reply_markup=get_device_menu())
    elif data.startswith("dev_"):
        await callback.message.edit_text("🚀 **Choose a product:**", reply_markup=get_products_menu(data))
    elif data.startswith("plan_"):
        prod_id = data.replace("plan_", "")
        if not stock_db[prod_id]:
            await callback.answer("🔴 Out of Stock! यह पैनल अभी स्टॉक में नहीं है।", show_alert=True)
            return
        await callback.message.edit_text("⚡ **Choose a plan:**", reply_markup=get_plans_keyboard(prod_id))
    elif data.startswith("buy_confirm_"):
        parts = data.split("_")
        prod_id = parts[2]
        amount = float(parts[3])
        user_bal = users_db[user_id]["balance"]
        if user_bal < amount:
            deficit = amount - user_bal
            await callback.answer(f"❌ Insufficient Balance! You need ₹{deficit:.2f}.", show_alert=True)
            insufficient_text = (
                f"💰 **INSUFFICIENT BALANCE**\n\n"
                f"┣ Product: {prod_id.upper()}\n"
                f"┣ Price: ₹{amount:.2f}\n"
                f"┣ Your Balance: ₹{user_bal:.2f}\n"
                f"┗ Deficit Need: ₹{deficit:.2f}\n\n"
                f"Select payment method below:"
            )
            kb = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="PAY UPI", callback_data=f"deposit_qr_{amount}"),
                 InlineKeyboardButton(text="BINANCE", callback_data="binance_cooming")],
                [InlineKeyboardButton(text="Back to Plans", callback_data=f"plan_{prod_id}")]
            ])
            await callback.message.edit_text(insufficient_text, reply_markup=kb)
        else:
            key = stock_db[prod_id].pop(0)
            users_db[user_id]["balance"] -= amount
            users_db[user_id]["total_spent"] += amount
            users_db[user_id]["keys"].append(key)
            summary_text = (
                f"📦 **ORDER SUMMARY**\n\n"
                f"🔑 Product: {prod_id.upper()}\n"
                f"🔑 Key Delivered: `{key}`\n"
                f"💵 Final Total: ₹{amount:.2f}\n\n"
                f"✅ आपकी की सफलतापूर्वक डिलीवर हो चुकी है!"
            )
            await callback.message.edit_text(summary_text, reply_markup=get_main_menu(users_db[user_id]['balance']))
    elif data == "add_balance":
        add_funds_text = (
            f"💰 **ADD FUNDS TO WALLET**\n\n"
            f"Current balance: ₹{users_db[user_id]['balance']:.2f}\n\n"
            f"Pick a quick amount below, or enter a custom amount:\n"
            f"Min: ₹10.00 • Max: ₹50,000.00"
        )
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="₹100", callback_data="deposit_qr_100"),
             InlineKeyboardButton(text="₹500", callback_data="deposit_qr_500")],
            [InlineKeyboardButton(text="₹1000", callback_data="deposit_qr_1000"),
             InlineKeyboardButton(text="₹2000", callback_data="deposit_qr_2000")],
            [InlineKeyboardButton(text="Custom Amount", callback_data="enter_custom")],
            [InlineKeyboardButton(text="Back to Menu", callback_data="back_to_main")]
        ])
        await callback.message.edit_text(add_funds_text, reply_markup=kb)
    elif data == "enter_custom":
        await callback.message.edit_text("🔢 कृपया वह राशि टाइप करके भेजें जिसे आप वॉलेट में जोड़ना चाहते हैं (Min: ₹10):")
        await state.set_state(BotStates.custom_amount)
    elif data.startswith("deposit_qr_"):
        amt = data.split("_")[2]
        qr_link = f"upi://pay?pa={UPI_ID}&am={amt}&cu=INR&tn=StoreDeposit"
        qr_text = (
            f"📥 **UPI PAYMENT QR**\n\n"
            f"Scan & pay exactly ₹{amt} via UPI.\n\n"
            f"🔗 UPI Link: `{qr_link}`\n\n"
            f"⚡ Pay karne ke baad 'VERIFY PAYMENT' button dabayein.\n"
            f"⏳ This QR expires in 5 minutes."
        )
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="VERIFY PAYMENT", callback_data=f"verify_utr_prompt_{amt}")],
            [InlineKeyboardButton(text="Cancel Payment", callback_data=f"cancel_pay_{amt}")]
        ])
        await callback.message.edit_text(qr_text, reply_markup=kb)
    elif data.startswith("cancel_pay_"):
        amt = data.split("_")[2]
        await callback.message.edit_text(
            f"❌ **Payment Cancelled**\n\nYour QR for ₹{amt} was cancelled — no charge was made.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="Add Balance Again", callback_data="add_balance")],
                [InlineKeyboardButton(text="Back to Menu", callback_data="back_to_main")]
            ])
      )
      
