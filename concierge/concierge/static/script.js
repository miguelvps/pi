// remove page caching
// $('.ui-page').live('pagehide', function(){ $(this).remove(); });
$('.page-map').live('pagehide', function(){ $(this).each(function(){$(this).remove();}); });
$('#favorites').live('pagehide', function(){ $(this).remove(); });
$('#ratings').live('pagehide', function(){ $(this).remove(); });
$('#history').live('pagehide', function(){ $(this).remove(); });
//$('#custom_search').live('pagehide', function(){ $(this).remove(); });

// notifications
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
