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

    # Another constructor of meetup but in that case we do not need all info of the meetup
    # Meetup short resume without cover
    def __init__(self, mini):
        self.title=mini['title']['rendered']
        self.group=mini['comunidad'][0]['post_title']
        self.category=mini['taxonomy_info']['cat_meetup'][0]['label']
        self.link=mini['link']
        self.date=mini['fecha']


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