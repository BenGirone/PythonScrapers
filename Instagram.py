from . import ScraperLib
import json
from .getFromPath import safeGet
import re
from time import sleep
from copy import deepcopy

PROFILE_REGEX = re.compile('profilePage_([0-9]+)')

class Instagram(ScraperLib.Scraper):
    def __init__(self, params):
        super().__init__(params)
        self.query = safeGet(params, 'query', False)
        self.isHashTag = self.query.startswith('#')
        self.query = self.query.replace('#', '').replace('@', '')
        self.shouldGetTextAndComments = safeGet(params, 'shouldGetTextAndComments', False)
        self.chunks.append(ScraperLib.Chunk(None))
        self.canScrape = True
        self.queryUrl = 'https://www.instagram.com/graphql/query/'
        self.shortcodeHash = '2b0673e0dc4580674a88d426fe00ea90'
        
        self.scraperSession.get('https://instagram.com')
        if self.isHashTag:
            self.hash = '90cba7a4c91000cf16207e4f3bee2fa2'
            self.varType = 'tag_name'
            self.page_info_path = 'data.hashtag.edge_hashtag_to_media.page_info'
            self.edgePath = 'data.hashtag.edge_hashtag_to_media.edges'
            self.var = self.query
        else:
            self.hash = 'e769aa130647d2354c40ea6a439bfc08'
            profile = self.scraperSession.get('https://www.instagram.com/' + self.query).content.decode('utf-8')
            self.profile_id = re.search(PROFILE_REGEX, profile).group(1)
            self.varType = 'id'
            self.page_info_path = 'data.user.edge_owner_to_timeline_media.page_info'
            self.edgePath = 'data.user.edge_owner_to_timeline_media.edges'
            self.var = self.profile_id
        
        self.scrape()

    def scrape(self):
        if not(self.canScrape):
            return False

        try:
            params = {
                'query_hash': self.hash,
            }

            if self.chunks[-1].recipe:
                params['variables'] = "{\"" + self.varType + "\":\"" + self.var + "\",\"first\":50,\"after\":\"" + self.chunks[-1].recipe + "\"}"
            else:
                params['variables'] = "{\"" + self.varType + "\":\"" + self.var + "\",\"first\":50}"

            sleep(0.1)
            response = self.scraperSession.get(self.queryUrl, params=params)
            responseJson = json.loads(response.content.decode('utf-8'))

            self.canScrape = safeGet(responseJson, self.page_info_path + '.has_next_page')

            edges = safeGet(responseJson, self.edgePath, [])

            self.chunks[-1].size = len(edges)

            for edge in edges:
                params = {
                    'text': safeGet(edge, 'node.edge_media_to_caption.edges.[0].node.text', ''),
                    'positiveMetric': safeGet(edge, 'node.edge_media_preview_like.count', None),
                    'interactionMetric': safeGet(edge, 'node.edge_media_to_comment.count', None),
                    'reference': 'https://www.instagram.com/p/' + safeGet(edge, 'node.shortcode', None)
                }

                if edge['node']['__typename'] == 'GraphVideo':
                    params['video'] = self.handleVideo(edge)
                    
                    self.chunks[-1].size += 1

                    self.frames.append(ScraperLib.Frame(params))
                elif edge['node']['__typename'] == 'GraphImage':
                    params['image'] = safeGet(edge, 'node.display_url', None)

                    self.chunks[-1].size += 1

                    self.frames.append(ScraperLib.Frame(params))
                elif edge['node']['__typename'] == 'GraphSidecar':
                    for sub_edge in safeGet(edge, 'node.edge_sidecar_to_children.edges', []):
                        sub_params = deepcopy(params)

                        if sub_edge['node']['__typename'] == 'GraphVideo':
                            sub_params['video'] = safeGet(sub_edge, 'node.video_url', None)
                        elif edge['node']['__typename'] == 'GraphImage':
                            sub_params['image'] = safeGet(edge, 'node.display_url', None)

                        self.chunks[-1].size += 1

                        self.frames.append(ScraperLib.Frame(sub_params))
                
            self.chunks.append(ScraperLib.Chunk(safeGet(responseJson, self.page_info_path + '.end_cursor')))

            return True
        except Exception as e:
            print(e)
            return False

    def handleVideo(self, edge):
        if (self.isHashTag):
            vidParams = {
                'query_hash': self.shortcodeHash,
                'variables': '{"shortcode": "' + safeGet(edge, 'node.shortcode', None) + '"}',
            }

            videoEdge = json.loads(self.scraperSession.get(self.queryUrl, params=vidParams).content.decode('utf-8'))
            
            return safeGet(videoEdge, 'data.shortcode_media.video_url', None)
        else:
            return safeGet(edge, 'node.video_url', None)