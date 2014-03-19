from django.shortcuts import render_to_response

# Create your views here.
def home(request):
    return render_to_response('home.html')


def list(request):
    dummy_event = {
        'name': 'Klonckenstein',
        'date': 'Tuesday 18 March',
        'time': '23:30',
        'img_url': 'http://partyflock.nl/images/party/265544_original_325779.jpg',
        'genres': [
            'disco',
            'funk',
            'groove',
            'house',
        ],
        'venue': {
            'name': 'Sugarfactory',
            'url': 'http://www.sugarfactory.nl',
            'address': 'Lijnbaansgracht 238 Amsterdam'
        },
    }
    events = [dummy_event for i in range(7)]

    return render_to_response('list.html', {'events': events})
