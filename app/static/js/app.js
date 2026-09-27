// Utilitários de UI: toast de sucesso, modais e registro rápido.

(function () {
  // --- Toast de sucesso -----------------------------------------------
  function showToast(msg) {
    const toast = document.getElementById("toast");
    if (!toast) return;
    if (msg) document.getElementById("toast-msg").textContent = msg;
    toast.classList.remove("hidden");
    setTimeout(() => toast.classList.add("hidden"), 2600);
  }
  window.showToast = showToast;

  // Mostra toast automaticamente quando a URL tem ?ok=1
  const params = new URLSearchParams(window.location.search);
  if (params.get("ok") === "1") {
    showToast("Registro salvo com sucesso!");
    // limpa o parâmetro da URL sem recarregar
    params.delete("ok");
    const clean =
      window.location.pathname +
      (params.toString() ? "?" + params.toString() : "");
    window.history.replaceState({}, "", clean);
  }

  // --- Modais genéricos -----------------------------------------------
  window.openModal = function (id) {
    const el = document.getElementById(id);
    if (el) {
      el.classList.remove("hidden");
      el.classList.add("flex");
      document.body.style.overflow = "hidden";
    }
  };
  window.closeModal = function (id) {
    const el = document.getElementById(id);
    if (el) {
      el.classList.add("hidden");
      el.classList.remove("flex");
      document.body.style.overflow = "";
    }
  };

  // Fecha modal ao clicar no backdrop
  document.addEventListener("click", function (e) {
    if (e.target.dataset && e.target.dataset.modalBackdrop !== undefined) {
      const id = e.target.dataset.modalBackdrop;
      window.closeModal(id);
    }
  });

  // Fecha modal com ESC
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") {
      document.querySelectorAll("[data-modal].flex").forEach((m) => {
        window.closeModal(m.id);
      });
    }
  });

  // --- FAB Registro Rápido --------------------------------------------
  window.toggleFab = function () {
    const menu = document.getElementById("fab-menu");
    if (menu) menu.classList.toggle("hidden");
  };
})();
