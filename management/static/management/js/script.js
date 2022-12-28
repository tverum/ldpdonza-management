$(document).ready(function () {
    $(document.body).on("click", "td[data-href]", function () {
        window.location.href = this.dataset.href;
    });

    // only bind the function when the document is ready
    $('#inputGroupFile02').on('change', function() {
        //get the file name
        var fileName = $(this).val().replace("C:\\fakepath\\", "");
        //replace the "Choose a file" label
        $(this).next('.custom-file-label').html(fileName);
    });

    $('#getBetalingen').on('click', function () {
            $.ajax({
                type: 'GET',
                url: '/management/betalingen',
                beforeSend: function() {
                    $('#loading').show();
                    $('#loadingModal').modal('show');
                },
                success: function(data) {
                    window.location.href = '/management/betalingen';
                },
                cache: true
            });
        }
    );

    // Close mobile & tablet menu on item click
    $('.navbar-item').each(function(e) {
        $(this).click(function(){
          if($('#navbar-burger-id').hasClass('is-active')){
            $('#navbar-burger-id').removeClass('is-active');
            $('#navbar-menu-id').removeClass('is-active');
          }
        });
    });

    // Open or Close mobile & tablet menu
    $('#navbar-burger-id').click(function () {
        if($('#navbar-burger-id').hasClass('is-active')){
          $('#navbar-burger-id').removeClass('is-active');
          $('#navbar-menu-id').removeClass('is-active');
        } else {
          $('#navbar-burger-id').addClass('is-active');
          $('#navbar-menu-id').addClass('is-active');
        }
    });
});
