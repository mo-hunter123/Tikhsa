$(document).ready(function() {
    $('.addButton').on('click', function() {
        var rel_id = $('#rel_id').val();
        var compteur_id = $(this).attr('compteur_id');
        var consommation = $('#ReleveConsommation'+compteur_id).val();
        var commentaire = $('#CommentFormTextarea'+compteur_id).val();

        req = $.ajax({
            url : '/addrelev/submit',
            type : 'POST',
            data : {rel_id : rel_id, compteur_id : compteur_id, consommationActuelle : consommation, comment : commentaire}
        });
        req.done(function(data) {
            $('#Changeable'+compteur_id).html("you are good now");
        }); 
    });
});