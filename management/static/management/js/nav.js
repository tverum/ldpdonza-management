$(document).ready(function () {
    $('body').on('click', function (e) {
        if ($('li.nav-item.dropdown .dropdown-menu a').is(e.target)) {
            if ($(this).parent().parent().toggleClass('open').length = 1) {
                $('li.nav-item.dropdown').removeClass('open');
            }
        }
    })
    $('li.nav-item.dropdown a').on('click', function (event) {
        $(this).parent().toggleClass('open');
    });
});