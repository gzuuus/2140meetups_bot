# ==> External libraries
from pandas import *  
from PIL import Image, ImageDraw, ImageFont
from collections import defaultdict
from time import strptime, strftime
from telebot.types import ReplyKeyboardMarkup, ReplyKeyboardRemove, ForceReply, InlineKeyboardMarkup, InlineKeyboardButton
from pilmoji import Pilmoji
# Environment file reader
from dotenv import load_dotenv
# OS: Provides ways to access the OS and allows to read the environment variables
import time, os, telebot, textwrap, threading,requests, json, schedule
import pandas as pd

# ==> Local files
from constants import *
from helpers.proxy import *
from helpers.utils import *
from classes.meetup import *

from telebot import apihelper

print(f'loading the environment file...')
load_dotenv()
env = os.getenv(ENV)
bot_token = os.getenv(BOT_TOKEN)
print(f'Started at {timestamp()} in "{env}" environment')
print(f'2140-meetups bot started with "{bot_token}" token')
# Add proxy when we start the bot
if env == STAGING or env == PROD:
    apihelper.proxy = PROXY

bot=telebot.TeleBot(bot_token)


## MESSAGE HANDLERS
@bot.message_handler(commands=['start'])
def cmd_buttons(message):
    bot.send_message(message.chat.id, f'{hi_msg}', parse_mode='html', disable_web_page_preview=True)

@bot.message_handler(commands=['get_meetups'])
def get_menu(message):
    markup= ReplyKeyboardMarkup(row_width=1, one_time_keyboard=True, resize_keyboard=True, input_field_placeholder='Select from list')
    markup.add(NEXT_MEETUPS)
    markup.add(COMMUNITIES)
    msg = bot.send_message(message.chat.id, 'Escoge una accion', reply_markup=markup)
    bot.register_next_step_handler(msg, select_group)

@bot.message_handler(commands=['feed'])
def subscribe_feed(message):
    markup = InlineKeyboardMarkup(row_width=2)
    msg=[message.chat.id]
    clean_mssid_list=get_subscription_list()

    # If the user is in the subscription list
    if message.chat.id in clean_mssid_list:
        b1 = InlineKeyboardButton(CANCEL_SUBSCRIPTION, callback_data='cancel_sub')
        markup.add(b1)
        bot.send_message(message.chat.id, feed_msg, parse_mode='html', disable_web_page_preview=True)
        x= bot.send_message(message.chat.id, ALREADY_SUBSCRIBED, reply_markup=markup)
        time.sleep(10)
        bot.delete_message(message.chat.id, x.message_id)
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
        print(f'{timestamp()} New subscription: {msg}')
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
    update(message.chat.id, 7)

##Callbacks
@bot.callback_query_handler(func=lambda x: True)
def b_inline(call):
    subscription_path=os.getenv(SUBS_DB_PATH)   
    chat_id=call.json['message']['chat']['id']
    if call.data == 'cancel_sub':
        df = pd.read_csv(subscription_path)
        df.drop(df.index[(df["chat_id"] == chat_id)],axis=0,inplace=True)
        df.to_csv(subscription_path, mode='w+', index=False)
        bot.send_message(chat_id, '🔸Suscripcion cancelada')
        print(f'{timestamp()}cancel_sub: {chat_id}')
    if call.data == 'get_meetups':
        meetup_feed(chat_id)
    if call.data == 'get_feed':
        update(chat_id, 7)


## GET_MEETUPS helpers
def select_group(message):    
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
        for i in range(1, pages):  
            url=(f"http://2140meetups.com/wp-json/wp/v2/community?page={i}&per_page=50")  
            # Make request
            response = make_request(url, GET)      
            #response = requests.get(url, headers=headers ).json()
            t_items=len(response)

            for x in range(t_items):
                group_list.append(response[x]['title']['rendered'])

        for i in range(len(group_list)):
            markup.add(group_list[i])

        msg = bot.send_message(message.chat.id, f'Escoge una de las {total_communities} comunidades?', reply_markup=markup)
        bot.register_next_step_handler(msg, get_events)
    else:
        meetup_feed(message.chat.id)

def get_events(message):
    markup= ReplyKeyboardRemove()
    group_selected= message.text
    event_counter=0
    url=(community_100)
    response=make_request(url, GET)
    total_entries=len(response)

    for i in range(total_entries):   

        if response[i]['comunidad'][0]['post_title'] == group_selected:
            # Create new meetup
            meetup=Meetup(response[i])
            # Get display format for meetup
            output=meetup.format()
            bot.send_photo(message.chat.id, meetup.image, output, reply_markup=markup)
            event_counter += 1

    if event_counter==0:
        bot.send_message(message.chat.id, 'No hay meetups de esta comunidad...\n\n📮 /get_meetups', reply_markup=markup)


def meetup_feed(messageid):
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
            bot.send_photo(messageid, meetup.image, output, parse_mode="html", reply_markup=markup)
        except:
            pass





##Updates
def update(message, daysoffset):
    print(f'{timestamp()} update start')
    url=(meetup_all)
    startdate = time.strftime('%Y-%m-%d')
    if message == 'none':
        clean_mssid_list=get_subscription_list()
    else:
        clean_mssid_list=[message]
    response=make_request(url, GET)
    total_entries=len(response)
    get_events_dict={}
    daily_meetups_list=[]
    delete_msg_list={}
    next_dates_list=[]
    for i in range(daysoffset):
        next_date = (pd.to_datetime(startdate) + pd.DateOffset(days=i)).strftime('%Y-%m-%d')
        next_dates_list.append(next_date)
    for i in range(total_entries):
        meetup_date=response[i]['fecha']
        if meetup_date in next_dates_list:
            daily_meetups_list.append(i)
    for x in range(len(clean_mssid_list)):
        try:
            if len(daily_meetups_list) == 0:
                markup = InlineKeyboardMarkup(row_width=2)
                b1 = InlineKeyboardButton('Consultar proximos meetups', callback_data='get_meetups')
                if not range(total_entries) == 0:
                    markup.add(b1)
                msg=bot.send_message(clean_mssid_list[x], f'No hay meetups esta semana, estas al dia', parse_mode='html', reply_markup=markup)
                delete_msg_list[x]={}
                delete_msg_list[x]['msg_id']=msg.message_id
                delete_msg_list[x]['chat_id']=message
            else:
                bot.send_message(clean_mssid_list[x], f'Meetups en los proximos {daysoffset} dias: {len(daily_meetups_list)}', parse_mode='html')
                for i in daily_meetups_list:
                    meetup=Meetup(mini=response[daily_meetups_list[i]])
                    output=meetup.format_mini()
                    bot.send_message(clean_mssid_list[x], f'{output}', parse_mode='html', disable_web_page_preview=True)
        except:
            pass
    if message == 'none':
        print(f'{timestamp()}week feed sent, date')
    else:
        print(f'{timestamp()}single update sent to: {message}')
    if not range(total_entries) == 0:
        time.sleep(15)
        try:
            for i in range(len(delete_msg_list)):
                bot.delete_message(delete_msg_list[i]['chat_id'], delete_msg_list[i]['msg_id'])
        except:
            pass

def daily_update(message):
    print(f'{timestamp()} checking if there are meetups today...')
    url=(meetup_all)
    startdate = time.strftime('%Y-%m-%d')
    response=make_request(url, GET)
    total_entries=len(response)
    daily_meetups_list=[]
    for i in range(total_entries):
        meetup_date=response[i]['fecha']
        # Filter just the actual date meetups
        if meetup_date == startdate:
            daily_meetups_list.append(i)
    if len(daily_meetups_list) == 0:
        print(f'{timestamp()} daily update sent: No events today')
        return False
    else:
        if message == 'none':
            clean_mssid_list=get_subscription_list()
        else:
            clean_mssid_list=[message]

        get_events_dict={}

        for x in clean_mssid_list:
            bot.send_message(x, '⚡Hoy hay meetup!!')
            for i in range(len(daily_meetups_list)):

                meetup=Meetup(mini=response[daily_meetups_list[i]])
                output=meetup.format_mini()
                
                try:
                    bot.send_message(x, f'{output}', parse_mode='html', disable_web_page_preview=True)
                except:
                    pass        
        print(f'{timestamp()} daily update sent')
        return True

def new_community():
    url=(community_all)
    header=make_request(url, HEAD)
    response=make_request(url, GET)
    total_com=int(header.headers['x-wp-total'])
    print(f'{timestamp()}Sync communities, total: {total_com}')
    while True:
        total_com_u=int(header.headers['x-wp-total'])
        if total_com == total_com_u:
            print(f'{timestamp()}Sync... {total_com}')
        else:
            title=response[0]['title']['rendered']
            city=response[0]['ciudad']
            country=response[0]['pais']
            link=response[0]['link']
            output_com=f'🟠Nueva comunidad: {title} \n📍Ciudad: {city}, Pais: {country}\n🔗Link: {link}'
            print(f'{timestamp()}New com: {title}, {link}')
            total_com == total_com_u
            for x in get_subscription_list():
                try:
                    bot.send_message(x, output_com)
                except:
                    pass
        # Sleep an two hours and wake up to see if new meetup is published
        time.sleep(TWO_HOURS)

def new_meetup():
    url=(meetup_all)
    header=make_request(url, HEAD)
    response=make_request(url, GET)
    total_meet=int(header.headers['x-wp-total'])
    print(f'{timestamp()}Sync meetups, total: {total_meet}')
    while True:
        total_meet_u=int(header.headers['x-wp-total'])
        if total_meet == total_meet_u:
            print(f'{timestamp()}Sync... {total_meet_u}')
        else:
            title=response[0]['title']['rendered']
            comm=response[0]['comunidad'][0]['post_title']
            cat=response[0]['taxonomy_info']['cat_meetup'][0]['label']
            link=response[0]['link']
            date=response[0]['fecha']
            output_meet=f'🟠**Nuevo meetup:** {title} \n📍**Comunidad:** {comm}\n💡**Cat:** {cat}\n🗓️**Fecha:** {date}\n🔗**Link:** {link}'
            print(f'{timestamp()}New meetup: {title}, {link}')
            total_meet == total_meet_u
            for x in get_subscription_list():
                try:
                    bot.send_message(x, output_meet, parse_mode='markdown')
                except:
                    pass
        # Sleep an hour and wake up to see if new meetup is published
        time.sleep(ONE_HOUR)

def schedule_thread():
    #Scheduled works
    schedule.every().day.at('10:40').do(daily_update, message='none')
    schedule.every().monday.at("10:00").do(update, message='none', daysoffset=7)
    schedule.every().thursday.at("21:40").do(update, message='none', daysoffset=7)
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