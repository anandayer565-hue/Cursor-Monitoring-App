/* Demo Monitor — history charts (Chart.js via CDN when available). */
(function () {
  var dataEl = document.getElementById("history-data");
  var canvas = document.getElementById("history-chart");
  if (!dataEl || !canvas) return;

  function render(Chart) {
    var payload;
    try {
      payload = JSON.parse(dataEl.textContent || "{}");
    } catch (e) {
      return;
    }
    new Chart(canvas.getContext("2d"), {
      type: "line",
      data: {
        labels: payload.labels || [],
        datasets: [
          { label: "CPU %", data: payload.cpu || [], borderColor: "#0d6e6e", tension: 0.2 },
          { label: "Memory %", data: payload.memory || [], borderColor: "#a85c00", tension: 0.2 },
          { label: "Disk %", data: payload.disk || [], borderColor: "#3d5a80", tension: 0.2 },
        ],
      },
      options: {
        responsive: true,
        plugins: { legend: { position: "bottom" } },
        scales: { y: { beginAtZero: true, suggestedMax: 100 } },
      },
    });
  }

  if (window.Chart) {
    render(window.Chart);
    return;
  }
  var s = document.createElement("script");
  s.src = "https://cdn.jsdelivr.net/npm/chart.js@4.4.6/dist/chart.umd.min.js";
  s.onload = function () {
    render(window.Chart);
  };
  document.head.appendChild(s);
})();
