$('.event-card').on('click', function (e) {
    var url = $(e.delegateTarget).data('details-url');
    window.location = url;
});


var width = 300;
var gutter = 50;

$('#suggested').masonry({
    columnWidth: width,
    itemSelector: '#suggested article',
    isFitWidth: true,
    gutter: gutter
});

$('#top').masonry({
    columnWidth: width,
    itemSelector: '#top article',
    isFitWidth: true,
    gutter: gutter
});
