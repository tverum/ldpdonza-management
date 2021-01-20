$(document).ready(function () {
    $(".slow-link").click(function () {
        $('#slowmodal').addClass('is-active');
        $.ajax({
            type: 'GET',
            url: $(this).data('url'),
            success: function (html) {
                document.write(html);
            }
        })
    })
})