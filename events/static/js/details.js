L.Icon.Default.imagePath = window.location.origin + '/static/images';

var lat = $('#map').data('lat');
var lng = $('#map').data('lng');

var map = L.map('map', {
    center: [lat, lng],
    zoom: 16
});
L.tileLayer.provider('OpenStreetMap.Mapnik').addTo(map);

L.marker([lat, lng])
    .addTo(map);
