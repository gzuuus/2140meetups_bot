from PIL import Image, ImageDraw, ImageFont
import time, os, telebot, textwrap, threading,requests, json
from telebot.types import ReplyKeyboardMarkup, ReplyKeyboardRemove, ForceReply, InlineKeyboardMarkup, InlineKeyboardButton
from datafile_bot import *
from pilmoji import Pilmoji
import pandas as pd
bot= telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def cmd_buttons(message):
    bot.send_message(message.chat.id, f'{hi_msg}', parse_mode='html')

@bot.message_handler(commands=['createbadge'])
def newreg(message):
    markup= ForceReply()
    msg = bot.send_message(message.chat.id, '👥Escribe el nombre del grupo', reply_markup=markup)
    bot.register_next_step_handler(msg, event_select_color)
def event_select_color(message):
    markup= ReplyKeyboardMarkup(row_width=3, one_time_keyboard=True, resize_keyboard=True, input_field_placeholder='Select bg color:')
    event_data['handle']= message.text    
    for i in range(len(color_list)):
        markup.add(color_list[i])
    msg = bot.send_message(message.chat.id, 'Selecciona un color de fondo', reply_markup=markup)
    bot.register_next_step_handler(msg, create_image)
def create_image(message):
    im = Image.open(dir_res + 'frame_1.png')
    markup= ReplyKeyboardRemove()
    get_date=time.strftime('%d-%m-%Y')
    handle= event_data['handle']
    font = ImageFont.truetype(dir_res + font_name, 75)
    if message.text in color_list:
        if color_list.index(message.text)==1:
            font_color=('white')
        else:
            font_color=('black')
    else:
        image_bg=0
        font_color=('black')
    W, H = im.size
    whandle = textwrap.wrap(handle, width=10)
    image = Image.open(dir_res + f'frame_{image_bg}.png')
    draw = ImageDraw.Draw(image)
    current_h, pad = H-210, -10
    for line in whandle:
        w, h = draw.textsize(line, font=font)
        with Pilmoji(image) as pilmoji:
            pilmoji.text((int((W-w)/2), current_h), line.strip(), (font_color), font, emoji_scale_factor=0.9, emoji_position_offset=(0, 15))
            current_h += h + pad
    image.save(dir_photos_output + f'{get_date}_{handle}.png')   
    outphoto= open(dir_photos_output + f'{get_date}_{handle}.png', 'rb')    
    bot.send_photo(message.chat.id, outphoto, f'✅ Aqui tienes tu foto para {handle}', reply_markup=markup)
##Gen_publication
@bot.message_handler(commands=['gen_publication'])
def clear_msgid_list(message):
    msg_ids.clear()
    newevent(message)
def newevent(message):    
    markup= ForceReply()
    init= bot.send_message(message.chat.id,'Si quieres visualizar como quedara el output de este asistente /output_example \nSi quieres consultar la guia para crear eventos <a href="https://github.com/danielcharrua/bitcoin-2140-meetups">Pulsa aqui</a>', reply_markup=markup, parse_mode='html')
    msg = bot.send_message(message.chat.id, 'Escribe un header llamativo para tu evento', reply_markup=markup)
    msg_ids.extend([msg.message_id, msg.message_id+1,init.message_id])
    bot.register_next_step_handler(msg, event_name)

def event_name(message):
    if message.text == '/output_example':
        markup= ReplyKeyboardMarkup(row_width=1, one_time_keyboard=True, resize_keyboard=True, input_field_placeholder='Categorias sugeridas')
        markup.add("Let's goo!")
        msg = bot.send_message(message.chat.id,'Este es un ejemplo del output de este asistente:\n\n'+ '🔥🔥(Header, pon todos los emojis que creas necesario!)🔥🔥🔥'+ outm_name + '2140 meetup' + outm_group + '2140 crew' +outm_description+ f'Descripcion del evento {lorem}' +outm_cat+ 'Categoria del evento' +outm_type + 'Presencial/Online' +outm_location+ 'Cyberspace' +outm_date+ '09-01-2009' +outm_hour+ '20:00'+outm_location_link+ 'Link a mapa o web' +'\n\n',reply_markup=markup)
        bot.register_next_step_handler(msg, newevent)
        msg_ids.extend([msg.message_id, msg.message_id+1])
    else:
        markup= ForceReply()
        event_data['event_header']=message.text
        msg = bot.send_message(message.chat.id, '💡Escribe el nombre del evento', reply_markup=markup)
        bot.register_next_step_handler(msg, event_group)
        msg_ids.extend([msg.message_id, msg.message_id+1])

def event_group(message):
    markup= ForceReply()
    event_data['event_name']=message.text
    msg = bot.send_message(message.chat.id, '👥Escribe el nombre del grupo que organiza el evento', reply_markup=markup)
    bot.register_next_step_handler(msg, event_description)
    msg_ids.extend([msg.message_id, msg.message_id+1])

def event_description(message):
    markup= ForceReply()
    event_data['event_group']=message.text
    msg = bot.send_message(message.chat.id, '📝Escribe una breve descripción para tu evento', reply_markup=markup)
    bot.register_next_step_handler(msg, event_category)
    msg_ids.extend([msg.message_id, msg.message_id+1])

def event_category(message):
    markup= ReplyKeyboardMarkup(row_width=3, one_time_keyboard=True, resize_keyboard=True, input_field_placeholder='Categorías sugeridas')
    for i in range(len(event_cat_list)):
        markup.add(event_cat_list[i])
    event_data['event_description']=message.text
    msg = bot.send_message(message.chat.id, '🟠Categoría de tu evento, puedes escribir libremente tu categoría o pulsar alguna de las sugeridas', reply_markup=markup)
    bot.register_next_step_handler(msg, event_type)
    msg_ids.extend([msg.message_id, msg.message_id+1])

def event_type(message):
    markup= ReplyKeyboardMarkup(row_width=3, one_time_keyboard=True, resize_keyboard=True, input_field_placeholder='Tipos de evento')
    markup.add('👤Presencial')
    markup.add('🔛Online')
    event_data['event_cat']=message.text
    msg = bot.send_message(message.chat.id, '🟢Escoge el tipo de evento', reply_markup=markup)
    bot.register_next_step_handler(msg, event_location)
    msg_ids.extend([msg.message_id, msg.message_id+1])

def event_location(message):
    markup= ReplyKeyboardRemove()
    event_data['event_type']=message.text
    msg = bot.send_message(message.chat.id, '📍Escribe la localización de tu evento, puede ser una dirección escrita textualmente o link de mapa', reply_markup=markup)
    bot.register_next_step_handler(msg, event_location_link)
    msg_ids.extend([msg.message_id, msg.message_id+1])

def event_location_link(message):
    markup= ForceReply()
    event_data['event_location']=message.text
    msg = bot.send_message(message.chat.id, '🔗Link: Si tu evento es online, link donde se realizara, si es presencial, link de mapa o página del evento', reply_markup=markup)
    bot.register_next_step_handler(msg, event_date)
    msg_ids.extend([msg.message_id, msg.message_id+1])

def event_date(message):
    markup= ForceReply()
    event_data['event_location_link']=message.text
    msg = bot.send_message(message.chat.id, '🗓️Fecha de tu evento? Formato sugerido: dd-mm-aaaa', reply_markup=markup)
    bot.register_next_step_handler(msg, event_hour)
    msg_ids.extend([msg.message_id, msg.message_id+1])

def event_hour(message):
    markup= ForceReply()
    event_data['event_date']=message.text
    msg = bot.send_message(message.chat.id, '🕓Hora del evento?', reply_markup=markup)
    bot.register_next_step_handler(msg, event_save)
    msg_ids.extend([msg.message_id, msg.message_id+1])

def event_save(message):
    markup= ReplyKeyboardRemove()
    event_data['event_hour']=message.text
    bot.send_message(message.chat.id,'Copia y pega ese output en tu grupo de meetups', reply_markup=markup)
    bot.send_message(message.chat.id, event_data['event_header']+ outm_name + event_data['event_name'] + outm_group +event_data['event_group'] +outm_description+ event_data['event_description'] +outm_cat+ event_data['event_cat'] +outm_type + event_data['event_type'] +outm_location+ event_data['event_location'] +outm_date+ event_data['event_date'] +outm_hour+ event_data['event_hour'] +outm_location_link+ event_data['event_location_link'] +'\n\n', reply_markup=markup)    
    get_month=time.strftime('%m-%Y')
    events_output_file= (f'{dir_events_output}events-{get_month}.csv')
    event_data['date']=get_date=time.strftime('%d-%m-%Y//%H:%M')
    df= pd.DataFrame(event_data, index=[0])
    if not os.path.exists(events_output_file):
        os.makedirs(dir_events_output, exist_ok=True)
        df.to_csv(events_output_file, mode='w', index=False, encoding='utf-8')
    else:
        df.to_csv(events_output_file, mode='a+', index=False, header=False, encoding='utf-8')
    for i in msg_ids:
        bot.delete_message(message.chat.id, i)

@bot.message_handler(commands=['get_events'])
def select_group(message):
    markup= ReplyKeyboardMarkup(row_width=1, one_time_keyboard=True, resize_keyboard=True, input_field_placeholder='Select from list')
    group_list=[]
    url=(f"http://2140meetups.com/wp-json/wp/v2/group")
    response = requests.get(url).json()
    total_entries=len(response)
    for i in range(total_entries):
        group_list.append(response[i]['title']['rendered'])
    for i in range(len(group_list)):
        markup.add(group_list[i])
    msg = bot.send_message(message.chat.id, 'Grupo?', reply_markup=markup)
    bot.register_next_step_handler(msg, get_events)
def get_events (message):
    markup= ReplyKeyboardRemove()
    group_selected= message.text
    get_events_dict={}
    url=(f"http://2140meetups.com/wp-json/wp/v2/event")
    response=requests.get(url).json()
    total_entries=len(response)
    for i in range(total_entries):        
        if response[i]['grupo'][0]['post_title'] == group_selected:
            get_events_dict[i]={}
            get_events_dict[i]['event_title']=response[i]['title']['rendered']
            get_events_dict[i]['event_group']=response[i]['grupo'][0]['post_title']
            get_events_dict[i]['event_description']=response[i]['grupo'][0]['post_excerpt']
            get_events_dict[i]['event_page_link']=response[i]['link']
            get_events_dict[i]['event_date']=response[i]['fecha']
            get_events_dict[i]['event_hour']=response[i]['hora']
            get_events_dict[i]['event_location']=response[i]['direccion']
            if response[i]['featured_image_src_large']:
                get_events_dict[i]['event_feature_image']=response[i]['featured_image_src_large'][0]
            else: get_events_dict[i]['event_feature_image']='https://2140meetups.com/wp-content/uploads/2022/10/default_banner.png'
            output_get_events=outm_name + get_events_dict[i]['event_title']+ outm_group+ get_events_dict[i]['event_group']+ outm_description+get_events_dict[i]['event_description'] + outm_location + get_events_dict[i]['event_location'] + outm_date + get_events_dict[i]['event_date'] + outm_hour + get_events_dict[i]['event_hour'] + outm_location_link + get_events_dict[i]['event_page_link']            
            bot.send_photo(message.chat.id, get_events_dict[i]['event_feature_image'], output_get_events, reply_markup=markup)
##Threading polling
def polling():
    bot.infinity_polling(interval=0, timeout=20)

if __name__=='__main__':
    bot.set_my_commands([
        telebot.types.BotCommand('/start', 'Starts the bot'),
        telebot.types.BotCommand('/createbadge', 'Crea un nuevo badge/insignia'),
        telebot.types.BotCommand('/gen_publication', 'Genera una publicacion de meetup'),
        telebot.types.BotCommand('/get_events', 'Get events')
    ])
    thread_polling= threading.Thread(name='thread_polling', target=polling)    
    thread_polling.start()
    print('Started...')