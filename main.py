from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler , Updater , CallbackContext
from telegram import Update
from telegram.constants import ChatAction
from telegram import ReplyKeyboardMarkup
from telegram.ext import MessageHandler
from telegram.ext import filters
from telegram import InlineKeyboardMarkup
from telegram import InlineKeyboardButton
from telegram.ext import CallbackQueryHandler
from telegram.ext import ConversationHandler
import mysql.connector
import subprocess
user = "wikm"
password = "Mdmd@1383"
host = "127.0.0.1"
database = "UKCalendar"
db = mysql.connector.connect(user=user, password=password,
                              host=host , database = database)
cursor = db.cursor()

token = "7029093646:AAFqi8sFOTpJS_t-7GKYRLVZOuyajJa2xWw"
status = bool
# admin interface :
async def admin_handler (update : Update , context : CallbackContext) :
    admin_chat = 877591460
    chat_id = update.message.chat_id
    if chat_id == admin_chat :
        await context.bot.send_chat_action(chat_id , ChatAction.TYPING)
        await context.bot.sendMessage(chat_id , "سلام گلم . به محیط ادمین خوش آمدی")
        buttons = [
            [
                InlineKeyboardButton("ارسال بکاپ" , callback_data="send_backup"),
                InlineKeyboardButton("ارسال پیام همگانی" , callback_data="send_to_all")
            ]
        ]
        await update.message.reply_text(
            text="منو ادمین" ,
            reply_markup=InlineKeyboardMarkup(buttons)
        )

async def query_handler(update : Update , context : CallbackContext) :
    global user
    global password
    global database
    global db
    global cursor
    global status
    admin_chat = 877591460
    query = update.callback_query
    data = query.data
    chat_id = query.message.chat_id
    chat_id_str = str(chat_id)
    if data == "send_backup" :
        if chat_id == admin_chat :
            with open("./backup_file", 'wb') as file:
                subprocess.run(['mysqldump', '-u', user, '-p' + password, database], stdout=file)
            with open ("./backup_file" , "rb") as file :
                await context.bot.send_chat_action(chat_id , ChatAction.UPLOAD_DOCUMENT)
                await context.bot.send_document(chat_id , file , caption="BackUp File" , connect_timeout = 5000)
        await admin_handler(query , context)
    elif data == "send_to_all" :
        await context.bot.sendMessage(chat_id , "پیام موردنظر را وارد کنید : ")
        context.user_data['action'] = 'send'
    elif data == "change_status" :
        if status == True :
            query = "DELETE FROM users WHERE chat_id = " + chat_id_str
            cursor.execute(query)
            db.commit()
            await context.bot.sendMessage(chat_id , "ربات برای شما غیرفعال شد")
        elif status == False :
            await start(query , context)


async def text_handler (update : Update , context : CallbackContext) :
    chat_id = update.message.chat_id
    if context.user_data['action'] == "send" :
        name = update.message.text
        await context.bot.sendMessage(chat_id , name)
        context.user_data['action'] = " "

#start and user interface:
        
async def start (update : Update , context : CallbackContext) :
    global db
    global cursor
    global status
    chat_id = update.message.chat_id
    fisrname = update.message.chat.first_name
    lastname = update.message.chat.last_name
    if fisrname == None :
        fisrname = " "
    if lastname == None :
        lastname = " "
    status_check_in_database(chat_id)
    if status == False :
        query = "INSERT INTO users (name, chat_id) VALUES (%s, %s)"
        values = (fisrname+" " + lastname, chat_id)
        cursor.execute(query, values)
        db.commit()
        await context.bot.send_chat_action(chat_id , ChatAction.TYPING)
        await context.bot.sendMessage(chat_id , " سلام " + str(fisrname) + " " + str(lastname) + "خوش آمدی")
        await context.bot.sendMessage(chat_id , "بات با موفقیت برای شما فعال شد")

    await context.bot.send_chat_action(chat_id , ChatAction.TYPING)
    #await context.bot.sendMessage(chat_id , " سلام " + str(fisrname) + " " + str(lastname))
    #await context.bot.sendMessage(chat_id , "بات با موفقیت برای شما فعال شد")
    await user_menu(update , context)

async def user_menu(update : Update , context : CallbackContext) :
    buttons = [
        ["تقویم آموزشی ترم"],
        ["مشاهده وضعیت"] ,
        ["درباره"]
    ]
    await update.message.reply_text(text="منو اصلی :" , reply_markup=ReplyKeyboardMarkup(buttons , resize_keyboard=True))

async def send_calendar(update : Update , context : CallbackContext) :
    chat_id = update.message.chat_id
    with open ("./calendar.jpg" , "rb") as file :
        await context.bot.send_chat_action(chat_id , ChatAction.UPLOAD_PHOTO)
        await context.bot.sendPhoto(chat_id , file , caption="تقویم آموزشی" , connect_timeout = 5000)

async def about(update : Update , context : CallbackContext) :
    chat_id = update.message.chat_id
    await context.bot.send_chat_action(chat_id , ChatAction.TYPING)
    await context.bot.sendMessage(chat_id , "Created By @wikm360 with ❤️")

def status_check_in_database(chat_id) :
    global status
    global db
    global cursor
    status = False
    chat_id_str = str(chat_id)
    query = "SELECT * FROM users"
    cursor.execute(query)
    records = cursor.fetchall()
    for record in records:
        if record[2] == chat_id_str :
            status = True
            break
        else :
            pass


async def status_check(update : Update , context : CallbackContext) :
    global status
    global db
    global cursor
    chat_id = update.message.chat_id
    status_check_in_database(chat_id)
    if status == True :
        await context.bot.sendMessage(chat_id , "ربات برای شما فعال میباشد")
    elif status == False :
        await context.bot.sendMessage(chat_id , "ربات برای شما فعال نمیباشد")
    buttons = [
            [
                InlineKeyboardButton("تغییر وضعیت" , callback_data="change_status")
            ]
        ]
    await update.message.reply_text(
        text="عملیات :" ,
        reply_markup=InlineKeyboardMarkup(buttons)) #request send to query handler

def main () :
    application = ApplicationBuilder().token(token).build()
    application.add_handler(CommandHandler("start" , start))
    application.add_handler(CommandHandler("admin" , admin_handler))

    application.add_handler(CallbackQueryHandler(query_handler))

    application.add_handler(MessageHandler(filters.Regex("تقویم آموزشی ترم") , send_calendar))
    application.add_handler(MessageHandler(filters.Regex("مشاهده وضعیت") , status_check))
    application.add_handler(MessageHandler(filters.Regex("درباره") , about))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND , text_handler))

    application.run_polling()


main()