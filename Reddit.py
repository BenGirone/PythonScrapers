from .import ScraperLib
import json
from .getFromPath import safeGet

class Reddit(ScraperLib.Scraper):
    def __init__(self, params):
        super().__init__(params)
        self.query = params['query']
        self.shouldGetTextAndComments = safeGet(params, 'shouldGetTextAndComments', False)
        self.chunks.append(ScraperLib.Chunk(''))
        self.scrape()

    def scrape(self):
        if not(self.canScrape):
            return False

        try:
            response = self.scraperSession.get('https://reddit.com/' + self.query + '.json?after=' + self.chunks[-1].recipe)
            responseJson = json.loads(response.content)

            self.chunks[-1].size = len(responseJson['data']['children'])

            self.chunks.append(ScraperLib.Chunk(responseJson['data']['after']))

            if not(responseJson['data']['after']):
                self.canScrape = False

            for child in responseJson['data']['children']:
                self.frames.append(self.makeFrame(child['data']))

            return True
        except Exception as e:
            return False
    
    def makeFrame(self, data):
        params = {
            'text': safeGet(data, 'title', ''),
            'reference': 'https://reddit.com' + safeGet(data, 'permalink', ''),
            'positiveMetric': safeGet(data, 'ups', None),
            'negativeMetric': safeGet(data, 'downs', None),
            'interactionMetric': safeGet(data, 'num_comments', None) 
        }

        if safeGet(data, 'is_video', False):
            params['video'] = safeGet(data, 'media.reddit_video.fallback_url', None)
        elif 'gfycat.com' in safeGet(data, 'url', ''):
            gfycatURL = data['url'].replace('gfycat.com', 'api.gfycat.com/v1/gfycats')
            params['video'] = safeGet(json.loads(self.scraperSession.get(gfycatURL).content), 'gfyItem.mp4Url', None)
        elif safeGet(data, 'url', '').split('.')[-1] in ['gif', 'gifv']:
            params['video'] = data['url']
        elif safeGet(data, 'url', '').split('.')[-1] in ['jpg', 'png', 'bmp', 'jpeg']:
            params['image'] = data['url']

        if self.shouldGetTextAndComments:
            params['additionalText'] = self.getTextAndComments(data['permalink'])

        return ScraperLib.Frame(params)

    def getTextAndComments(self, postUrl):
        post = json.loads(self.scraperSession.get('https://reddit.com' + postUrl + '.json').content)
        
        textAndComments = {
            'text': safeGet(post, '[0].data.children.[0].data.selftext', '')
        }

        commentsJson = safeGet(post, '[1]', False)
        if commentsJson:
            comments = self.cleanComments(commentsJson)
            textAndComments['comments'] = comments
        
        return json.dumps(textAndComments)

    def cleanComments(self, comments):
        if comments:
            return [{'author': safeGet(comment, 'data.author'), 'text': safeGet(comment, 'data.body', ''), 'replies': self.cleanComments(safeGet(comment, 'data.replies', False))} for comment in safeGet(comments, 'data.children', [])]
        
        return []