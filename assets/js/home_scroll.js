$(document).on('scroll', window, function() {
    if ($(window).scrollTop() > 507) {
        $('#nav-container').addClass('fixed-nav navbar navbar-expand-lg');
        $('.navbar-brand').show();
        if (!$(".navbar-toggler").length) {
            $('.navbar-brand').after('<button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarNavAltMarkup" aria-controls="navbarNavAltMarkup" aria-expanded="false" aria-label="Toggle navigation"><i class="far fa-bars"></i></button>');
        }
        $('#navbarNavAltMarkup').removeClass('col text-center');
        $('#navbarNavAltMarkup').addClass('collapse navbar-collapse');
        $('#nav-ul').removeClass('list-inline');
        $('#nav-ul').addClass('navbar-nav ml-auto');
        $('#create').removeClass('list-inline-item');
        $('#create').addClass('nav-item');
        $('#search').removeClass('list-inline-item');
        $('#search').addClass('nav-item');
        $('#login').removeClass('list-inline-item');
        $('#login').addClass('nav-item mb-2');
        $('#signup').removeClass('list-inline-item');
        $('#signup').addClass('nav-item');
        $('#logout').removeClass('list-inline-item');
        $('#logout').addClass('nav-item');
        $('#profile').removeClass('list-inline-item');
        $('#profile').addClass('nav-item');
    }
    if ($(window).scrollTop() < 507) {
        $('#nav-container').removeClass('fixed-nav navbar navbar-expand-lg');
        $('.navbar-brand').hide();
        if ($(".navbar-toggler").length) {
            $('.navbar-toggler').remove();
        }
        $('#navbarNavAltMarkup').removeClass('collapse navbar-collapse');
        $('#navbarNavAltMarkup').addClass('col text-center');
        $('#nav-ul').removeClass('navbar-nav ml-auto');
        $('#nav-ul').addClass('list-inline');
        $('#create').removeClass('nav-item');
        $('#create').addClass('list-inline-item');
        $('#search').removeClass('nav-item');
        $('#search').addClass('list-inline-item');
        $('#login').removeClass('nav-item');
        $('#login').addClass('list-inline-item');
        $('#signup').removeClass('nav-item');
        $('#signup').addClass('list-inline-item');
        $('#logout').removeClass('nav-item');
        $('#logout').addClass('list-inline-item');
        $('#profile').removeClass('nav-item');
        $('#profile').addClass('list-inline-item');
    }
});
