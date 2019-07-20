$(document).ready(function() {
  $("form").on("submit", function(event) {
    $.ajax({
      url: "/spoof",
      data: {
        username: $("#usernameInput").val(),
        password: $("#passwordInput").val(),
        latitude: $("#latitudeInput").val(),
        longitude: $("#longitudeInput").val(),
        duration: $("#durationInput").val()
      },
      type: "POST",
      success: function(response) {
        console.log(response);
      }
    });
    event.preventDefault();
  });
});
