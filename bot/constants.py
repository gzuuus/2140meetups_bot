# BOT Font
font_name='Gogh-ExtraBold.ttf'

# URLs
community_50="https://2140meetups.com/wp-json/wp/v2/community?per_page=50"
community_100="https://2140meetups.com/wp-json/wp/v2/meetup?per_page=100"
community_all="https://2140meetups.com/wp-json/wp/v2/community"
meetup_3="https://2140meetups.com/wp-json/wp/v2/meetup?per_page=3"
meetup_all="https://2140meetups.com/wp-json/wp/v2/meetup"
default_banner="https://2140meetups.com/wp-content/uploads/2022/10/default_banner.png"

# Messages
hi_msg = '<u><b>Bienvenido al bot de 2140meetups</b></u>\n<a href="https://2140meetups.com/guia/">Guia para creacion de meetups</a>\n\nEste es un bot diseñado para ayudar a las comunidades a participar en la iniciativa de 2140meetups \n\nFunciones del bot:\n🖼️/createbadge Crea un badge/foto de tu comunidad \n🔍/get_meetups Recibe publicaciones para los 3 proximos meetus o filtra por comunidad\n📰/feed Suscribete al feed para recibir actualizaciones regulares de los eventos publicados en la web\n🤠/get_feed No puedes esperar a que llegue la hora del feed? usa este comando para recibir el feed cuando quieras\n\n🟠Have fun and spread bitcoin!\n<a href="https://getalby.com/p/2140meetups">⚡2140meetups@getalby.com</a>'
feed_msg= '<b>Feed info:</b>\n<u>Notificaciones:</u> \n🔸Meetups hoy, cada día comprueba si hay un meetup pasando ese mismo día y te lo muestra \n🔸Cada lunes y jueves meetups para los próximos 7 días\n🔸Cada 6h comprueba si se han añadido nuevos meetups\n🔸Cada 12h comprueba si se han añadido nuevas comunidades \n\n💡Si quieres cancelar tu suscripción solo haz /feed y pulsa el botón "Cancelar suscripción" \n\n<i>Si tienes alguna sugerencia o comentario hay un canal para esto <a href="https://t.me/meetups_bot_discussion"> 2140meetups bot discussion </a></i>'


# Events
event_cat_list=['📢General', '💬Socrático', '👾Dev']
event_data={}

# Words
outm_name='\n\n💡Evento: '
outm_group='\n👥Grupo: '
outm_description='\n\n📝Descripción: '
outm_cat='\n\n🟠Categoría: '
outm_type='\n🟢Tipo: '
outm_location='\n📍Localización: '
outm_location_link='\n🔗Link: '
outm_date='\n\n🗓️Fecha: '
outm_hour='\n🕓Hora: '

# EXAMPLES
lorem='Lorem ipsum dolor sit amet, consectetur adipiscing elit. Duis leo nibh, accumsan ut dapibus tempus, ultricies eu turpis. Proin vitae massa eu tellus sodales mollis. Maecenas neque neque, tincidunt eget nunc nec, dapibus fringilla neque. '
msg_ids=[]
m_separators="\n\n---\n\n"

# COMMANDS
start="/start"
start_msg="Inicia el bot"
meetups="/get_meetups"
meetups_msg="Muestra los proximos meetups"
feed="/feed"
feed_msg="Activa/desactiva el Feed para recibir actualizaciones de los meetups"
get_feed="/get_feed"
get_feed_msg="Muestra el feed"

# Environment file variables
BOT_TOKEN='BOT_TOKEN'
ENV='ENV'
DB_DIR='DB_DIR'
SUBS_DB_PATH='SUBS_DB_PATH'
# Environment types
DEV='dev'
STAGING='staging'
PROD='prod'

# DEPRECATED
badge="/createbadge"
badge_msg="Crea un nuevo badge/insignia"
color_list=['Blanco⬜', 'Negro⬛','Morado🟪', 'Rosa 🟣', 'Amarillo🟡', 'Verde 🟢', 'Azul🔵']