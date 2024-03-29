import requests
import schedule
from pytz import timezone
import time
from datetime import datetime
import mysql.connector
from databasedetail import user_input , password_input , host_input , database_input , token

list = []
date = []

def get_from_db() :
    global user_input , password_input , host_input , database_input
    db = mysql.connector.connect(user=user_input, password=password_input,
                                host=host_input , database = database_input)
    cursor = db.cursor()
    global list

    query = "SELECT chat_id FROM users"
    ## getting records from the table
    cursor.execute(query)
    ## fetching all records from the 'cursor' object
    records = cursor.fetchall()
    ## Showing the data
    for record in records:
        list.append(str(record).split("(")[1].split(")")[0].split(",")[0].split("'")[1])
    return list

def send_message_every () :
    global token
    global list
    get_from_db()
    for user in list :
        requests.get("https://api.telegram.org/bot" + token + "/sendMessage" + "?chat_id=" + user + "&text=" + "برای هفته آینده غذا رزرو کنید")
    list.clear()

def send_message_specific () :
    global token
    global list
    global date
    get_from_db()
    with open ("./date.txt" , "r") as file :
        for line in file :
            date = line.split(",")[0].strip()
            event = line.split(",")[1].strip()
            specific_date = datetime.strptime(date, '%Y-%m-%d') 
            current_date = datetime.now()
            if specific_date.date() == current_date.date():
                for user in list :
                    requests.get("https://api.telegram.org/bot" + token + "/sendMessage" + "?chat_id=" + user + "&text=" + " یادآوری " + event)
                list.clear()

def main() :
    schedule.every().wednesday.at("09:00" , timezone("Asia/Tehran")).do(send_message_every)
    schedule.every().day.at("08:00" , timezone("Asia/Tehran")).do(send_message_specific)
    while True :
        schedule.run_pending()
        time.sleep(1)


main()