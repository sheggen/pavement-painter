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

/* Press and hold handlers */
$(document).ready(function() {
    btns = $("#btns_div").find("button");
    for (btn in btns) {
        $(btn).on({
            "mousedown touchstart": function(e) {
		/* If flush or startstopprint, toggle button info on/off */
		if (e.which == 1) {
		  if (this.id) {
		    console.log("Pressing " + this.id);
		    console.log("ID not null");
		    if (this.id == "startStopPrint") {
		      console.log("ID is startStopPrint")
		      if ($(this).text() == "Start Printing") {
			console.log("Switching to Stop Printing");
			$(this).text("Stop Printing")
			$(this).addClass("btn-info");
			console.log($(".btn-info"));
		      } else {
			console.log("Switching to Start Printing");
			$(this).text("Start Printing");
                        $(this).removeClass("btn-info");
		      }
		    } else if (this.id == "flush") {
		      if ($(this).hasClass("btn-info")) {
 			$(this).removeClass("btn-info");
		      } else {
			$(this).addClass("btn-info");
			$(this).animate({backgroundColor: '#FFF'}, 'slow');
		      } 
		    } else {
			console.log("ID isn't startStopButton");
		    	$(this).addClass("btn-info");
		    }
  	            pressingDown(this);
	          }
	        }
            },
            "mouseup touchend": function(e) {
	      if (e.which == 1) {
		if (this.id) {
		  console.log("Button released: " + this.id)
  		  if (this.id != "startStopPrint" && this.id != "flush") {
  		    $(this).removeClass('btn-info');
                    console.log("Calling not pressed");
		    notPressingDown(this);
	 	  }
		}
	      }
            }
        })
    }

    /* Updating vehicle speed */
    let timer1 = setInterval(() => updateSpeed(), 1000);
})

function pressingDown(btn) {
  console.log("Pressing!", btn.id);
  if (btn.id) {
    $.ajax({
      method: "GET",
      url: "activateButton/" + btn.id + "/True"
    })
  }
}

function notPressingDown(btn) {
  console.log("Not pressing!", btn.id);
    if (btn.id) {
      $.ajax({
        method: "GET",
        url: "activateButton/" + btn.id + "/False" 
      })
    }
}

function updateSpeed() {
  $.ajax({
    method: "GET",
    url: "currentSpeed",
    success: function (response) {
      $("#currentSpeed").text(response.split(" ")[0]);
      $("#scaleFactor").text(response.split(" ")[1]);
      /*console.log("Rates updated" + $("#fireRate").text() + $("#currentSpeed").text() )*/
    }
  })
}
