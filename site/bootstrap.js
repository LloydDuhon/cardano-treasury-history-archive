(function () {
  function showError(message) {
    var root = document.getElementById("root");
    if (!root) return;
    root.textContent = message;
  }

  fetch("data.json", { credentials: "same-origin" })
    .then(function (response) {
      if (!response.ok) throw new Error("HTTP " + response.status);
      return response.json();
    })
    .then(function (data) {
      window.__TREASURY_DATA = data;
      var script = document.createElement("script");
      script.src = "bundle.js";
      script.defer = true;
      script.onerror = function () {
        showError("Unable to load the dashboard application bundle.");
      };
      document.body.appendChild(script);
    })
    .catch(function (error) {
      showError("Unable to load dashboard data: " + error.message);
    });
})();
