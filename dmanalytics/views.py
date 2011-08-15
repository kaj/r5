from django.views.generic.simple import direct_to_template
from bson.code import Code
from math import log, exp
import pymongo


def get_ranges(lo, hi, n=10):
    llo = log(lo)
    lhi = log(hi)
    interval = (lhi - llo) / n
    limits = [exp(llo + interval * x) for x in range(0, n+1)]
    return [(limits[i], limits[i+1]) for i in range(0, n)]

def index(request):
    def mapfunction(attr):
        src = ("function() {"
               "  key=this.%s;"
               "  emit(key, {count: 1});"
               "}" % attr)
        return Code(src)
    
    mongo = pymongo.Connection()
    db = mongo.dmanalytics
    log = db.log

    reduce = Code("function (key, values) {"
                  "  var sum = 0;"
                  "  values.forEach(function (value) {sum += value.count;});"
                  "  return {count: sum};"
                  "}")
    
    def bysomething(attr, name=None, limit=10):
        return {
            'name': name or attr,
            'values': [ {'value': x['_id'],
                         'count': x['value']['count']}
                        for x
                        in log.map_reduce(mapfunction(attr), reduce,
                                          'by_%s' % attr,
                                          query={attr: {'$exists': True}}) \
                            .find() \
                            .sort('value.count', pymongo.DESCENDING) \
                            .limit(limit)
                        ]
            }

    def by_ua_part(attr, name=None):
        m = Code("function() {"
                 "  b = db.known_uas.findOne({_id: this._id});"
                 "  b = b || {%s: 'unknown'};"
                 "  emit(b.%s, {count: this.value.count});"
                 "}" % (attr, attr))
        return { 'name': attr or name,
                 'values': [ {'value': x['_id'],
                              'count': x['value']['count']}
                             for x
                             in db.by_user_agent.map_reduce(m, reduce,
                                                            'by_browser') \
                                 .find() \
                                 .sort('value.count', pymongo.DESCENDING)
                             ]
                 }
    
    def by_elapsed_time():
        with_elapsed = subquery({'elapsed': {'$exists': True}})
        lowest = log.find(with_elapsed, {'_id': 0, 'elapsed': 1}) \
            .sort('elapsed', pymongo.ASCENDING).limit(1)[0]['elapsed']
        highest = log.find(with_elapsed, {'_id': 0, 'elapsed': 1})\
            .sort('elapsed', pymongo.DESCENDING).limit(1)[0]['elapsed']
       
        def query(lo, hi):
            q = {'elapsed':
                        {'$gt': lo,
                         '$lte': hi}}
            q.update(basequery)
            print basequery
            print q
            return q
        
        return { 'name': 'Elapsed seconds',
                 'values': [ { 'value': '%f - %f' % (lo, hi),
                               'count': db.log.find(query(lo, hi)).count()
                               }
                             for (lo, hi)
                             in get_ranges(0.999*lowest, 1.001*highest, n=7) ]
                 }
    
    return direct_to_template(request, 'dma/index.html', {
            'results': [ bysomething('path'),
                         bysomething('remote_addr'),
                         bysomething('referer'),
                         bysomething('response.status_code', 'status code'),
                         bysomething('response.content_type', 'content type'),
                         bysomething('method'),
                         bysomething('user'),
                         bysomething('user_agent'),
                         by_ua_part('browser'),
                         by_ua_part('os'),
                         by_elapsed_time(),
                         ],
            })
