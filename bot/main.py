# ==> External libraries
from pandas import *
from collections import defaultdict
from time import strptime, strftime
from telebot.types import ReplyKeyboardMarkup, ReplyKeyboardRemove, ForceReply, InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton
# Environment file reader
from dotenv import load_dotenv
# OS: Provides ways to access the OS and allows to read the environment variables
import time, os, telebot, threading, schedule
import pandas as pd
from datetime import timedelta, date
import json

# ==> Local files
from constants import *
from helpers.httprequests import *
from helpers.utils import *
from helpers.logs import *
from classes.meetup import *
from classes.community import *
from classes.db import *

# Load the environment variables
load_dotenv()
env = os.getenv(ENV)
bot_token = os.getenv(BOT_TOKEN)
display_log(f'Started at {timestamp()} in "{env}" environment')
display_log(f'2140-meetups bot started with "{bot_token}" token')
# Make sure the database exist in the project,
DB.create_db()
# Initialise the bot
bot=telebot.TeleBot(bot_token)

## MESSAGE HANDLERS
@bot.message_handler(commands=['start'])
def cmd_buttons(message):
    """Activate the bot in a telegram group"""
    bot.send_message(message.chat.id, f'{hi_msg}', parse_mode='html', disable_web_page_preview=True)

@bot.message_handler(commands=['get_meetups'])
def get_menu(message):
    """Display the meetups in different way:
    - Community: Display just the selected community meetup
    - Proximos meetups: Get all the next week meetups without filter
    """
    markup= ReplyKeyboardMarkup(row_width=1, one_time_keyboard=True, resize_keyboard=True)
    itembtn1 = KeyboardButton(NEXT_MEETUPS)
    itembtn2 = KeyboardButton(COMMUNITIES)
    markup.add(itembtn1, itembtn2)
    msg = bot.send_message(message.chat.id, 'Escoge una accion', reply_markup=markup)
    bot.register_next_step_handler(msg, display_options)

@bot.message_handler(commands=['feed'])
def subscribe_feed(message):
    """Subscribe to weekly or daily meetups notification
    Once we activate, we have the option the deactivate
    """
    markup = InlineKeyboardMarkup(row_width=2)
    msg=[message.chat.id]
    clean_mssid_list=DB.get_subscription_list()

    # If the user is in the subscription list, it has the option to cancelled
    if message.chat.id in clean_mssid_list:
        b1 = InlineKeyboardButton(CANCEL_SUBSCRIPTION, callback_data='cancel_sub')
        markup.add(b1)
        bot.send_message(message.chat.id, feed_msg, parse_mode='html', disable_web_page_preview=True)
        x= bot.send_message(message.chat.id, ALREADY_SUBSCRIBED, reply_markup=markup)
        time.sleep(10)
        bot.delete_message(message.chat.id, x.message_id)
    # The user subscribes to the feed
    else:
        b1 = InlineKeyboardButton(ALL_FEED, callback_data='get_feed')
        markup.add(b1)
        mssid= {'chat_id': msg}
        df=pd.DataFrame(mssid)
        subscription_path=os.getenv(SUBS_DB_PATH)
        # Write in the CSV file using pandas
        if not os.path.exists(subscription_path):
            df.to_csv(subscription_path, mode='w', index=False)
        else:
            df.to_csv(subscription_path, mode='a', index=False, header=False)
        display_log(f"New subscription: {msg}")
        # Send message back to the user
        bot_answer=bot.send_message(message.chat.id, feed_subscription_msg, reply_markup=markup)
        bot.send_message(message.chat.id, feed_msg, parse_mode='html', disable_web_page_preview=True)
        daily_update(message.chat.id)
        time.sleep(10)
        bot.delete_message(message.chat.id, bot_answer.message_id)

@bot.message_handler(commands=['get_feed'])
def get_instant_feed(message):
    # Print the actual day meetups
    daily_update(message.chat.id)
    # Print next 7 days meetups
    display_meetups_in_a_range(message.chat.id, WEEK)

##Callbacks: A response that we get when we click a button
@bot.callback_query_handler(func=lambda x: True)
def b_inline(call):
    subscription_path=os.getenv(SUBS_DB_PATH)
    chat_id=call.json['message']['chat']['id']
    if call.data == 'cancel_sub':
        df = pd.read_csv(subscription_path)
        df.drop(df.index[(df["chat_id"] == chat_id)],axis=0,inplace=True)
        df.to_csv(subscription_path, mode='w+', index=False)
        bot.send_message(chat_id, '🔸Suscripcion cancelada')
        display_log(f"Subscription cancelled: {chat_id}")
    if call.data == 'get_meetups':
        meetup_feed(chat_id)
    if call.data == 'get_feed':
        display_meetups_in_a_range(chat_id, WEEK)


## GET_MEETUPS helpers
def display_options(message):
    """ Display the user the selected option in the /get_meetups command
    @message: User selected action information
    """
    #The user select to display the community meetups. Once we choose the community, we show the next meetups
    if message.text == COMMUNITIES:
        markup= ReplyKeyboardMarkup(row_width=1, one_time_keyboard=True, resize_keyboard=True, input_field_placeholder='Select from list')
        # Make request
        communities_header = make_request(community_50, HEAD)
        # Extract info from the header
        pages=int(communities_header.headers['x-wp-totalpages']) + 1
        total_communities=int(communities_header.headers['x-wp-total'])
        # Send message to the client
        # Maybe add some interactive timer to see that something is happening in the background
        bot.send_message(message.chat.id, 'Escraping comunidades...')
        group_list=[]
        communities={}

        for i in range(1, pages):
            url=community_pagination % i
            # Make request
            response = make_request(url, GET)
            #response = requests.get(url, headers=headers ).json()
            t_items=len(response)

            for x in range(t_items):
                community_name=response[x]['title']['rendered']
                community_id=response[x]['id']
                communities[community_name] = community_id
                group_list.append(KeyboardButton(community_name))

        for i in range(len(group_list)):
            markup.add(group_list[i])

        msg = bot.send_message(message.chat.id, f'Escoge una de las {total_communities} comunidades', reply_markup=markup)
        bot.register_next_step_handler(msg, get_community_meetups, communities)
    # The user chooses to display all the meetups
    else:
        meetup_feed(message.chat.id)

def get_community_meetups(message, communities):
    """Display all the meetups of one community
    @message: User selected action information"""
    community_id=communities[message.text]
    print(f"{message.text} community selected with {community_id} id")
    markup= ReplyKeyboardRemove()
    url=community_meetups % (community_id)
    response=make_request(url, GET)
    total_entries=len(response)

    if total_entries == 0:
        bot.send_message(message.chat.id, 'No hay meetups de esta comunidad...\n\n📮 /get_meetups', reply_markup=markup)
    
    else:
        for i in range(total_entries):
            # Create new meetup
            meetup=Meetup(response[i])
            # Get display format for meetup
            output=meetup.format()
            bot.send_photo(message.chat.id, meetup.image, output, reply_markup=markup)
        


def meetup_feed(chat_id):
    """Find the most recent meetups
    @chat_id: User telegram chat id
    WARNING: Technically we are bringing just three. Do not know if that ones are the incoming ones
    """
    markup= ReplyKeyboardRemove()
    get_events_dict={}
    url=(meetup_3)
    response=make_request(url, GET)
    total_entries=len(response)

    for i in range(total_entries):
        # Create new meetup
        meetup=Meetup(response[i])
        # Get display format for meetup
        output=meetup.format()
        try:
            bot.send_photo(chat_id, meetup.image, output, parse_mode="html", reply_markup=markup)
        except:
            pass

def display_meetups_in_a_range(message, days_offset):
    """Notify the users the meetups between dates
    @message: The id of the user channel. "none" set when we want to broadcast to all the subscribers
    @days_offset: Number of days started from actual date
    """
    display_log("Fetching all meetups between a timeframe...")

    if message == 'none':
        clean_mssid_list=DB.get_subscription_list()
    else:
        clean_mssid_list=[message]

    # Define the timeframes that we want to fetch
    start_date = time.strftime('%Y-%m-%d')
    end_date = date.today() + timedelta(days=days_offset)
    # Create the URL
    timeframe_url=timeframe_meetups % (start_date, end_date)
    timeframe_meetups_list=make_request(timeframe_url, GET)

    total_entries=len(timeframe_meetups_list)

    get_events_dict={}
    delete_msg_list={}

    for x in range(len(clean_mssid_list)):
        try:
            if len(timeframe_meetups_list) == 0:
                markup = InlineKeyboardMarkup(row_width=2)
                b1 = InlineKeyboardButton('Consultar proximos meetups', callback_data='get_meetups')
                if not range(total_entries) == 0:
                    markup.add(b1)
                msg=bot.send_message(clean_mssid_list[x], f'No hay meetups esta semana, estas al dia', parse_mode='html', reply_markup=markup)
                delete_msg_list[x]={}
                delete_msg_list[x]['msg_id']=msg.message_id
                delete_msg_list[x]['chat_id']=message
            else:
                bot.send_message(clean_mssid_list[x], f'Meetups en los proximos {days_offset} dias: {len(timeframe_meetups_list)}', parse_mode='html')
                # Print all the meetups in the subscribed user channel (chat)
                for i in range(len(timeframe_meetups_list)):
                    meetup=Meetup(timeframe_meetups_list[i])
                    output=meetup.format_mini()
                    bot.send_message(clean_mssid_list[x], f'{output}', parse_mode='html', disable_web_page_preview=True)
        except Exception as error:
            print("Error: display_meetups_in_a_range")
            print(error)
            pass
    if message == 'none':
        display_log("Weekly subscriptions sent")
    else:
        display_log(f"Displayed to particular user ({message}) meetups")
    # Delete messages from the chat???
    if not range(total_entries) == 0:
        time.sleep(15)
        try:
            for i in range(len(delete_msg_list)):
                bot.delete_message(delete_msg_list[i]['chat_id'], delete_msg_list[i]['msg_id'])
        except:
            pass

def daily_update(message):
    """Get the actual date meetups
    @message: Could be user button action info or user channel id
    """
    display_log("checking if there are meetups today...")
    actual_date = time.strftime('%Y-%m-%d')
    url=day_meetups % (actual_date)
    response=make_request(url, GET)

    if len(response) == 0:
        display_log(f"Daily update sent, it does not exist any event today ({actual_date})")
        return False
    else:
        # Choose to whom direct the messages: Particular user or subscribers
        if message == 'none':
            clean_mssid_list=DB.get_subscription_list()
        else:
            clean_mssid_list=[message]

        for x in clean_mssid_list:
            bot.send_message(x, '⚡ Hoy hay meetup(s)!!')
            ## Display all the meetups
            for i in range(len(response)):

                meetup=Meetup(response[i])
                output=meetup.format_mini()

                try:
                    bot.send_message(x, f'{output}', parse_mode='html', disable_web_page_preview=True)
                except:
                    pass
        display_log(f"Actual date, {actual_date}, meetups fetched succesfully!")
        return True

def new_community():
    """Create a thread that checks each two hours if there are new communities"""
    url=(community_all)
    header=make_request(url, HEAD)
    response=make_request(url, GET)
    total_com=int(header.headers['x-wp-total'])
    display_log(f"communities sync! total of {total_com}")
    while True:
        # How do we know if we get a new meetup
        # Shouldn't be the query inside the loop?
        total_com_u=int(header.headers['x-wp-total'])
        if total_com == total_com_u:
            print(f'{timestamp()} community sync... {total_com}')
        else:
            new_commumity=Community(response[0])
            output=new_commumity.format()
            display_log(f"New community! {new_commumity.title}, {new_commumity.link}")
            total_com == total_com_u
            for channel_id in DB.get_subscription_list():
                try:
                    bot.send_message(channel_id, output)
                except:
                    pass
        # Sleep an two hours and wake up to see if new meetup is published
        time.sleep(TWO_HOURS)

def new_meetup():
    """Create a thread that checks each hour if there are new meetups """
    url=(meetup_all)
    header=make_request(url, HEAD)
    response=make_request(url, GET)
    total_meet=int(header.headers['x-wp-total'])
    display_log(f"meetup sync! total of {total_meet}")
    while True:
        # How do we know if we get a new meetup
        # Shouldn't be the query inside the loop?
        total_meet_u=int(header.headers['x-wp-total'])
        if total_meet == total_meet_u:
            print(f'{timestamp()} meetup sync... {total_meet_u}')
        else:

            new_meetup=Meetup(response[0])
            output=new_meetup.format_new()
            display_log(f"New meetup: {self.title}, {self.link}")
            total_meet == total_meet_u
            for channel_id in DB.get_subscription_list():
                try:
                    bot.send_message(channel_id, output, parse_mode='html', disable_web_page_preview=True)
                except:
                    pass
        # Sleep an hour and wake up to see if new meetup is published
        time.sleep(ONE_HOUR)

def schedule_thread():
    #Scheduled works
    schedule.every().day.at(DAYLY_UPDATE_TIME).do(daily_update, message='none')
    schedule.every().monday.at(WEEKLY_UPDATE_TIME).do(display_meetups_in_a_range, message='none', days_offset=WEEK)
    # Duplicating the weekly meetups subscription. Decide if it is need it
    #schedule.every().thursday.at("21:40").do(display_meetups_in_a_range, message='none', days_offset=WEEK)
    while True:
        schedule.run_pending()
        time.sleep(1)

#Threading polling
def polling():
    try:
        bot.infinity_polling()
    except:
        pass

# Create all the commands of the bot
if __name__=='__main__':
    try:
        bot.set_my_commands([
            telebot.types.BotCommand(start, start_msg),
            telebot.types.BotCommand(meetups, meetups_msg),
            telebot.types.BotCommand(feed, feed_msg),
            telebot.types.BotCommand(get_feed, get_feed_msg)
        ])
        thread_schedule= threading.Thread(name='thread_schedule', target=schedule_thread)
        thread_schedule.start()

        thread_polling= threading.Thread(name='thread_polling', target=polling)
        thread_polling.start()

        # Display a new message when a new community is created in the DB
        thread_com_u= threading.Thread(name='thread_com_u', target=new_community)
        thread_com_u.start()

        # Display a new message when a new meetup is created in DB
        thread_meet_u= threading.Thread(name='thread_meet_u', target=new_meetup)
        thread_meet_u.start()
    except Exception as error:
        # Still testing...
        print(error)
        print("Error in the main function")
        pass
