/* LENS ON THE STREET — print configurator v2
   The framed print hangs from a thin gilt cord and resizes in true
   proportion. Price rolls like a counter, every size chip shows its
   price, and the order link is rebuilt with the chosen size.         */
(function () {
  "use strict";
  const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* Το print που πουλάς. Άλλαξε τίτλο/τιμές/μεγέθη μόνο εδώ. */
  const PRINT = {
    title: "Walking Shadow",
    email: "lensonthestreet@gmail.com",
    paper: "Ilford Galerie Smooth Pearl 310",
    sizes: {
      a4: { label: "A4",      w: 21,   h: 29.7, price: 30  },
      a3: { label: "A3",      w: 29.7, h: 42,   price: 50  },
      a2: { label: "A2",      w: 42,   h: 59.4, price: 80  },
      xl: { label: "60 × 90", w: 60,   h: 90,   price: 140 }
    }
  };

  const frame = document.querySelector("[data-frame]");
  if (!frame) return;

  const stage   = document.querySelector(".print-stage");
  const wall    = document.querySelector(".print-wall");
  const chips   = [...document.querySelectorAll(".size-chip")];
  const priceEl = document.querySelector("[data-price]");
  const dimW    = document.querySelector("[data-dim-w]");
  const dimH    = document.querySelector("[data-dim-h]");
  const order   = document.querySelector("[data-order]");

  /* γέμισε τις τιμές πάνω στα chips από το PRINT object */
  chips.forEach((c) => {
    const s = PRINT.sizes[c.dataset.size];
    const el = c.querySelector("[data-chip-price]");
    if (s && el) el.textContent = `€${s.price}`;
  });

  /* px ανά cm: το μεγαλύτερο μέγεθος (60×90) πρέπει να χωράει άνετα */
  const pxPerCm = () => {
    const availW = wall.clientWidth - 120;   /* χώρος για το πλαϊνό label */
    const availH = wall.clientHeight - 120;  /* κορδόνι + δάπεδο          */
    return Math.max(1.4, Math.min(availW / 60, availH / 90, 3.4));
  };

  const rollPrice = (from, to) => {
    if (reduced) { priceEl.textContent = `€${to}`; return; }
    const T = 500; let t0 = null;
    const ease = (p) => 1 - Math.pow(1 - p, 3);
    const tick = (ts) => {
      if (!t0) t0 = ts;
      const p = Math.min((ts - t0) / T, 1);
      priceEl.textContent = `€${Math.round(from + (to - from) * ease(p))}`;
      if (p < 1) requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
  };

  let currentKey = "a3";
  const apply = (key, animate) => {
    const prev = PRINT.sizes[currentKey];
    const s = PRINT.sizes[key];
    currentKey = key;
    const k = pxPerCm();
    frame.style.width = `${s.w * k}px`;
    frame.style.height = `${s.h * k}px`;
    dimW.textContent = `${s.w} cm`;
    dimH.textContent = `${s.h} cm`;
    if (animate) rollPrice(prev.price, s.price); else priceEl.textContent = `€${s.price}`;
    const subject = encodeURIComponent(`Print request · ${PRINT.title} · ${s.label} (€${s.price})`);
    const body = encodeURIComponent(
      `Hello Giorgos,\n\nI would like to order the print "${PRINT.title}" in ${s.label} (${s.w} × ${s.h} cm) on ${PRINT.paper}, at €${s.price}.\n\nShipping address:\n\nThank you!`
    );
    order.href = `mailto:${PRINT.email}?subject=${subject}&body=${body}`;
    chips.forEach((c) => {
      const on = c.dataset.size === key;
      c.classList.toggle("active", on);
      c.setAttribute("aria-checked", String(on));
    });
    if (!reduced && animate) {
      frame.classList.remove("settle");
      void frame.offsetWidth;
      frame.classList.add("settle");
    }
  };

  chips.forEach((c) => c.addEventListener("click", () => apply(c.dataset.size, true)));
  addEventListener("resize", () => apply(currentKey, false));

  /* πρώτο render μόλις μπει στο viewport */
  const io = new IntersectionObserver((es) => es.forEach((e) => {
    if (!e.isIntersecting) return;
    io.disconnect();
    stage.classList.add("on");
    apply("a3", false);
  }), { threshold: 0.2 });
  io.observe(stage);
})();
