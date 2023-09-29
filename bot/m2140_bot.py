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
from proxy import *
from utils import *

# for production use to activate proxy
from telebot import apihelper


# DOCKER
# Start the telegram bot
print(f'loading the environment file...')
load_dotenv()
env = os.getenv(ENV)
bot_token = os.getenv(BOT_TOKEN)
print(f'Started at {timestamp()} in "{env}" environment')
print(f'2140-meetups bot started with "{bot_token}" token')
bot=telebot.TeleBot(bot_token)

# PROD
# Start the telegram bot
#print(f'loading the environment file...')
#load_dotenv()
#env = os.getenv(ENV)
#bot_token = os.getenv(BOT_TOKEN)
#print(f'Started at {timestamp()} in "{env}" environment')
#print(f'2140-meetups bot started with "{bot_token}" token')
#apihelper.proxy = PROXY
#bot=telebot.TeleBot(bot_token)


## Message handlers
@bot.message_handler(commands=['start'])
def cmd_buttons(message):
    bot.send_message(message.chat.id, f'{hi_msg}', parse_mode='html', disable_web_page_preview=True)

@bot.message_handler(commands=['get_meetups'])
def get_menu(message):
    markup= ReplyKeyboardMarkup(row_width=1, one_time_keyboard=True, resize_keyboard=True, input_field_placeholder='Select from list')
    markup.add('Proximos meetups')
    markup.add('Comunidades')
    msg = bot.send_message(message.chat.id, 'Escoge una accion', reply_markup=markup)
    bot.register_next_step_handler(msg, select_group)

# HELPER
def select_group(message):    
    if message.text == 'Comunidades':
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
        meetupfeed(message.chat.id)



@bot.message_handler(commands=['feed'])
def subscribe_feed(message):
    markup = InlineKeyboardMarkup(row_width=2)
    msg=[message.chat.id]
    # Get the environment variable
    db_dir=os.getenv(DB_DIR)
    if not os.path.exists(db_dir):
        os.mkdir(db_dir)
    clean_mssid_list=get_subs_list()
    if message.chat.id in clean_mssid_list:
        b1 = InlineKeyboardButton('Cancelar suscripcion', callback_data='cancel_sub')
        markup.add(b1)
        bot.send_message(message.chat.id, feed_msg, parse_mode='html', disable_web_page_preview=True)
        x= bot.send_message(message.chat.id, 'Ya estas suscrito', reply_markup=markup)
        time.sleep(10)
        bot.delete_message(message.chat.id, x.message_id)
    else:
        b1 = InlineKeyboardButton('Mostrar feed completo', callback_data='get_feed')
        markup.add(b1)
        mssid= {'chat_id': msg}
        df=pd.DataFrame(mssid)   
        subscription_path=os.getenv(SUBS_DB_PATH)     
        if not os.path.exists(subscription_path):
            df.to_csv(subscription_path, mode='w', index=False)
        else:
            df.to_csv(subscription_path, mode='a', index=False, header=False)
        print(f'{timestamp()}new sub: {msg}')
        
        x= bot.send_message(message.chat.id, '✅Te has suscrito al feed, ahora recibirás notificaciones sobre los meetups de 2140meetups.com', reply_markup=markup)
        bot.send_message(message.chat.id, feed_msg, parse_mode='html', disable_web_page_preview=True)
        daily_update(message.chat.id)
        time.sleep(10)
        bot.delete_message(message.chat.id, x.message_id)

@bot.message_handler(commands=['get_feed'])
def get_instant_feed(message):
    daily_update(message.chat.id)
    update(message.chat.id, 7)

##Helpers
def get_events(message):
    markup= ReplyKeyboardRemove()
    group_selected= message.text
    get_events_dict={}
    url=(community_100)
    #response=requests.get(url, headers=headers).json()
    response=make_request(url, GET)
    total_entries=len(response)
    for i in range(total_entries):      
        if response[i]['comunidad'][0]['post_title'] == group_selected:

            get_events_dict[i]={}
            get_events_dict[i]['event_title']=response[i]['title']['rendered']
            get_events_dict[i]['event_group']=response[i]['comunidad'][0]['post_title']
            get_events_dict[i]['event_cat']=response[i]['taxonomy_info']['cat_meetup'][0]['label']
            get_events_dict[i]['event_page_link']=response[i]['link']
            get_events_dict[i]['event_date']=response[i]['fecha']
            get_events_dict[i]['event_hour']=response[i]['hora']
            get_events_dict[i]['event_location']=response[i]['direccion']

            if response[i]['featured_image_src_large']:
                get_events_dict[i]['event_feature_image']=response[i]['featured_image_src_large'][0]
            else: 
                get_events_dict[i]['event_feature_image']=default_banner

            output_get_events=outm_name + get_events_dict[i]['event_title']+ outm_group+ get_events_dict[i]['event_group']+ outm_cat+get_events_dict[i]['event_cat'] + outm_location + get_events_dict[i]['event_location'] + outm_date + get_events_dict[i]['event_date'] + outm_hour + get_events_dict[i]['event_hour'] + outm_location_link + get_events_dict[i]['event_page_link']
            bot.send_photo(message.chat.id, get_events_dict[i]['event_feature_image'], output_get_events, reply_markup=markup)

    if len(get_events_dict)==0:
        bot.send_message(message.chat.id, 'No hay meetups de esta comunidad... /get_meetups', reply_markup=markup)

def meetupfeed(messageid):
    markup= ReplyKeyboardRemove()
    get_events_dict={}
    url=(meetup_3)
    #response=requests.get(url, headers=headers ).json()
    response=make_request(url, GET)
    total_entries=len(response)
    for i in range(total_entries):
        get_events_dict[i]={}
        get_events_dict[i]['event_title']=response[i]['title']['rendered']
        get_events_dict[i]['event_group']=response[i]['comunidad'][0]['post_title']
        get_events_dict[i]['event_cat']=response[i]['taxonomy_info']['cat_meetup'][0]['label']
        get_events_dict[i]['event_page_link']=response[i]['link']
        get_events_dict[i]['event_date']=response[i]['fecha']
        get_events_dict[i]['event_hour']=response[i]['hora']
        get_events_dict[i]['event_location']=response[i]['direccion']
        if response[i]['featured_image_src_large']:
            get_events_dict[i]['event_feature_image']=response[i]['featured_image_src_large'][0]
        else: get_events_dict[i]['event_feature_image']=default_banner
        output_get_events=outm_name + get_events_dict[i]['event_title']+ outm_group+ get_events_dict[i]['event_group']+ outm_cat+get_events_dict[i]['event_cat'] + outm_location + get_events_dict[i]['event_location'] + outm_date + get_events_dict[i]['event_date'] + outm_hour + get_events_dict[i]['event_hour'] + outm_location_link + get_events_dict[i]['event_page_link']
        try:
            bot.send_photo(messageid, get_events_dict[i]['event_feature_image'], output_get_events, parse_mode="html",reply_markup=markup)
        except:
            pass

def get_subs_list():
    db_dir=os.getenv(DB_DIR) 
    subscription_path=os.getenv(SUBS_DB_PATH) 
    if not os.path.exists(db_dir):
        os.mkdir(db_dir)
    data = read_csv(subscription_path)
    mssid_list = data['chat_id'].tolist()
    clean_mssid_list = list(dict.fromkeys(mssid_list))
    return clean_mssid_list

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
        meetupfeed(chat_id)
    if call.data == 'get_feed':
        update(chat_id, 7)

##Updates
def update(message, daysoffset):
    print(f'{timestamp()}update start')
    url=(meetup_all)
    startdate = time.strftime('%Y-%m-%d')
    if message == 'none':
        clean_mssid_list=get_subs_list()
    else:
        clean_mssid_list=[message]
    #response=requests.get(url, headers=headers).json()
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
                    get_events_dict[i]={}
                    get_events_dict[i]['event_title']=response[i]['title']['rendered']
                    get_events_dict[i]['event_group']=response[i]['comunidad'][0]['post_title']
                    get_events_dict[i]['event_cat']=response[i]['taxonomy_info']['cat_meetup'][0]['label']
                    get_events_dict[i]['event_page_link']=response[i]['link']
                    get_events_dict[i]['event_date']=response[i]['fecha']
                    output_get_events='🟠 '+'<a href="'+get_events_dict[i]['event_page_link']+'">'+get_events_dict[i]['event_title']+ '</a> \n🔸 <b>'+ get_events_dict[i]['event_group']+ '</b> 🗓️ ' + get_events_dict[i]['event_date']
                    bot.send_message(clean_mssid_list[x], f'{output_get_events}', parse_mode='html', disable_web_page_preview=True)
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
    print(f'{timestamp()}daily update start')
    url=(meetup_all)
    startdate = time.strftime('%Y-%m-%d')
    #response=requests.get(url, headers=headers).json()
    response=make_request(url, GET)
    total_entries=len(response)
    daily_meetups_list=[]
    for i in range(total_entries):
        meetup_date=response[i]['fecha']
        if meetup_date == startdate:
            daily_meetups_list.append(i)
    if len(daily_meetups_list) == 0:
        print(f'{timestamp()}daily update sent: no events today')
        return False
    else:
        if message == 'none':
            clean_mssid_list=get_subs_list()
        else:
            clean_mssid_list=[message]
        get_events_dict={}
        for x in clean_mssid_list:
            bot.send_message(x, '⚡Hoy hay meetup!!')
            for i in range(len(daily_meetups_list)):
                #if response[0]['fecha'] == startdate:
                get_events_dict[i]={}
                get_events_dict[i]['event_title']=response[daily_meetups_list[i]]['title']['rendered']
                get_events_dict[i]['event_group']=response[daily_meetups_list[i]]['comunidad'][0]['post_title']
                get_events_dict[i]['event_cat']=response[daily_meetups_list[i]]['taxonomy_info']['cat_meetup'][0]['label']
                get_events_dict[i]['event_page_link']=response[daily_meetups_list[i]]['link']
                get_events_dict[i]['event_date']=response[daily_meetups_list[i]]['fecha']
                output_get_events='🟠 '+'<a href="'+get_events_dict[i]['event_page_link']+'">'+get_events_dict[i]['event_title']+ '</a> \n🔸 <b>'+ get_events_dict[i]['event_group']+ '</b> 🗓️ ' + get_events_dict[i]['event_date']
                try:
                    bot.send_message(x, f'{output_get_events}', parse_mode='html', disable_web_page_preview=True)
                except:
                    pass        
        print(f'{timestamp()}daily update sent')
        return True

def new_comm():
    url=(community_all)
    #header=requests.head(url)
    #response=requests.get(url).json()
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
            for x in get_subs_list():
                try:
                    bot.send_message(x, output_com)
                except:
                    pass
        time.sleep(3600*12)

def new_meetup():
    url=(meetup_all)
    #header=requests.head(url)
    #response=requests.get(url).json()
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
            print(f'{timestamp()}New meet: {title}, {link}')
            total_meet == total_meet_u
            for x in get_subs_list():
                try:
                    bot.send_message(x, output_meet, parse_mode='markdown')
                except:
                    pass
        time.sleep(3600*6)

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

    thread_com_u= threading.Thread(name='thread_com_u', target=new_comm)
    thread_com_u.start()

    thread_meet_u= threading.Thread(name='thread_meet_u', target=new_meetup)
    thread_meet_u.start()