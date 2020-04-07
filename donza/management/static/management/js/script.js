$(document).ready(function () {
    $(document.body).on("click", "tr[data-href]", function () {
        window.location.href = this.dataset.href;
    })
});

$('#inputGroupFile01').on('change',function() {
    //get the file name
    var fileName = $(this).val().replace("C:\\fakepath\\", "");
    //replace the "Choose a file" label
    $(this).next('.custom-file-label').html(fileName);
});