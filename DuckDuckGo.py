from . import ScraperLib
import json
from .getFromPath import safeGet
import re

VQD_REGEX = re.compile("vqd='([0-9\-]+)'")

class DuckDuckGo(ScraperLib.Scraper):
    def __init__(self, params):
        super().__init__(params)

        self.query = params['query']
        if params['filter']:
            self.filter = '1'
        else:
            self.filter = '-1'

        page = self.scraperSession.get('https://duckduckgo.com/?q=' + '+'.join(self.query.split(' ')) + '&t=h_&iar=images&iaf=size%3ALarge&iax=images&ia=images').content.decode('utf-8')
        self.vqd = re.search(VQD_REGEX, page).group(1)
        self.chunks.append(ScraperLib.Chunk('i.js?l=us-en&o=json&q=' + '+'.join(self.query.split(' ')) + '&vqd=' + self.vqd + '&f=size:Wallpaper,,,&p=' + self.filter + '&v7exp=a'))
        
        self.scrape()

    def scrape(self):
        if not(self.canScrape):
            return False

        try:
            response = json.loads(self.scraperSession.get('https://duckduckgo.com/' + self.chunks[-1].recipe + '&vqd=' + self.vqd).content)

            self.chunks[-1].size = len(response['results'])

            self.chunks.append(ScraperLib.Chunk(response['next']))
            
            for result in response['results']:
                if (result['image'].endswith('.gif') or result['image'].endswith('.gifv')):
                    self.frames.append(ScraperLib.Frame({
                        'video': result['image'],
                        'text': result['title'],
                        'reference': result['url']
                    }))
                else:
                    self.frames.append(ScraperLib.Frame({
                        'image': result['image'],
                        'text': result['title'],
                        'reference': result['url']
                    }))

            return True
        except Exception as e:
            print(e)
            return False
