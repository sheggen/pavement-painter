$("#imageUploadForm").submit(function(e) {
    e.preventDefault(); // avoid to execute the actual submit of the form.
    form  = $(this);
    var formData = new FormData($(this)[0]);
    $.ajax({
            method: "POST",
            url: form.attr('action'),
            data: formData,
            processData: false,
            contentType: false,

            success: function(response) {
                if (response["success"]) {
                $("#imgSection").append('<button class="dasButtons btn btn-default" id="'+response['filename']+'" onclick=switchActiveImage(this,"'+response['filename']+'") style="border: 1px lightgray solid; border-radius: 8px;">'+response['filename']+' <img src="static/images/'+response['filename']+'" height="150px" /></button>')
//                    $("#imgSection").append('<button class="badge">'+response['filename']+'<img id="'+response['filename']+'" src="static/images/'+response['filename']+'" height="150px;"></img></button>')
            }
          }
        })
});

var activeButton = null;

function switchActiveImage(btn, filename) {
    $.ajax({
        method: "POST",
        url: "switchActiveImage/"+filename,
        data: JSON.stringify({"filename": filename}),
        processData: false,
        contentType: "application/json",

        success: function(response) {
            if (response["success"]) {
                allBtns = $("#imgSection").find(".dasButtons").removeClass("btn-info");
                $(btn).addClass("btn-info");
            }
        }
    })
}

function buttonPressed(btn) {
    $.ajax({
        method: "GET",
        url: "activateButton/"+btn.id,
        success: function(response) {
            if (response["success"]) {
                allBtns = $("#imgSection").find(".dasButtons").removeClass("btn-info");
                $(btn).addClass("btn-info");
            }
        }
    })
}
