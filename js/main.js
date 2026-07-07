/* LENS ON THE STREET — interactions (vanilla, no dependencies)
   1. wordmark letter stagger  2. header hide-on-scroll  3. mobile nav
   4. scroll reveals           5. subtle image parallax  6. lightbox   */
(function () {
  "use strict";
  document.documentElement.classList.add("js");
  const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* 1 ─ wordmark: split into letters, stagger them in */
  document.querySelectorAll(".wordmark[data-animate]").forEach((el) => {
    if (reduced) return;
    const text = el.textContent;
    el.textContent = "";
    [...text].forEach((ch, i) => {
      const s = document.createElement("span");
      s.className = "ch";
      s.style.setProperty("--i", i);
      s.textContent = ch === " " ? "\u00A0" : ch;
      el.appendChild(s);
    });
    requestAnimationFrame(() => el.classList.add("animate"));
  });

  /* 2 ─ header hides scrolling down, returns scrolling up */
  const header = document.querySelector(".site-header");
  let lastY = window.scrollY;
  window.addEventListener("scroll", () => {
    const y = window.scrollY;
    if (header) header.classList.toggle("hidden", y > 140 && y > lastY);
    lastY = y;
  }, { passive: true });

  /* 3 ─ mobile nav */
  const toggle = document.querySelector(".nav-toggle");
  const nav = document.querySelector(".site-nav");
  if (toggle && nav) {
    toggle.addEventListener("click", () => {
      const open = nav.classList.toggle("open");
      toggle.setAttribute("aria-expanded", String(open));
    });
  }

  /* 4 ─ scroll reveals (staggered inside grids) */
  const io = new IntersectionObserver((entries) => {
    entries.forEach((e) => {
      if (e.isIntersecting) { e.target.classList.add("in"); io.unobserve(e.target); }
    });
  }, { rootMargin: "0px 0px -8% 0px", threshold: 0.05 });
  document.querySelectorAll(".reveal").forEach((el, i) => {
    const siblings = el.parentElement ? [...el.parentElement.children] : [];
    const idx = siblings.indexOf(el);
    el.style.setProperty("--d", `${Math.min(idx, 5) * 70}ms`);
    io.observe(el);
  });

  /* 5 ─ subtle parallax on flagged images */
  const plx = [...document.querySelectorAll("[data-parallax] img")];
  if (plx.length && !reduced) {
    let ticking = false;
    const update = () => {
      const vh = window.innerHeight;
      plx.forEach((img) => {
        const r = img.parentElement.getBoundingClientRect();
        if (r.bottom < 0 || r.top > vh) return;
        const progress = (r.top + r.height / 2 - vh / 2) / vh; // -1..1
        img.style.transform = `translateY(${(-progress * 26).toFixed(1)}px) scale(1.06)`;
      });
      ticking = false;
    };
    window.addEventListener("scroll", () => {
      if (!ticking) { requestAnimationFrame(update); ticking = true; }
    }, { passive: true });
    update();
  }

  /* 6 ─ lightbox with prev/next, counter, keyboard */
  const box = document.querySelector(".lightbox");
  if (!box) return;
  const boxImg = box.querySelector("img");
  const boxCap = box.querySelector("figcaption");
  const counter = box.querySelector(".lightbox-counter");
  const items = [...document.querySelectorAll(".p-item img, .g-item img")];
  let cur = -1;

  const pad = (n) => String(n).padStart(2, "0");
  const show = (i) => {
    cur = (i + items.length) % items.length;
    const img = items[cur];
    boxImg.src = img.currentSrc || img.src;
    boxImg.alt = img.alt || "";
    const cap = img.closest("figure")?.querySelector("figcaption");
    boxCap.textContent = cap ? cap.textContent : (img.alt || "");
    counter.textContent = `${pad(cur + 1)} / ${pad(items.length)}`;
    box.hidden = false;
    document.body.style.overflow = "hidden";
  };
  const close = () => { box.hidden = true; document.body.style.overflow = ""; };

  items.forEach((img, i) => img.addEventListener("click", () => show(i)));
  box.querySelector(".lightbox-prev").addEventListener("click", (e) => { e.stopPropagation(); show(cur - 1); });
  box.querySelector(".lightbox-next").addEventListener("click", (e) => { e.stopPropagation(); show(cur + 1); });
  box.addEventListener("click", (e) => {
    if (e.target === box || e.target.closest(".lightbox-close")) close();
  });
  document.addEventListener("keydown", (e) => {
    if (box.hidden) return;
    if (e.key === "Escape") close();
    if (e.key === "ArrowLeft") show(cur - 1);
    if (e.key === "ArrowRight") show(cur + 1);
  });
})();
