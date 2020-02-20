import requests
import json
import wget

HEADERS = {'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.79 Safari/537.36'}

class Scraper(object):
    def __init__(self, params,):
        self.params = params
        self.chunks = []
        self.scraperSession = requests.Session()
        self.scraperSession.headers = HEADERS
        self.frames = []

    def scrape(self):
        # Bring down content
        # Save the next continuation
        # return true or false
        pass

    def __getitem__(self, key):
        if isinstance(key, slice):
            start = key.start or 0
            stop = key.stop or len(self)
            step = key.step or 1

            if step < 0:
                start = key.start or len(self) - 1
                stop = key.stop or 0
            
            items = []
            for i in range(start, stop, step):
                item = self[i]
                if item:
                    items.append(item)
                else:
                    break
            
            return items
        else:
            try:
                return self.frames[key]
            except IndexError:
                if self.scrape():
                    return self[key]
                else:
                    return None
                

    def __len__(self):
        return len(self.frames)

class Chunk(object):
    def __init__(self, recipe, size=0):
        self.recipe = recipe
        self.size = size

class Frame(object):
    def __init__(self, params):
        self.__rawParams = params

    @property
    def video(self):
        return self.__rawParams.get('video', None)
    @property
    def image(self):
        return self.__rawParams.get('image', None)
    @property
    def text(self):
        return self.__rawParams.get('text', None)
    @property
    def additionalText(self):
        return self.__rawParams.get('additionalText', None)
    @property
    def positiveMetric(self):
        return self.__rawParams.get('positiveMetric', None)
    @property
    def negativeMetric(self):
        return self.__rawParams.get('negativeMetric', None)
    @property
    def interactionMetric(self):
        return self.__rawParams.get('interactionMetric', None)
    @property
    def reference(self):
        return self.__rawParams.get('reference', None)

    def toJson(self):
        return json.dumps(self.__rawParams)

    def save(self, aspect, path = None):
        if aspect in ['video', 'image']:
            if path == None:
                wget.download(self.__rawParams[aspect])
            else:
                wget.download(self.__rawParams[aspect], path)
        else:
            path = path or 'default'
            with open(path, 'w') as f:
                f.write(self.__rawParams[aspect])