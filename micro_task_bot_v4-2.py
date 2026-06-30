import logging
import sqlite3
from datetime import datetime, timedelta
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    ConversationHandler,
    filters,
)

# ============================================================
# 1. CONFIGURATION
# ============================================================
BOT_TOKEN = "8821369295:AAGn7rEW6TawewF6dejeUm21Ybb9a1pIYsk"
ADMIN_ID = 8456410826
BOT_USERNAME = "MicroEarnTaskBot"
CHANNEL_USERNAME = "@MicroEarnTask"
ADMIN_USERNAME = "@AliAhmed1780"
MIN_WITHDRAW = 0.20
REFERRAL_BONUS = 0.01

# ============================================================
# 2. TRANSLATIONS
# ============================================================
TEXTS = {
    "en": {
        "welcome": "Welcome to the Micro-Task Earn Bot! 🚀 👋\n\nHello *{name}*! Earn real money by completing simple online tasks!\n\n*Select one of the Menu Options below 👇*",
        "subscribe_first": "👋 Welcome *{name}*!\n\n📢 To use this bot, you must subscribe to our channel first!\n\n👇 Click the button below to subscribe:",
        "subscribe_btn": "📢 Subscribe to Channel",
        "check_sub_btn": "✅ Check Subscription",
        "sub_verified": "✅ *Subscription Verified!*\n\nWelcome *{name}*! You can now use the bot.",
        "not_subscribed": "❌ *You are not subscribed yet!*\n\nPlease subscribe first, then click Check Subscription.",
        "earn_money": "💰 Earn Money",
        "my_wallet": "👤 My Wallet",
        "withdraw": "💸 Withdraw",
        "referral_link": "🔗 Referral Link",
        "support_help": "ℹ️ Support & Help",
        "settings": "⚙️ Settings",
        "back_menu": "🔙 Back to Main Menu",
        "new_task": "📢 *New Task Available!*\n━━━━━━━━━━━━━━━━━━━━━━━━\n🔹 *Platform:* {platform}\n🔹 *Action:* {action}\n💰 *Reward:* `${reward}`\n━━━━━━━━━━━━━━━━━━━━━━━━\n_Complete the action, take a screenshot as proof, and send it here._\n\n[👉 OPEN TASK LINK 👈]({link})",
        "no_tasks": "⏳ *No New Tasks Available*\n\nCheck back later for new ones!",
        "send_screenshot": "📸 Send Screenshot",
        "skip_task": "⏭️ Skip Task",
        "main_menu": "🔙 Main Menu",
        "send_screenshot_prompt": "📸 *Please send your screenshot photo now!*\n\n_Take a screenshot proving you completed the task and send it here._",
        "proof_submitted": "🎉 *Screenshot Submitted!*\n\nYour proof has been sent to admin for review. You will receive your reward once approved! ✅",
        "send_as_photo": "⚠️ Please send your proof as a *Photo* 📸",
        "wallet_title": "👤 *Your Wallet Dashboard*",
        "user_id": "🆔 *User ID:*",
        "balance": "💰 *Available Balance:*",
        "total_earned": "📈 *Total Earned:*",
        "total_referrals": "👥 *Total Referrals:*",
        "referral_earnings": "🎁 *Referral Earnings:*",
        "total_withdrawn": "💸 *Total Withdrawn:*",
        "member_since": "📅 *Member Since:*",
        "referral_title": "🔗 *Invite Friends & Earn Money!*",
        "referral_text": "Invite your friends and earn *$0.01* for every person who joins!\n\n👥 *Your Total Referrals:* `{count} Users`\n💰 *Total Referral Earnings:* `${earnings}`\n\n👇 *Your Unique Referral Link:*\n`{link}`\n━━━━━━━━━━━━━━━━━━━━━━━━\n_Share this link on Telegram Groups to boost your earnings!_",
        "task_approved": "✅ *Task Approved!*\n\n`${reward}` added to your wallet! Keep earning! 💪",
        "task_rejected": "❌ *Task Rejected!*\n\nPlease complete the task properly and try again.",
        "withdraw_menu": "💸 *Withdraw Menu*\n\n💰 *Your Balance:* `${balance}`\n\nSelect an option:",
        "payout_request": "💳 Payout Request",
        "withdrawal_history": "📜 Withdrawal History",
        "no_history": "📜 *No withdrawal history yet.*",
        "insufficient": "❌ *Insufficient Balance!*\n\nYour balance: `${balance}`\nMinimum: `${min}`\n\nKeep earning! 💪",
        "select_method": "💸 *Select Payment Method*\n\n💰 Balance: `${balance}`",
        "evc": "📱 EVC Plus",
        "premier": "💳 Premier Wallet",
        "usdt": "🪙 USDT (TRC-20)",
        "enter_amount": "💰 *Enter Amount*\n\nBalance: `${balance}`\nMinimum: `${min}`\n\nType the amount:",
        "enter_account": "📱 *Enter your phone number or wallet address:*",
        "confirm_withdraw": "⚠️ *Confirm Withdrawal*\n━━━━━━━━━━━━━━━━━━━━━━━━\n🔹 *Method:* {method}\n🔹 *Amount:* `${amount}`\n🔹 *Account:* `{account}`",
        "confirm_btn": "✅ Confirm Withdrawal",
        "cancel_btn": "❌ Cancel",
        "withdraw_submitted": "🎉 *Withdrawal Submitted!*\n\nAmount: `${amount}` via {method}\nRequest ID: `#{id}`\nStatus: ⏳ *Pending Review*\n\nProcessed within 24 hours. Check *📜 Withdrawal History* anytime to see if it's been approved! ✅",
        "withdraw_cancelled": "Withdrawal cancelled.",
        "payment_sent": "✅ *Payment Sent!*\n\nYour `${amount}` has been sent! 🎉",
        "declined": "❌ *Withdrawal Declined!*\n\n`${amount}` refunded. Contact admin.",
        "support_text": "ℹ️ *HELP CENTER*\n━━━━━━━━━━━━━━━━━━━━━━━━\n\n📜 *Rules*\n\n🚫 Multi-accounts are strictly banned\n🚫 Fake or recycled screenshots = permanent ban\n✅ You must be subscribed to our channel\n\n💰 *Earnings & Payouts*\n\n💵 Minimum withdrawal: *$0.20*\n⏱️ Withdrawals processed within *24 hours*\n🎁 Referral bonus: *$0.01* per friend invited\n\n━━━━━━━━━━━━━━━━━━━━━━━━\n\n❓ *FAQ*\n\n▫️ How much can I earn?\n   → Unlimited!\n\n▫️ When do I get paid?\n   → Within 24 hours of request\n\n▫️ Is this free to join?\n   → Yes, 100% free!\n\n▫️ Minimum withdrawal?\n   → $0.20\n\n━━━━━━━━━━━━━━━━━━━━━━━━\n\n📞 *Contact*\n👨‍💻 Support: {admin}\n📢 Channel: {channel}",
        "contact_admin": "👨‍💻 *Contact Admin*\n\nFor support: {admin}",
        "contact_btn": "👨‍💻 Contact Admin",
        "referral_bonus_msg": "🎉 Someone joined using your referral link! You earned *$0.01* bonus!",
        "banned": "❌ Your account has been banned.",
        "must_subscribe": "❌ *You must subscribe to our channel first!*",
        "action_cancelled": "Action cancelled.",
        "invalid_amount": "❌ Invalid amount. Enter a number (e.g. `0.50`):",
        "min_amount": "❌ Minimum is ${min}. Enter again:",
        "not_enough": "❌ Not enough balance (${balance}). Enter again:",
        "language_select": "🌍 *Select Your Language*\n\nChoose your preferred language:",
        "lang_changed": "✅ Language changed to English!",
    },
    "so": {
        "welcome": "Ku soo dhawow Micro-Task Earn Bot! 🚀 👋\n\nSalaan *{name}*! Lacag run ah kasab adoo dhameystiraya hawlaha fudud!\n\n*Dooro mid ka mid ah menuuga hoose 👇*",
        "subscribe_first": "👋 Ku soo dhawow *{name}*!\n\n📢 Si aad u isticmaashid bot-kan, waa inaad channel-ka la biirtaa marka hore!\n\n👇 Riix badhanka hoose:",
        "subscribe_btn": "📢 La biir Channel-ka",
        "check_sub_btn": "✅ Xaqiiji Rukunka",
        "sub_verified": "✅ *Rukunka Waa La Xaqiijiyay!*\n\nKu soo dhawow *{name}*! Hadda waxaad isticmaali kartaa bot-ka.",
        "not_subscribed": "❌ *Weli kuma biirsan channel-ka!*\n\nFarxad la biir channel-ka, kadib riix Xaqiiji Rukunka.",
        "earn_money": "💰 Kasab Lacag",
        "my_wallet": "👤 Boorsadayda",
        "withdraw": "💸 Lacag Bixi",
        "referral_link": "🔗 Link Martida",
        "support_help": "ℹ️ Caawimaad",
        "settings": "⚙️ Dejinta",
        "back_menu": "🔙 Menu Hore",
        "new_task": "📢 *Hawl Cusub!*\n━━━━━━━━━━━━━━━━━━━━━━━━\n🔹 *Platform:* {platform}\n🔹 *Shaqo:* {action}\n💰 *Abaal:* `${reward}`\n━━━━━━━━━━━━━━━━━━━━━━━━\n_Dhameyso hawsha, screenshot qaad, halkan u dir._\n\n[👉 FUR LINK-KA 👈]({link})",
        "no_tasks": "⏳ *Hawl Cusub Majirto*\n\nMarar dambe soo eeg!",
        "send_screenshot": "📸 Dir Screenshot",
        "skip_task": "⏭️ Ka Bax Hawsha",
        "main_menu": "🔙 Menu Hore",
        "send_screenshot_prompt": "📸 *Hada sawirkaaga soo dir!*\n\n_Screenshot qaad oo halkan u dir._",
        "proof_submitted": "🎉 *Screenshot Waa La Diray!*\n\nCaddayntaada admin-ka ayaa eegaya. Abaalmarinta waxaad helaysaa marka la oggolaado! ✅",
        "send_as_photo": "⚠️ Sawirkaaga *Sawir* ahaan u dir 📸",
        "wallet_title": "👤 *Boorsadaada*",
        "user_id": "🆔 *ID-gaaga:*",
        "balance": "💰 *Lacagta Joogta:*",
        "total_earned": "📈 *Wadarta La Kasabtay:*",
        "total_referrals": "👥 *Wadarta Martida:*",
        "referral_earnings": "🎁 *Faa'iidada Martida:*",
        "total_withdrawn": "💸 *Wadarta La Bixiyay:*",
        "member_since": "📅 *Taariikhda La Yimid:*",
        "referral_title": "🔗 *Asxaab Martiyee Lacag Hel!*",
        "referral_text": "Asxaabtaada martiyee *$0.01* hel qof kasta oo yimaada!\n\n👥 *Wadarta Martida:* `{count} Qof`\n💰 *Faa'iidada Martida:* `${earnings}`\n\n👇 *Link-kaaga Gaar ah:*\n`{link}`\n━━━━━━━━━━━━━━━━━━━━━━━━\n_La wadaag kooxaha Telegram!_",
        "task_approved": "✅ *Hawsha Waa La Aqbalay!*\n\n`${reward}` boorsadaada ayaa lagu daray! Sii wad! 💪",
        "task_rejected": "❌ *Hawsha Waa La Diiday!*\n\nHawsha si sax ah u dhameyso oo mar kale isku day.",
        "withdraw_menu": "💸 *Lacag Bixinta*\n\n💰 *Lacagta:* `${balance}`\n\nDooro ikhtiyaar:",
        "payout_request": "💳 Codsi Lacag",
        "withdrawal_history": "📜 Taariikhda Bixinta",
        "no_history": "📜 *Wali lacag lama bixin.*",
        "insufficient": "❌ *Lacag Kuma Filna!*\n\nLacagtaada: `${balance}`\nUgu yaraan: `${min}`\n\nSii wad hawlaha! 💪",
        "select_method": "💸 *Dooro Qaabka Lacag Qaadashada*\n\n💰 Lacagta: `${balance}`",
        "evc": "📱 EVC Plus",
        "premier": "💳 Premier Wallet",
        "usdt": "🪙 USDT (TRC-20)",
        "enter_amount": "💰 *Geli Lacagta*\n\nLacagta: `${balance}`\nUgu yaraan: `${min}`\n\nQor lacagta:",
        "enter_account": "📱 *Geli lambarka telefoonkaaga ama cinwaanka boorsadaada:*",
        "confirm_withdraw": "⚠️ *Xaqiiji Lacag Bixinta*\n━━━━━━━━━━━━━━━━━━━━━━━━\n🔹 *Qaab:* {method}\n🔹 *Lacag:* `${amount}`\n🔹 *Akoon:* `{account}`",
        "confirm_btn": "✅ Xaqiiji Bixinta",
        "cancel_btn": "❌ Jooji",
        "withdraw_submitted": "🎉 *Codsiga Waa La Diray!*\n\nLacag: `${amount}` via {method}\nID: `#{id}`\nXaalad: ⏳ *Sugaya Xaqiijin*\n\n24 saacadood gudahood waa la xidhi doonaa. Marwalba *📜 Taariikhda Lacag Bixinta* eeg si aad u aragto haddii la oggolaaday! ✅",
        "withdraw_cancelled": "Lacag bixinta waa la joojiyay.",
        "payment_sent": "✅ *Lacagta Waa La Diray!*\n\n`${amount}` waa la kuu diray! 🎉",
        "declined": "❌ *Codsiga Waa La Diiday!*\n\n`${amount}` boorsadaada ayaa lagu soo celiyay.",
        "support_text": "ℹ️ *XARUNTA CAAWIMAADA*\n━━━━━━━━━━━━━━━━━━━━━━━━\n\n📜 *Xeerarka*\n\n🚫 Akoon badan isticmaalida waa la joojiyaa\n🚫 Screenshot been ah = joojin joogto ah\n✅ Waa inaad channel-ka la biirtaa\n\n💰 *Lacagta & Bixinta*\n\n💵 Ugu yar lacag bixinta: *$0.20*\n⏱️ Lacagta waxaa la xidha *24 saacadood* gudahood\n🎁 Bonus martida: *$0.01* qof kasta\n\n━━━━━━━━━━━━━━━━━━━━━━━━\n\n❓ *Su'aalaha Badanaa La Weydiiyo*\n\n▫️ Imisa ayaan kasbi karaa?\n   → Xad la'aan!\n\n▫️ Goorma la i bixiyaa?\n   → 24 saacadood gudahood\n\n▫️ Bilaashma?\n   → Haa, 100% bilaash!\n\n▫️ Ugu yar lacag bixinta?\n   → $0.20\n\n━━━━━━━━━━━━━━━━━━━━━━━━\n\n📞 *La Xiriir*\n👨‍💻 Caawimaad: {admin}\n📢 Channel: {channel}",
        "contact_admin": "👨‍💻 *La Xiriir Admin-ka*\n\nCaawimaad: {admin}",
        "contact_btn": "👨‍💻 La Xiriir Admin-ka",
        "referral_bonus_msg": "🎉 Qof ayaa link-kaaga adeegsaday! Waad heshay *$0.01* bonus!",
        "banned": "❌ Akoonkaaga waa la xayiray.",
        "must_subscribe": "❌ *Waa inaad channel-ka la biirtaa marka hore!*",
        "action_cancelled": "Hawsha waa la joojiyay.",
        "invalid_amount": "❌ Lacag khalad ah. Qor tiro (tusaale `0.50`):",
        "min_amount": "❌ Ugu yaraan waa ${min}. Mar kale qor:",
        "not_enough": "❌ Lacag kuma filna (${balance}). Mar kale qor:",
        "language_select": "🌍 *Dooro Luuqadda*\n\nDooro luuqadda aad doorbideyso:",
        "lang_changed": "✅ Luuqadda waxaa loo beddelay Soomaali!",
    }
}

def t(user_id, key, **kwargs):
    lang = get_user_lang(user_id)
    text = TEXTS.get(lang, TEXTS["en"]).get(key, TEXTS["en"].get(key, key))
    if kwargs:
        try:
            text = text.format(**kwargs)
        except:
            pass
    return text

# ============================================================
# 3. LOGGING
# ============================================================
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# ============================================================
# 4. CONVERSATION STATES
# ============================================================
WITHDRAW_METHOD, WITHDRAW_AMOUNT, WITHDRAW_DETAILS, WITHDRAW_CONFIRM = range(4)
UPLOAD_SCREENSHOT = 4

# ============================================================
# 5. DATABASE
# ============================================================
def init_db():
    conn = sqlite3.connect("bot_database.db")
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        full_name TEXT,
        balance REAL DEFAULT 0.0,
        total_earned REAL DEFAULT 0.0,
        total_withdrawn REAL DEFAULT 0.0,
        referral_count INTEGER DEFAULT 0,
        referral_earnings REAL DEFAULT 0.0,
        referred_by INTEGER DEFAULT NULL,
        joined_date TEXT,
        is_banned INTEGER DEFAULT 0,
        language TEXT DEFAULT 'en'
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        platform TEXT,
        action TEXT,
        link TEXT,
        reward REAL,
        is_active INTEGER DEFAULT 1
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS task_submissions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        task_id INTEGER,
        file_id TEXT,
        status TEXT DEFAULT 'pending',
        submitted_at TEXT,
        reviewed_at TEXT
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS withdrawals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        method TEXT,
        amount REAL,
        account TEXT,
        status TEXT DEFAULT 'pending',
        requested_at TEXT,
        processed_at TEXT
    )''')

    try:
        c.execute("ALTER TABLE users ADD COLUMN language TEXT DEFAULT 'en'")
    except:
        pass

    c.execute("SELECT COUNT(*) FROM tasks")
    if c.fetchone()[0] == 0:
        sample_tasks = [
            ("TikTok", "Follow Account", "https://tiktok.com/@mohamed098011", 0.015),
            ("TikTok", "Like Video", "https://tiktok.com/@mohamed098011", 0.010),
            ("Telegram", "Join Channel", "https://t.me/MicroEarnTask", 0.010),
            ("YouTube", "Subscribe to Channel", "https://youtube.com/@example", 0.020),
            ("YouTube", "Like Video", "https://youtube.com/@example", 0.015),
        ]
        c.executemany("INSERT INTO tasks (platform, action, link, reward) VALUES (?, ?, ?, ?)", sample_tasks)

    conn.commit()
    conn.close()

def get_user(user_id):
    conn = sqlite3.connect("bot_database.db")
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    user = c.fetchone()
    conn.close()
    return user

def get_user_lang(user_id):
    conn = sqlite3.connect("bot_database.db")
    c = conn.cursor()
    c.execute("SELECT language FROM users WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    conn.close()
    return row[0] if row and row[0] else "en"

def set_user_lang(user_id, lang):
    conn = sqlite3.connect("bot_database.db")
    c = conn.cursor()
    c.execute("UPDATE users SET language=? WHERE user_id=?", (lang, user_id))
    conn.commit()
    conn.close()

def create_user(user_id, username, full_name, referred_by=None):
    conn = sqlite3.connect("bot_database.db")
    c = conn.cursor()
    c.execute(
        "INSERT OR IGNORE INTO users (user_id, username, full_name, referred_by, joined_date, language) VALUES (?, ?, ?, ?, ?, 'en')",
        (user_id, username, full_name, referred_by, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    )
    conn.commit()
    conn.close()

def get_next_task(user_id):
    conn = sqlite3.connect("bot_database.db")
    c = conn.cursor()
    c.execute('''SELECT t.* FROM tasks t
                 WHERE t.is_active = 1
                 AND t.id NOT IN (
                     SELECT task_id FROM task_submissions
                     WHERE user_id = ? AND status IN ('pending', 'approved')
                 )
                 ORDER BY RANDOM() LIMIT 1''', (user_id,))
    task = c.fetchone()
    conn.close()
    return task

# ============================================================
# 6. CHECK CHANNEL SUBSCRIPTION
# ============================================================
async def is_subscribed(user_id, context):
    try:
        member = await context.bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

# ============================================================
# 7. MAIN MENU
# ============================================================
def get_main_menu(user_id):
    lang = get_user_lang(user_id)
    keyboard = [
        [TEXTS[lang]["earn_money"], TEXTS[lang]["my_wallet"]],
        [TEXTS[lang]["withdraw"], TEXTS[lang]["referral_link"]],
        [TEXTS[lang]["support_help"], TEXTS[lang]["settings"]]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# ============================================================
# 8. /start COMMAND
# ============================================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    args = context.args
    referred_by = None

    if args and args[0].startswith("ref_"):
        try:
            referred_by = int(args[0].split("_")[1])
            if referred_by == user.id:
                referred_by = None
        except:
            referred_by = None

    existing = get_user(user.id)
    if not existing:
        create_user(user.id, user.username or "", user.full_name, referred_by)
        if referred_by:
            conn = sqlite3.connect("bot_database.db")
            c = conn.cursor()
            c.execute("UPDATE users SET referral_count=referral_count+1, referral_earnings=referral_earnings+0.01, balance=balance+0.01 WHERE user_id=?", (referred_by,))
            conn.commit()
            conn.close()
            try:
                await context.bot.send_message(referred_by, t(referred_by, "referral_bonus_msg"), parse_mode="Markdown")
            except:
                pass

        # Show language selection for new users
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")],
            [InlineKeyboardButton("🇸🇴 Somali", callback_data="lang_so")]
        ])
        await update.message.reply_text(
            "🌍 *Select Your Language / Dooro Luuqadda*",
            parse_mode="Markdown",
            reply_markup=keyboard
        )
        return

    subscribed = await is_subscribed(user.id, context)
    if not subscribed:
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(t(user.id, "subscribe_btn"), url=f"https://t.me/MicroEarnTask")],
            [InlineKeyboardButton(t(user.id, "check_sub_btn"), callback_data="check_subscription")]
        ])
        await update.message.reply_text(
            t(user.id, "subscribe_first", name=user.first_name),
            parse_mode="Markdown",
            reply_markup=keyboard
        )
        return

    await update.message.reply_text(
        t(user.id, "welcome", name=user.first_name),
        parse_mode="Markdown",
        reply_markup=get_main_menu(user.id)
    )

# ============================================================
# 9. LANGUAGE CALLBACK
# ============================================================
async def language_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = query.from_user
    lang = query.data.split("_")[1]
    set_user_lang(user.id, lang)

    await query.edit_message_text(
        t(user.id, "lang_changed"),
        parse_mode="Markdown"
    )

    subscribed = await is_subscribed(user.id, context)
    if not subscribed:
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(t(user.id, "subscribe_btn"), url=f"https://t.me/MicroEarnTask")],
            [InlineKeyboardButton(t(user.id, "check_sub_btn"), callback_data="check_subscription")]
        ])
        await context.bot.send_message(
            user.id,
            t(user.id, "subscribe_first", name=user.first_name),
            parse_mode="Markdown",
            reply_markup=keyboard
        )
    else:
        await context.bot.send_message(
            user.id,
            t(user.id, "welcome", name=user.first_name),
            parse_mode="Markdown",
            reply_markup=get_main_menu(user.id)
        )

# ============================================================
# 10. CHECK SUBSCRIPTION CALLBACK
# ============================================================
async def check_subscription(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = query.from_user

    subscribed = await is_subscribed(user.id, context)
    if subscribed:
        await query.edit_message_text(
            t(user.id, "sub_verified", name=user.first_name),
            parse_mode="Markdown"
        )
        await context.bot.send_message(
            user.id,
            t(user.id, "welcome", name=user.first_name),
            parse_mode="Markdown",
            reply_markup=get_main_menu(user.id)
        )
    else:
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(t(user.id, "subscribe_btn"), url=f"https://t.me/MicroEarnTask")],
            [InlineKeyboardButton(t(user.id, "check_sub_btn"), callback_data="check_subscription")]
        ])
        await query.edit_message_text(
            t(user.id, "not_subscribed"),
            parse_mode="Markdown",
            reply_markup=keyboard
        )

# ============================================================
# 11. MY WALLET
# ============================================================
async def my_wallet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = get_user(user_id)
    if not user:
        await start(update, context)
        return

    wallet_text = (
        f"{t(user_id, 'wallet_title')}\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{t(user_id, 'user_id')} `{user[0]}`\n"
        f"{t(user_id, 'balance')} `${user[3]:.2f}`\n"
        f"{t(user_id, 'total_earned')} `${user[4]:.2f}`\n"
        f"{t(user_id, 'total_referrals')} `{user[6]} Users`\n"
        f"{t(user_id, 'referral_earnings')} `${user[7]:.2f}`\n"
        f"{t(user_id, 'total_withdrawn')} `${user[5]:.2f}`\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{t(user_id, 'member_since')} `{user[9][:10]}`"
    )
    keyboard = [[t(user_id, "back_menu")]]
    markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(wallet_text, parse_mode="Markdown", reply_markup=markup)

# ============================================================
# 12. REFERRAL LINK
# ============================================================
async def referral_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = get_user(user_id)
    if not user:
        await start(update, context)
        return

    ref_link = f"https://t.me/{BOT_USERNAME}?start=ref_{user_id}"
    ref_text = (
        f"{t(user_id, 'referral_title')}\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n"
        + t(user_id, "referral_text", count=user[6], earnings=f"{user[7]:.2f}", link=ref_link)
    )
    keyboard = [[t(user_id, "back_menu")]]
    markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(ref_text, parse_mode="Markdown", reply_markup=markup)

# ============================================================
# 13. SUPPORT & HELP
# ============================================================
async def support_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    support_text = t(user_id, "support_text", admin=ADMIN_USERNAME, channel=CHANNEL_USERNAME)
    keyboard = [[t(user_id, "contact_btn")], [t(user_id, "back_menu")]]
    markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(support_text, parse_mode="Markdown", reply_markup=markup)

async def contact_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    await update.message.reply_text(
        t(user_id, "contact_admin", admin=ADMIN_USERNAME),
        parse_mode="Markdown",
        reply_markup=get_main_menu(user_id)
    )

# ============================================================
# 14. EARN MONEY
# ============================================================
async def earn_money_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = get_user(user_id)
    if not user:
        await start(update, context)
        return

    if user[10] == 1:
        await update.message.reply_text(t(user_id, "banned"))
        return

    subscribed = await is_subscribed(user_id, context)
    if not subscribed:
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(t(user_id, "subscribe_btn"), url=f"https://t.me/MicroEarnTask")],
            [InlineKeyboardButton(t(user_id, "check_sub_btn"), callback_data="check_subscription")]
        ])
        await update.message.reply_text(
            t(user_id, "must_subscribe"),
            parse_mode="Markdown",
            reply_markup=keyboard
        )
        return ConversationHandler.END

    task = get_next_task(user_id)
    if not task:
        await update.message.reply_text(
            t(user_id, "no_tasks"),
            parse_mode="Markdown",
            reply_markup=get_main_menu(user_id)
        )
        return ConversationHandler.END

    context.user_data['current_task'] = task

    task_text = t(user_id, "new_task",
                  platform=task[1], action=task[2],
                  reward=f"{task[4]:.3f}", link=task[3])

    lang = get_user_lang(user_id)
    keyboard = [
        [TEXTS[lang]["send_screenshot"]],
        [TEXTS[lang]["skip_task"]],
        [TEXTS[lang]["main_menu"]]
    ]
    markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(task_text, parse_mode="Markdown", reply_markup=markup)
    return UPLOAD_SCREENSHOT

async def send_screenshot_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    await update.message.reply_text(
        t(user_id, "send_screenshot_prompt"),
        parse_mode="Markdown"
    )
    return UPLOAD_SCREENSHOT

async def process_screenshot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    task = context.user_data.get('current_task')

    if update.message.photo:
        file_id = update.message.photo[-1].file_id

        conn = sqlite3.connect("bot_database.db")
        c = conn.cursor()
        c.execute(
            "INSERT INTO task_submissions (user_id, task_id, file_id, status, submitted_at) VALUES (?, ?, ?, 'pending', ?)",
            (user_id, task[0], file_id, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        )
        submission_id = c.lastrowid
        conn.commit()
        conn.close()

        admin_text = (
            f"📸 *New Task Submission!*\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"👤 *User:* {update.effective_user.full_name} (`{user_id}`)\n"
            f"📋 *Task:* {task[1]} - {task[2]}\n"
            f"💰 *Reward:* ${task[4]:.3f}\n"
            f"🆔 *Submission ID:* #{submission_id}"
        )
        admin_keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("✅ Approve", callback_data=f"approve_{submission_id}_{user_id}_{task[4]}"),
                InlineKeyboardButton("❌ Reject", callback_data=f"reject_{submission_id}_{user_id}")
            ]
        ])
        try:
            await context.bot.send_photo(
                ADMIN_ID, photo=file_id,
                caption=admin_text, parse_mode="Markdown",
                reply_markup=admin_keyboard
            )
        except Exception as e:
            logger.error(f"Failed to notify admin: {e}")

        await update.message.reply_text(
            t(user_id, "proof_submitted"),
            parse_mode="Markdown",
            reply_markup=get_main_menu(user_id)
        )
        return ConversationHandler.END
    else:
        await update.message.reply_text(
            t(user_id, "send_as_photo"),
            parse_mode="Markdown"
        )
        return UPLOAD_SCREENSHOT

# ============================================================
# 15. ADMIN CALLBACKS
# ============================================================
async def admin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.from_user.id != ADMIN_ID:
        await query.answer("❌ Not authorized!", show_alert=True)
        return

    data = query.data.split("_")
    action = data[0]
    submission_id = int(data[1])
    user_id = int(data[2])

    conn = sqlite3.connect("bot_database.db")
    c = conn.cursor()

    if action == "approve":
        reward = float(data[3])
        c.execute("UPDATE task_submissions SET status='approved', reviewed_at=? WHERE id=?",
                  (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), submission_id))
        c.execute("UPDATE users SET balance=balance+?, total_earned=total_earned+? WHERE user_id=?",
                  (reward, reward, user_id))

        c.execute("SELECT referred_by FROM users WHERE user_id=?", (user_id,))
        ref_row = c.fetchone()
        if ref_row and ref_row[0]:
            ref_commission = round(reward * 0.10, 4)
            c.execute("UPDATE users SET balance=balance+?, referral_earnings=referral_earnings+? WHERE user_id=?",
                      (ref_commission, ref_commission, ref_row[0]))
            try:
                await context.bot.send_message(ref_row[0], f"💰 Referral Commission! You earned `${ref_commission:.4f}`!", parse_mode="Markdown")
            except:
                pass

        conn.commit()
        conn.close()
        await query.edit_message_caption(caption=query.message.caption + "\n\n✅ *APPROVED*", parse_mode="Markdown")
        try:
            await context.bot.send_message(user_id, t(user_id, "task_approved", reward=f"{reward:.3f}"), parse_mode="Markdown")
        except:
            pass

    elif action == "reject":
        c.execute("UPDATE task_submissions SET status='rejected', reviewed_at=? WHERE id=?",
                  (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), submission_id))
        conn.commit()
        conn.close()
        await query.edit_message_caption(caption=query.message.caption + "\n\n❌ *REJECTED*", parse_mode="Markdown")
        try:
            await context.bot.send_message(user_id, t(user_id, "task_rejected"), parse_mode="Markdown")
        except:
            pass

# ============================================================
# 16. WITHDRAW SYSTEM
# ============================================================
async def withdraw_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = get_user(user_id)
    lang = get_user_lang(user_id)
    keyboard = [
        [TEXTS[lang]["payout_request"]],
        [TEXTS[lang]["withdrawal_history"]],
        [TEXTS[lang]["back_menu"]]
    ]
    markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        t(user_id, "withdraw_menu", balance=f"{user[3]:.2f}"),
        parse_mode="Markdown", reply_markup=markup
    )
    return WITHDRAW_METHOD

async def withdrawal_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    lang = get_user_lang(user_id)
    conn = sqlite3.connect("bot_database.db")
    c = conn.cursor()
    c.execute("SELECT method, amount, status, requested_at FROM withdrawals WHERE user_id=? ORDER BY id DESC LIMIT 10", (user_id,))
    rows = c.fetchall()
    conn.close()

    if not rows:
        await update.message.reply_text(t(user_id, "no_history"), parse_mode="Markdown", reply_markup=get_main_menu(user_id))
        return ConversationHandler.END

    status_labels_en = {"paid": "✅ APPROVED & PAID", "pending": "⏳ PENDING REVIEW", "declined": "❌ DECLINED"}
    status_labels_so = {"paid": "✅ LA OGGOLAADAY & LA BIXIYAY", "pending": "⏳ SUGAYA XAQIIJIN", "declined": "❌ LA DIIDAY"}
    status_labels = status_labels_so if lang == "so" else status_labels_en

    title = "📜 *Taariikhda Lacag Bixinta*" if lang == "so" else "📜 *Withdrawal History*"
    text = f"{title}\n━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    for row in rows:
        status_text = status_labels.get(row[2], row[2].upper())
        text += f"💵 *${row[1]:.2f}* — {row[0]}\n{status_text}\n📅 {row[3][:10]}\n━━━━━━━━━━━━━━━━━━━━━━━━\n"

    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=get_main_menu(user_id))
    return ConversationHandler.END

async def payout_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = get_user(user_id)
    lang = get_user_lang(user_id)

    if not user or user[3] < MIN_WITHDRAW:
        await update.message.reply_text(
            t(user_id, "insufficient", balance=f"{user[3]:.2f}", min=f"{MIN_WITHDRAW:.2f}"),
            parse_mode="Markdown", reply_markup=get_main_menu(user_id)
        )
        return ConversationHandler.END

    keyboard = [
        [TEXTS[lang]["evc"], TEXTS[lang]["premier"]],
        [TEXTS[lang]["usdt"]],
        [TEXTS[lang]["back_menu"]]
    ]
    markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        t(user_id, "select_method", balance=f"{user[3]:.2f}"),
        parse_mode="Markdown", reply_markup=markup
    )
    return WITHDRAW_AMOUNT

async def withdraw_method_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    context.user_data['method'] = update.message.text
    user = get_user(user_id)
    await update.message.reply_text(
        t(user_id, "enter_amount", balance=f"{user[3]:.2f}", min=f"{MIN_WITHDRAW:.2f}"),
        parse_mode="Markdown", reply_markup=ReplyKeyboardRemove()
    )
    return WITHDRAW_DETAILS

async def withdraw_amount_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    try:
        amount = float(update.message.text)
        user = get_user(user_id)
        if amount < MIN_WITHDRAW:
            await update.message.reply_text(t(user_id, "min_amount", min=f"{MIN_WITHDRAW:.2f}"))
            return WITHDRAW_DETAILS
        if amount > user[3]:
            await update.message.reply_text(t(user_id, "not_enough", balance=f"{user[3]:.2f}"))
            return WITHDRAW_DETAILS
        context.user_data['amount'] = amount
        await update.message.reply_text(t(user_id, "enter_account"), parse_mode="Markdown")
        return WITHDRAW_CONFIRM
    except ValueError:
        await update.message.reply_text(t(user_id, "invalid_amount"), parse_mode="Markdown")
        return WITHDRAW_DETAILS

async def withdraw_details_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    context.user_data['account'] = update.message.text
    lang = get_user_lang(user_id)
    confirm_text = t(user_id, "confirm_withdraw",
                     method=context.user_data['method'],
                     amount=f"{context.user_data['amount']:.2f}",
                     account=context.user_data['account'])
    keyboard = [[TEXTS[lang]["confirm_btn"]], [TEXTS[lang]["cancel_btn"]]]
    markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(confirm_text, parse_mode="Markdown", reply_markup=markup)
    return WITHDRAW_METHOD

async def withdraw_final(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    lang = get_user_lang(user_id)
    confirm_texts = [TEXTS["en"]["confirm_btn"], TEXTS["so"]["confirm_btn"]]

    if update.message.text in confirm_texts:
        amount = context.user_data['amount']
        method = context.user_data['method']
        account = context.user_data['account']

        conn = sqlite3.connect("bot_database.db")
        c = conn.cursor()
        c.execute("UPDATE users SET balance=balance-?, total_withdrawn=total_withdrawn+? WHERE user_id=?",
                  (amount, amount, user_id))
        c.execute(
            "INSERT INTO withdrawals (user_id, method, amount, account, status, requested_at) VALUES (?, ?, ?, ?, 'pending', ?)",
            (user_id, method, amount, account, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        )
        withdrawal_id = c.lastrowid
        conn.commit()
        conn.close()

        user = update.effective_user
        admin_text = (
            f"💸 *New Withdrawal Request!*\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"👤 *User:* {user.full_name} (`{user_id}`)\n"
            f"💰 *Amount:* `${amount:.2f}`\n"
            f"📱 *Method:* {method}\n"
            f"🏦 *Account:* `{account}`\n"
            f"🆔 *Request ID:* #{withdrawal_id}"
        )
        admin_keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("✅ Mark Paid", callback_data=f"paid_{withdrawal_id}_{user_id}_{amount}"),
                InlineKeyboardButton("❌ Decline", callback_data=f"decline_{withdrawal_id}_{user_id}_{amount}")
            ]
        ])
        try:
            await context.bot.send_message(ADMIN_ID, admin_text, parse_mode="Markdown", reply_markup=admin_keyboard)
        except Exception as e:
            logger.error(f"Failed to notify admin: {e}")

        await update.message.reply_text(
            t(user_id, "withdraw_submitted", amount=f"{amount:.2f}", method=method, id=withdrawal_id),
            parse_mode="Markdown", reply_markup=get_main_menu(user_id)
        )
    else:
        await update.message.reply_text(t(user_id, "withdraw_cancelled"), reply_markup=get_main_menu(user_id))
    return ConversationHandler.END

# ============================================================
# 17. ADMIN WITHDRAWAL CALLBACK
# ============================================================
async def admin_withdrawal_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.from_user.id != ADMIN_ID:
        return

    data = query.data.split("_")
    action = data[0]
    withdrawal_id = int(data[1])
    user_id = int(data[2])
    amount = float(data[3])

    conn = sqlite3.connect("bot_database.db")
    c = conn.cursor()

    if action == "paid":
        c.execute("UPDATE withdrawals SET status='paid', processed_at=? WHERE id=?",
                  (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), withdrawal_id))
        conn.commit()
        conn.close()
        await query.edit_message_text(query.message.text + "\n\n✅ *MARKED AS PAID*", parse_mode="Markdown")
        try:
            await context.bot.send_message(user_id, t(user_id, "payment_sent", amount=f"{amount:.2f}"), parse_mode="Markdown")
        except:
            pass

    elif action == "decline":
        c.execute("UPDATE users SET balance=balance+?, total_withdrawn=total_withdrawn-? WHERE user_id=?",
                  (amount, amount, user_id))
        c.execute("UPDATE withdrawals SET status='declined', processed_at=? WHERE id=?",
                  (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), withdrawal_id))
        conn.commit()
        conn.close()
        await query.edit_message_text(query.message.text + "\n\n❌ *DECLINED & REFUNDED*", parse_mode="Markdown")
        try:
            await context.bot.send_message(user_id, t(user_id, "declined", amount=f"{amount:.2f}"), parse_mode="Markdown")
        except:
            pass

# ============================================================
# 18. ADMIN COMMANDS
# ============================================================
async def admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    conn = sqlite3.connect("bot_database.db")
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM users")
    total_users = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM task_submissions WHERE status='pending'")
    pending_tasks = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM withdrawals WHERE status='pending'")
    pending_withdrawals = c.fetchone()[0]
    c.execute("SELECT SUM(total_withdrawn) FROM users")
    total_paid = c.fetchone()[0] or 0
    conn.close()

    await update.message.reply_text(
        f"📊 *Bot Statistics*\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👥 *Total Users:* `{total_users}`\n"
        f"📸 *Pending Reviews:* `{pending_tasks}`\n"
        f"💸 *Pending Withdrawals:* `{pending_withdrawals}`\n"
        f"💰 *Total Paid Out:* `${total_paid:.2f}`",
        parse_mode="Markdown"
    )

async def admin_ban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    if not context.args:
        await update.message.reply_text("Usage: /ban <user_id>")
        return
    target_id = int(context.args[0])
    conn = sqlite3.connect("bot_database.db")
    c = conn.cursor()
    c.execute("UPDATE users SET is_banned=1 WHERE user_id=?", (target_id,))
    conn.commit()
    conn.close()
    await update.message.reply_text(f"✅ User `{target_id}` banned.", parse_mode="Markdown")

async def admin_addbalance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /addbalance <user_id> <amount>")
        return
    target_id = int(context.args[0])
    amount = float(context.args[1])
    conn = sqlite3.connect("bot_database.db")
    c = conn.cursor()
    c.execute("UPDATE users SET balance=balance+?, total_earned=total_earned+? WHERE user_id=?", (amount, amount, target_id))
    conn.commit()
    conn.close()
    await update.message.reply_text(f"✅ Added `${amount:.2f}` to user `{target_id}`.", parse_mode="Markdown")

async def cancel_conv(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    await update.message.reply_text(t(user_id, "action_cancelled"), reply_markup=get_main_menu(user_id))
    return ConversationHandler.END

async def back_to_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    await update.message.reply_text("🏠", reply_markup=get_main_menu(user_id))

async def change_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")],
        [InlineKeyboardButton("🇸🇴 Somali", callback_data="lang_so")]
    ])
    await update.message.reply_text(
        t(user_id, "language_select"),
        parse_mode="Markdown",
        reply_markup=keyboard
    )

# ============================================================
# 19. MAIN
# ============================================================
def main():
    init_db()
    app = Application.builder().token(BOT_TOKEN).build()

    earn_conv = ConversationHandler(
        entry_points=[
            MessageHandler(filters.Text([TEXTS["en"]["earn_money"], TEXTS["so"]["earn_money"]]), earn_money_start)
        ],
        states={
            UPLOAD_SCREENSHOT: [
                MessageHandler(filters.PHOTO, process_screenshot),
                MessageHandler(filters.Text([TEXTS["en"]["send_screenshot"], TEXTS["so"]["send_screenshot"]]), send_screenshot_prompt),
                MessageHandler(filters.Text([TEXTS["en"]["skip_task"], TEXTS["so"]["skip_task"]]), earn_money_start),
            ]
        },
        fallbacks=[
            MessageHandler(filters.Text([TEXTS["en"]["main_menu"], TEXTS["so"]["main_menu"],
                                         TEXTS["en"]["back_menu"], TEXTS["so"]["back_menu"]]), cancel_conv),
            CommandHandler("start", start)
        ]
    )

    withdraw_conv = ConversationHandler(
        entry_points=[
            MessageHandler(filters.Text([TEXTS["en"]["withdraw"], TEXTS["so"]["withdraw"]]), withdraw_start)
        ],
        states={
            WITHDRAW_METHOD: [
                MessageHandler(filters.Text([TEXTS["en"]["payout_request"], TEXTS["so"]["payout_request"]]), payout_start),
                MessageHandler(filters.Text([TEXTS["en"]["withdrawal_history"], TEXTS["so"]["withdrawal_history"]]), withdrawal_history),
                MessageHandler(filters.Text([TEXTS["en"]["confirm_btn"], TEXTS["so"]["confirm_btn"],
                                             TEXTS["en"]["cancel_btn"], TEXTS["so"]["cancel_btn"]]), withdraw_final),
            ],
            WITHDRAW_AMOUNT: [
                MessageHandler(filters.Text([
                    TEXTS["en"]["evc"], TEXTS["so"]["evc"],
                    TEXTS["en"]["premier"], TEXTS["so"]["premier"],
                    TEXTS["en"]["usdt"], TEXTS["so"]["usdt"]
                ]), withdraw_method_choice),
            ],
            WITHDRAW_DETAILS: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, withdraw_amount_choice),
            ],
            WITHDRAW_CONFIRM: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, withdraw_details_choice),
            ],
        },
        fallbacks=[
            MessageHandler(filters.Text([TEXTS["en"]["back_menu"], TEXTS["so"]["back_menu"]]), cancel_conv),
            CommandHandler("start", start)
        ]
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("language", change_language))
    app.add_handler(CommandHandler("stats", admin_stats))
    app.add_handler(CommandHandler("ban", admin_ban))
    app.add_handler(CommandHandler("addbalance", admin_addbalance))
    app.add_handler(earn_conv)
    app.add_handler(withdraw_conv)
    app.add_handler(CallbackQueryHandler(language_callback, pattern="^lang_"))
    app.add_handler(CallbackQueryHandler(check_subscription, pattern="^check_subscription$"))
    app.add_handler(CallbackQueryHandler(admin_callback, pattern="^(approve|reject)_"))
    app.add_handler(CallbackQueryHandler(admin_withdrawal_callback, pattern="^(paid|decline)_"))
    app.add_handler(MessageHandler(filters.Text([TEXTS["en"]["my_wallet"], TEXTS["so"]["my_wallet"]]), my_wallet))
    app.add_handler(MessageHandler(filters.Text([TEXTS["en"]["referral_link"], TEXTS["so"]["referral_link"]]), referral_link))
    app.add_handler(MessageHandler(filters.Text([TEXTS["en"]["support_help"], TEXTS["so"]["support_help"]]), support_help))
    app.add_handler(MessageHandler(filters.Text([TEXTS["en"]["contact_btn"], TEXTS["so"]["contact_btn"]]), contact_admin))
    app.add_handler(MessageHandler(filters.Text([TEXTS["en"]["settings"], TEXTS["so"]["settings"]]), change_language))
    app.add_handler(MessageHandler(filters.Text([TEXTS["en"]["back_menu"], TEXTS["so"]["back_menu"]]), back_to_menu))

    print("✅ Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
