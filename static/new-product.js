var formData = JSON.stringify($("#formTeste").serializeArray());


function submitform(){
$.ajax({
    type: "POST",
    url: "/image",
    contentType: 'application/json',
    data: formData,
    dataType: 'json',
    success: function() {
        console.log(data);
    }
    });
}