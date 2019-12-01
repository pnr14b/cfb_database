const log = $("#log");
//const file_input = $("#file_input");
const submit = $("#submit");
const warning = $("#warning");
const table = $("#mytable");

// Whenever this form has a submit event,
$("form").submit(function(event) {
  // prevent form from redirecting/making a request and do this instead
  event.preventDefault();
  var t1 = event.currentTarget[0].value;

  var t2 = event.currentTarget[1].value;
  var t3 = event.currentTarget[2].value;
  $.ajax({
    url: "conference_matchups",
    data: {
      c1: t1,
      c2: t2,
      season: t3
    },
    cache: false,
    type: "GET",
    beforeSend: function() {
      log.text(" is being uploaded. Please wait.");
      //submit.prop("disabled", true);
      console.log(t2);
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

        $("#mytable").append(tr);
      }
    },
    error: function(xhr) {
      console.log("ERROR");
    }
  });
});
