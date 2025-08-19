// app/static/js/socket.js
(function () {
  if (typeof io === "undefined") return; // socket.io not loaded
  const socket = io();
  const statusEl = document.getElementById("status");
  if (!statusEl) return;

  socket.on("connect", () => {
    statusEl.textContent = "Connected for live status…";
  });

  socket.on("status", (payload) => {
    const line = document.createElement("div");
    line.textContent = payload.msg;
    statusEl.appendChild(line);
  });
})();
