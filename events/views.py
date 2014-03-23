from django.shortcuts import render_to_response
from django.template import RequestContext


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
    events = [DUMMY_EVENT for i in range(7)]

    return render_to_response('list.html', {'events': events}, context_instance=RequestContext(request))


def details(request, id):
    # we should query the local datastore via sparql here to
    # get the details for this event

    return render_to_response('details.html', {'event': DUMMY_EVENT}, context_instance=RequestContext(request))
