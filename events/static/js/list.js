$('.event-card').on('click', function (e) {
    var url = $(e.delegateTarget).data('details-url');
    window.location = url;
});
