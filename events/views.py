import datetime
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from getInfoScripts import integrate, soundcloud_get_tracks

from getInfoScripts.sesame_repository import getFutureEvents, getEventInfoForId, getUserSuggestedEvents

import facebook
import requests
import sparql

from django.core.cache import cache

def cache_per_user(ttl=None, prefix=None, cache_post=False):
    def decorator(function):
        def apply_cache(request, *args, **kwargs):
            if request.user.is_anonymous():
                user = 'anonymous'
            else:
                user = request.user.id

            if prefix:
                CACHE_KEY = '%s_%s'%(prefix, user)
            else:
                CACHE_KEY = 'view_cache_%s_%s'%(function.__name__, user)       

            if not cache_post and request.method == 'POST':
                can_cache = False
            else:
                can_cache = True

            if can_cache:
                response = cache.get(CACHE_KEY, None)
            else:
                response = None
                
            if not response:
                response = function(request, *args, **kwargs)
                if can_cache:
                    cache.set(CACHE_KEY, response, ttl)
            return response
        return apply_cache
    return decorator

def home(request):
    return redirect(reverse('event_list'))


def parse_rdf_event(event):
    try:
        dt = datetime.datetime.strptime(event['date'],'%Y-%m-%dT%H:%M:%S')
        time = dt.strftime('%H:%M')
        date = dt.strftime('%d %B %Y')
        event['time'] = time
        event['date'] = date
    except:
        event['time'] = ''
        event['date'] = ''

    event['image_url'] = event['image_url'].replace('\\', '')

    if 'artists' in event:
        for i in range(len(event['artists'])):
            artist = event['artists'][i]
            artist['sample_html'] = soundcloud_get_tracks.getEmbedHtml(artist['soundcloud_track_ids'][0])

    return event


@cache_per_user()
def list(request):
    # we should query the local datastore via sparql here and get
    # the events
    top_events = [parse_rdf_event(e) for e in getFutureEvents('vibe', limit=50)]

    suggested_events = None
    if request.user.is_authenticated() and request.user.socialaccount_set.all():
        suggested_events = getUserSuggestedEvents('vibe', request.user.socialaccount_set.all()[0].extra_data['id'])
        suggested_events = [parse_rdf_event(e) for e in suggested_events[:9]]

    return render_to_response('list.html', {
            'top_events': top_events,
            'suggested_events': suggested_events
        }, context_instance=RequestContext(request))


def details(request, id):
    # we should query the local datastore via sparql here to
    # get the details for this event
    event = getEventInfoForId('vibe', id)
    event = parse_rdf_event(event)

    return render_to_response('details.html', {'event': event}, context_instance=RequestContext(request))


def import_fb_data(request):
    def get_all_data(url):
        data = []
        response = g.get_object(url)
        data.extend(response['data'])

        while 'paging' in response and 'next' in response['paging']:
            response = requests.get(response['paging']['next']).json()
            data.extend(response['data'])

        return data

    TOKEN = request.user.socialaccount_set.all()[0].socialtoken_set.all()[0].token
    g = facebook.GraphAPI(TOKEN)

    events = get_all_data('/me/events')
    likes = get_all_data('/me/likes')
    artists = [l for l in likes if l['category'] == 'Musician/band']
    genres = [l for l in likes if l['category'] == 'Musical genre']

    integrate.gatherAndExportUserData('vibe', request.user.socialaccount_set.all()[0].extra_data['id'], TOKEN)

    return redirect(reverse('event_list'))


def sparql_query(query, endpoint):
    """
    Runs the given (string) query against the given endpoint,
    returns a list of dicts with the variables' values.
    """
    result = sparql.query(endpoint, query)

    data = []
    for row in result:
        values = sparql.unpack_row(row)
        d = {}
        for i, v in enumerate(values):
            d[result.variables[i]] = v
        data.append(d)

    return data

