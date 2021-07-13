
$(document).ready(function(){
    //Perform Ajax request.
    $.ajax({
        url: '/api/rpi/roomid',
        type: 'get',
        success: function(data){
            console.log(data.room_id)
            $('#room_id').val(data.room_id);
        },
        error: function (xhr, ajaxOptions, thrownError) {
            var errorMsg = 'Ajax request failed: ' + xhr.responseText;
            $('#content').html(errorMsg);
          }
    });
});

$('#submit').on('click', function(event) {
    jQuery.ajax({
        url: '/api/rpi/login',
        type: "POST",
        dataType: "json",
        contentType: 'application/json',
        data: JSON.stringify({            
            room_id:$('#room_id').val(),
            email:$('#email').val(),
            password:$('#password').val()
        }),
        processData: false,
        success: function(data) {
            if(data.msg=="Room ID Updated"){
                alert("Successfully Updated!")
                location.reload()
            }else{
                alert("Update not successfull!")
                location.reload()
            }
        }, 
        error: function( jqXhr, textStatus, errorThrown ){
            console.log( errorThrown );
            alert("Update not successfull!")
                location.reload()
        }
});

    event.preventDefault();

});