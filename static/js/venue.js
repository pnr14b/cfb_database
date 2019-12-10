const log = $("#log");
//const file_input = $("#file_input");
const submit = $("#submit");
const warning = $("#warning");
const table = $("#mytable");
// file_input.on("change", function(){
//     var nameSplit = file_input.val().split(".");
//     if(nameSplit[nameSplit.length - 1].toLowerCase() == "mp3") {
//         warning.prop("hidden", false);
//     }
//     else {
//         warning.prop("hidden", true);
//     }
// });

// Whenever this form has a submit event,
$("form").submit(function(event) {
  // prevent form from redirecting/making a request and do this instead
  event.preventDefault();
  var t1 = event.currentTarget[0].value;
  var t2 = event.currentTarget[1].value;
  var t3 = event.currentTarget[2].value;
  // Creates FormData object and sticks file in there
  //let formData = new FormData();
  //let fileData = file_input[0].files[0];
  //formData.append("file", fileData);

  // Makes a POST request to the uploader endpoint
  // If successful, tell user file was uploaded successfully and clear #file_input
  // Else, tell user it failed
  // $.ajax({
  //     url: 'uploader',
  //     data: formData,
  //     processData: false,
  //     contentType: false,
  //     type: 'POST',
  //     beforeSend: function() {
  //         log.text(fileData.name + " is being uploaded. Please wait.");
  //         submit.prop("disabled", true);
  //     },
  //     success: function(response){
  //         console.log(response);
  //         log.text(fileData.name + " was uploaded successfully.");
  //         window.location.replace(window.location.href + "results");
  //     },
  //     error: function(){
  //         log.text("The file upload failed.");
  //         submit.prop("disabled", false);
  //     }
  // });

  $.ajax({
    url: "venue",
    data: {
      venue: t1,
      year1: t2,
      year2: t3
    },
    cache: false,
    type: "GET",
    beforeSend: function() {
      //log.text(" is being uploaded. Please wait.");
      //submit.prop("disabled", true);
    },
    success: function(response) {
      console.log(response);
      json = JSON.parse(response);
      var tr;
      for (var i = 0; i < json.length; i++) {
        tr = $("<tr/>");
        tr.append("<td>" + json[i].hometeam + "</td>");
        tr.append("<td>" + json[i].awayteam + "</td>");
        tr.append("<td>" + json[i].winner + "</td>");
        tr.append("<td>" + json[i].season + "</td>");
        tr.append("<td>" + json[i].week + "</td>");
        $("#mytable").append(tr);
      }
    },
    error: function(xhr) {
      console.log("ERROE");
    }
  });
});
