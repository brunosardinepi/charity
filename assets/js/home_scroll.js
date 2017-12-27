$(document).on('scroll', window, function() {
    if ($(window).scrollTop() > 507) {
        $('#nav-container').addClass('fixed-nav navbar navbar-expand-lg');
        $('.navbar-brand').show();
        $('#navbarNavAltMarkup').removeClass('col text-center');
        $('#navbarNavAltMarkup').addClass('collapse navbar-collapse');
        $('#nav-ul').removeClass('list-inline');
        $('#nav-ul').addClass('navbar-nav ml-auto');
        $('#search').removeClass('list-inline-item');
        $('#search').addClass('nav-item');
        $('#about').removeClass('list-inline-item');
        $('#about').addClass('nav-item');
        $('#faqs').removeClass('list-inline-item');
        $('#faqs').addClass('nav-item');
        $('#login').removeClass('list-inline-item');
        $('#login').addClass('nav-item');
        $('#signup').removeClass('list-inline-item');
        $('#signup').addClass('nav-item');
    }
    if ($(window).scrollTop() < 507) {
        $('#nav-container').removeClass('fixed-nav navbar navbar-expand-lg');
        $('.navbar-brand').hide();
        $('#navbarNavAltMarkup').removeClass('collapse navbar-collapse');
        $('#navbarNavAltMarkup').addClass('col text-center');
        $('#nav-ul').removeClass('navbar-nav ml-auto');
        $('#nav-ul').addClass('list-inline');
        $('#search').removeClass('nav-item');
        $('#search').addClass('list-inline-item');
        $('#about').removeClass('nav-item');
        $('#about').addClass('list-inline-item');
        $('#faqs').removeClass('nav-item');
        $('#faqs').addClass('list-inline-item');
        $('#login').removeClass('nav-item');
        $('#login').addClass('list-inline-item');
        $('#signup').removeClass('nav-item');
        $('#signup').addClass('list-inline-item');
    }
});
