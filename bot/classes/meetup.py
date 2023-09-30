from constants import *

class Meetup:
    # constructor function    
    def __init__(self, event):
        self.title=event['title']['rendered']
        self.group=event['comunidad'][0]['post_title']
        self.category=event['taxonomy_info']['cat_meetup'][0]['label']
        self.date=event['fecha']
        self.hour=event['hora']
        self.location=event['direccion']
        self.link=event['link']
        # Check if the meetup has a cover image
        if event['featured_image_src_large']:
            self.image=event['featured_image_src_large'][0]
        else: 
            self.image=default_banner


    # Format the meetup to display in the client
    def format(self):
        return f"""
        {outm_name} {self.title} \
        {outm_group} {self.group} 
        {outm_cat} {self.category} \
        {outm_location} {self.location}
        {outm_date} {self.date} \
        {outm_hour} {self.hour}
        {outm_location_link} {self.link}
        """

    def format_mini(self):
        return f"""
        🟠 <a href="{self.link}">{self.title}</a> \n🔸 <b>{self.group}</b> 🗓️ {self.date}
        """

    def format_new(self):
        # \ character does not interpret line break, thats why we add after that \n
        return f"""
        \n🟠 <b>Nuevo meetup:</b> {self.title} \
        \n📍 <b>Comunidad:</b> {self.group} \
        \n💡 <b>Category:</b> {self.category} \
        \n🗓️ <b>Fecha:</b> {self.category} \
        \n\n🔗 <a href="{self.link}">More info</a>
        """