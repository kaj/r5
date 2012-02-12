from django.conf import settings
from datetime import datetime
import pymongo

class DMAnalyticsMiddleware(object):
    """
    Collect data to analyze.
    """

    def __init__(self):
        self.mongo = pymongo.Connection()
        self.db = self.mongo.dmanalytics
        self.log = self.db.log
    
    def process_request(self, request):
        request.dma_starttime = datetime.now()
        item = {
            'method': request.method,
            'host': request.get_host(),
            'path': request.path,
            'is_ajax': request.is_ajax(),
            'cookies': request.COOKIES,
            'remote_addr': request.META['REMOTE_ADDR'],
            'time': request.dma_starttime,
            }
        
        if 'HTTP_USER_AGENT' in request.META:
            item['user_agent'] = request.META['HTTP_USER_AGENT']
        if 'HTTP_REFERER' in request.META:
            item['referer'] = request.META['HTTP_REFERER']
        
        if request.GET:
            item['query'] = request.GET
        
        request.dma_id = self.log.insert(item)
        #print "Request starting:", item

    def process_response(self, request, response):
        item = {
            'response': {
                'status_code': response.status_code,
                'content_type': response.get('Content-Type', None),
                'content_length': response.get('Content-Length', None),
                },
            'elapsed': (datetime.now() - request.dma_starttime).total_seconds(),
            'user': unicode(getattr(request, 'user', u'Anonymous')),
            }
        #if request.user.is_authenticated():
        #    item['user'] = request.user.username

        self.log.update({'_id': request.dma_id},
                        {'$set': item})
        #print "Done:", item
        return response
