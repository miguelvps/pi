$('div').live('pageshow', function(event, ui) {
    $(".notification").slideDown(750);
});

$('div').live('pagecreate', function(event, ui) {
    $('.notification').click(function() {
        $(this).slideToggle(750);
    });
});

$('div').live('pagehide', function(event, ui) {
        $('.notifications', this).empty();
});