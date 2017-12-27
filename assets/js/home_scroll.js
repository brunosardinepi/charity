$(document).on('scroll', window, function() {
    if ($(window).scrollTop() > 507) {
        $('#nav-container').addClass('fixed-nav');
    }
    if ($(window).scrollTop() < 507) {
        $('#nav-container').removeClass('fixed-nav');
    }
});
