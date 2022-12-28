$(document).ready(function () {
    $(".mail-anchor").click(function () {

        const template = $(this).data('target');

        // Fetch the HTML from the backend
        $.ajax({
            type: 'GET',
            url: $(this).data('url'),
            data: {
                'template': template
            },
            success: function (html) {
                // Render the mail in the preview section
                $('#preview').html(html);

                // Set the template that should be rendered in an e-mail
                $('.mail-input').val(template);
            },
            error: function (html) {
                alert("Er was een probleem bij het fetchen van de mail");
            }
        });

        // Set this menu item as selected
        $(".mail-anchor").removeClass('is-active')
        $(this).addClass("is-active");
    });
});
