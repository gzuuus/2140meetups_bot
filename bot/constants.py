# Environment file variables
BOT_TOKEN='BOT_TOKEN'
ENV='ENV'
DB_DIR='DB_DIR'
SUBS_DB_PATH='SUBS_DB_PATH'
# Environment types
DEV='dev'
STAGING='staging'
PROD='prod'

# BOT Font
font_name='Gogh-ExtraBold.ttf'

# URLs
community_50="https://2140meetups.com/wp-json/wp/v2/community?per_page=50&orderby=title&order=asc"
community_all="https://2140meetups.com/wp-json/wp/v2/community?orderby=title&order=asc"
community_pagination="https://2140meetups.com/wp-json/wp/v2/community?page=%s&per_page=50&orderby=title&order=asc"
meetup_100="https://2140meetups.com/wp-json/wp/v2/meetup?per_page=100"
meetup_5="https://2140meetups.com/wp-json/wp/v2/meetup?per_page=5"
meetup_all="https://2140meetups.com/wp-json/wp/v2/meetup"
default_banner="https://2140meetups.com/wp-content/uploads/2022/10/default_banner.png"
# %s: date format -> 2023-10-10
day_meetups="https://2140meetups.com/wp-json/wp/v2/meetup?day=%s"
timeframe_meetups="https://2140meetups.com/wp-json/wp/v2/meetup?from=%s&to=%s"
# %s: community_id
community_meetups="https://2140meetups.com/wp-json/wp/v2/meetup?community=%s"

# Messages
hi_msg = '<u><b>Bienvenido al bot de 2140meetups</b></u>\n<a href="https://2140meetups.com/guia/">Guia para creacion de meetups</a>\n\nEste es un bot diseñado para ayudar a las comunidades a participar en la iniciativa de 2140meetups \n\n<b>Funciones del bot:</b>\n\n🔍 /get_meetups Recibe publicaciones para los 3 proximos meetus o filtra por comunidad\n📰 /feed Suscribete al feed para recibir actualizaciones regulares de los eventos publicados en la web\n🤠 /get_feed No puedes esperar a que llegue la hora del feed? usa este comando para recibir el feed cuando quieras\n\n🟠 Have fun and spread bitcoin!\n<a href="https://getalby.com/p/2140meetups">⚡ 2140meetups@getalby.com</a>'
feed_msg= '<b>Feed info:</b>\n<u>Notificaciones:</u> \n🔸Meetups hoy, cada día comprueba si hay un meetup pasando ese mismo día y te lo muestra \n🔸Cada lunes y jueves meetups para los próximos 7 días\n🔸Cada 6h comprueba si se han añadido nuevos meetups\n🔸Cada 12h comprueba si se han añadido nuevas comunidades \n\n💡Si quieres cancelar tu suscripción solo haz /feed y pulsa el botón "Cancelar suscripción" \n\n<i>Si tienes alguna sugerencia o comentario hay un canal para esto <a href="https://t.me/meetups_bot_discussion"> 2140meetups bot discussion </a></i>'
feed_subscription_msg='✅Te has suscrito al feed, ahora recibirás notificaciones sobre los meetups de 2140meetups.com'

# Events
event_cat_list=['📢General', '💬Socrático', '👾Dev']
event_data={}

# Words
outm_name='\n\n💡 Evento: '
outm_group='\n👥 Grupo: '
outm_cat='\n🟠 Categoría: '
outm_location='\n📍Localización: '
outm_date='\n🗓️ Fecha: '
outm_hour='\n🕓 Hora: '
outm_location_link='\n🔗 Mas info: '
outm_description='\n\n📝Descripción: '
outm_type='\n🟢Tipo: '

# Buttons
COMMUNITIES='Ver meetups por comunidad'
NEXT_MEETUPS='Próximos 5 meetups'
CANCEL_SUBSCRIPTION='Cancelar suscripcion'
ALREADY_SUBSCRIBED='Ya estas suscrito'
ALL_FEED='Mostrar feed completo'

# COMMANDS
start="/start"
start_msg="Inicia el bot"
meetups="/get_meetups"
meetups_msg="Muestra los próximos 5 meetups o muestra los meetups de una comunidad"
feed="/feed"
feed_msg="Activa/desactiva el Feed para recibir actualizaciones de los meetups"
get_feed="/get_feed"
get_feed_msg="Muestra el feed"

# TIMEFRAMES
ONE_HOUR=3600*6
TWO_HOURS=3600*12
DAYLY_UPDATE_TIME="10:40"
WEEKLY_UPDATE_TIME="10:00"
WEEK=7

# EXAMPLES
lorem='Lorem ipsum dolor sit amet, consectetur adipiscing elit. Duis leo nibh, accumsan ut dapibus tempus, ultricies eu turpis. Proin vitae massa eu tellus sodales mollis. Maecenas neque neque, tincidunt eget nunc nec, dapibus fringilla neque. '
msg_ids=[]
m_separators="\n\n---\n\n"