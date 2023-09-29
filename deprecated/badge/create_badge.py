# Create a badge with custom colors
@bot.message_handler(commands=['createbadge'])
def newreg(message):
    markup= ForceReply()
    msg = bot.send_message(message.chat.id, '👥Escribe el nombre del comunidad', reply_markup=markup)
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
        image_bg=color_list.index(message.text)
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
    os.remove(outphoto.name)
    print(f'{timestamp()}new badge created: {handle}')