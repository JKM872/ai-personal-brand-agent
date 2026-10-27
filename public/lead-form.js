// Lead form handler (vanilla JS). Sends JSON to /api/lead; falls back to mailto when storage is unavailable.
(function () {
  var MSG = {
    required: "To pole jest wymagane.",
    invalid: "Nieprawidłowa wartość.",
    too_long: "Za długi tekst.",
  };
  function setup(form) {
    var tsField = form.querySelector('input[name="ts"]');
    if (tsField) tsField.value = String(Date.now());
    var params = new URLSearchParams(window.location.search);
    ["utm_source", "utm_medium", "utm_campaign"].forEach(function (k) {
      var f = form.querySelector('input[name="' + k + '"]');
      if (f && params.get(k)) f.value = params.get(k).slice(0, 100);
    });
    var status = form.querySelector('[role="status"]');
    var contact = form.getAttribute("data-contact-email") || "";

    function clearErrors() {
      form.querySelectorAll("[aria-invalid]").forEach(function (el) { el.removeAttribute("aria-invalid"); });
      form.querySelectorAll(".lead-error").forEach(function (el) { el.textContent = ""; });
    }
    function mailtoLink(data) {
      var subject = encodeURIComponent("Zapytanie: " + (data.service || "konsultacja"));
      var body = encodeURIComponent((data.message || "") + "\n\n" + (data.name || "") + " " + (data.company || ""));
      return "mailto:" + contact + "?subject=" + subject + "&body=" + body;
    }
    function showFallback(data) {
      status.innerHTML = "";
      status.appendChild(document.createTextNode("Nie udało się zapisać formularza. Napisz bezpośrednio: "));
      var a = document.createElement("a");
      a.href = mailtoLink(data);
      a.textContent = contact || "e-mail";
      status.appendChild(a);
    }

    form.addEventListener("submit", function (e) {
      e.preventDefault();
      clearErrors();
      var fd = new FormData(form);
      var data = {};
      fd.forEach(function (v, k) { data[k] = typeof v === "string" ? v : ""; });
      data.consent = !!form.querySelector('input[name="consent"]').checked;
      data.ts = Number(data.ts) || 0;
      status.textContent = "Wysyłanie…";
      fetch(form.getAttribute("action") || "/api/lead", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      }).then(function (r) {
        return r.json().catch(function () { return {}; }).then(function (j) { return { code: r.status, body: j }; });
      }).then(function (res) {
        if (res.code === 200 && res.body.ok) {
          form.reset();
          status.textContent = "Dziękuję! Odezwę się w ciągu 1–2 dni roboczych.";
        } else if (res.code === 400 && res.body.errors) {
          status.textContent = "Popraw zaznaczone pola.";
          Object.keys(res.body.errors).forEach(function (k) {
            var input = form.querySelector('[name="' + k + '"]');
            var err = form.querySelector("#lead-err-" + k);
            if (input) input.setAttribute("aria-invalid", "true");
            if (err) err.textContent = MSG[res.body.errors[k]] || MSG.invalid;
          });
        } else {
          showFallback(data);
        }
      }).catch(function () { showFallback(data); });
    });
  }
  document.querySelectorAll("form.lead-form").forEach(setup);
})();
