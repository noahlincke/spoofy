$(document).ready(function() {
  $("form").on("submit", function(event) {
    counter = 0;
    while (counter < 10) {
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
      counter++;
    }
    event.preventDefault();
  });
});
