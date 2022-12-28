$('.view-modal').on('click', function() {
    if($(this).data('id') != undefined) {
        $('.modal-card').load($(this).data('id'), function() {
            setupModal();
        });
    } else {
        setupModal();
    }
});

function setupModal() {
    // Show the modal when loaded
    $('#modal').addClass('is-active');

    // Add a close listener on modal-close
    $('.modal-close').on('click', function() {
        $('#modal').removeClass('is-active');
    });

    // Add a listener for buttons inside the modal
    $('.modal-close-inside').on('click', function() {
        $('#modal').removeClass('is-active');
    });
}
