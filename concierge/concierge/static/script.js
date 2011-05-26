$('div').live('pageshow',function(event, ui){
    $(".notification").slideDown(750);
    $('.notification').click(function() {
        $(this).slideToggle(750);
    });
});
