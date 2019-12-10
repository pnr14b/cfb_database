const log = $("#log");
//const file_input = $("#file_input");
const submit = $("#submit");
const warning = $("#warning");
const table = $("#mytable");

function callItem(id) {
  $.ajax({
    url: "stats",
    data: {
      id: id
    },
    cache: false,
    type: "GET",

    success: function(response) {
      json = JSON.parse(response);
      var tr;
      var tb = $("<tbody/>");
      $("#popup > #mytable2 tbody tr").remove();
      for (var i = 0; i < json.length; i++) {
        tr = $("<tr/>");
        tr.append("<td>" + json[i].team + "</td>");
        tr.append("<td>" + json[i].points + "</td>");
        tr.append("<td>" + json[i].yards + "</td>");
        tr.append("<td>" + json[i].rushingTDs + "</td>");
        tr.append("<td>" + json[i].passingTDs + "</td>");

        $("#popup > #mytable2").append(tr);
      }
      $("#popup > #mytable2").append(tb);
    },
    error: function(xhr) {}
  });
}

// Whenever this form has a submit event,
$("form").submit(function(event) {
  // prevent form from redirecting/making a request and do this instead
  event.preventDefault();
  var t1 = event.currentTarget[0].value;

  var t2 = event.currentTarget[1].value;
  var t3 = event.currentTarget[2].value;
  var t4 = event.currentTarget[3].value;

  $.ajax({
    url: "matchup",
    data: {
      Team1: t1,
      Team2: t2,
      year1: t3,
      year2: t4
    },
    cache: false,
    type: "GET",
    beforeSend: function() {
      //submit.prop("disabled", true);
      console.log(t2);
    },
    success: function(response) {
      console.log(response);
      json = JSON.parse(response);
      var tr;
      log.text(
        t1 +
          ":" +
          json[0].hometeam.toString() +
          "\n" +
          t2 +
          ":" +
          json[0].awayteam.toString()
      );

      for (var i = 1; i < json.length - 1; i++) {
        tr = $("<tr/>");
        tr.append("<td>" + json[i].hometeam + "</td>");
        tr.append("<td>" + json[i].awayteam + "</td>");
        tr.append("<td>" + json[i].week + "</td>");
        tr.append("<td>" + json[i].season + "</td>");
        tr.append("<td>" + json[i].winner + "</td>");
        tr.append("<td>" + json[i].venue + "</td>");
        tr.append(
          "<tr><td>" +
            "<button type='button' " +
            "id=" +
            '"' +
            json[i].id +
            '"' +
            "onclick='callItem(" +
            json[i].id +
            ")' >Stats</button>" +
            "</td></tr>"
        );

        $("#mytable").append(tr);
      }
      var totals = json[json.length - 1];
      for (var j = 0; j < totals.length; j++) {
        tr = $("<tr/>");
        tr.append("<td>" + totals[j].team + "</td>");
        tr.append("<td>" + totals[j].totpoints + "</td>");
        tr.append("<td>" + totals[j].totyards + "</td>");
        tr.append("<td>" + totals[j].totpassingTDs + "</td>");
        tr.append("<td>" + totals[j].totrushingTDs + "</td>");
        $("#popup > #mytable3").append(tr);
      }
    },
    error: function(xhr) {
      console.log("ERROR");
    }
  });
});
