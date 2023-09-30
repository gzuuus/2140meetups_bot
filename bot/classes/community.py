class Community:
    # constructor function    
    def __init__(self, community):
        self.title=community['title']['rendered']
        self.city=community['ciudad']
        self.country=community['pais']
        self.link=community['link']

    def format(self):
        return f"""
        🟠 Nueva comunidad: {title}\n📍Ciudad: {city}, Pais: {country}\n🔗Link: {link}
        """