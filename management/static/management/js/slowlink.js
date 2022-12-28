$(document).ready(function () {
    $(".slow-link").click(function () {
        const url = $(this).data('url');
        $('#slowmodal').addClass('is-active');
        $.ajax({
            type: 'GET',
            url: url,
            success: function (html) {
                document.write(html);
                window.location = url;
            }
        })
    })
})
