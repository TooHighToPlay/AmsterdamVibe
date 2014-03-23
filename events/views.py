from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext

import facebook
import requests


def home(request):
    return render_to_response('home.html', context_instance=RequestContext(request))


DUMMY_EVENT = {
    'id': 1,
    'name': 'Klonckenstein',
    'description': "Op de dinsdagavonden in Sugarfactory organiseert KISS een soulvolle dansavond genaamd Klonckenstein"
                   " voor de ware muziekliefhebbers. House, boogie en disco grooves uit New York, Chicago en Detroit "
                   "vormen basis voor deze nieuwe doordeweekse clubavond. Amsterdamse deejays en producers als Dim "
                   "Browski, Olivier Boogie, J.A.N., Marcel Vogel en Mr. Gibbs, Uncle Clyde, Th'Acquisition, Special "
                   "Mike, Black Grapes (Bird) zullen deze dynamische dans- en muziekcultuur in een wekelijkse avond "
                   "terug brengen naar de club, onder de noemer Klonckenstein aka House of Klonck!",
    'date': 'Tuesday 18 March',
    'time': '23:30',
    'img_url': 'http://partyflock.nl/images/party/265544_original_325779.jpg',
    'genres': [
        'disco',
        'funk',
        'groove',
        'house',
    ],
    'artists': [
        'Guessbeats',
        'Kidmalone',
    ],
    'price': '3 EUR',
    'people_going': 74,
    'venue': {
        'name': 'Sugarfactory',
        'url': 'http://www.sugarfactory.nl',
        'address': 'Lijnbaansgracht 238 Amsterdam',
        'lat': 52.36479810916446,
        'lng': 4.881749153137207,
    },
}


def list(request):
    # we should query the local datastore via sparql here and get
    # the events
    top_events = [DUMMY_EVENT for i in range(7)]

    suggested_events = None
    if request.user.is_authenticated():
        suggested_events = top_events[:3]

    return render_to_response('list.html', {
            'top_events': top_events,
            'suggested_events': suggested_events
        }, context_instance=RequestContext(request))


def details(request, id):
    # we should query the local datastore via sparql here to
    # get the details for this event

    return render_to_response('details.html', {'event': DUMMY_EVENT}, context_instance=RequestContext(request))


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

    # TODO: save into RDF store

    return redirect(reverse('event_list'))
