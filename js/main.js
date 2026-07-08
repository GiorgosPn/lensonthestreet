/* LENS ON THE STREET — interactions (vanilla, zero dependencies)
   1 loader "developing"      2 Athens clock        3 hero word rise
   4 header hide + progress   5 scroll reveals      6 negative-strip advance
   7 collections stage fade   8 lightbox            9 gold cursor dot
   10 mobile nav                                                        */
(function () {
  "use strict";
  document.documentElement.classList.add("js");
  const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const finePointer = window.matchMedia("(hover: hover) and (pointer: fine)").matches;

  /* 1 ─ loader */
  const loader = document.querySelector(".loader");
  const startHero = () => document.querySelector(".hero-title")?.classList.add("animate");
  if (loader && !reduced && !sessionStorage.getItem("lots-seen")) {
    const count = loader.querySelector(".loader-count");
    const T = 1050; let t0 = null;
    const tick = (ts) => {
      if (!t0) t0 = ts;
      const p = Math.min((ts - t0) / T, 1);
      count.textContent = String(Math.round(p * 100)).padStart(3, "0");
      if (p < 1) requestAnimationFrame(tick);
      else {
        loader.classList.add("done");
        sessionStorage.setItem("lots-seen", "1");
        setTimeout(startHero, 220);
        setTimeout(() => loader.remove(), 1000);
      }
    };
    requestAnimationFrame(tick);
  } else { loader?.remove(); startHero(); }

  /* 2 ─ Athens clock */
  const clock = document.querySelector("[data-clock]");
  if (clock) {
    const draw = () => {
      const t = new Date().toLocaleTimeString("en-GB", { timeZone: "Europe/Athens", hour12: false });
      clock.textContent = `ATHENS — ${t}`;
    };
    draw(); setInterval(draw, 1000);
  }

  /* 3 ─ hero word split */
  document.querySelectorAll("[data-split] .ln").forEach((ln) => {
    const words = ln.textContent.trim().split(/\s+/);
    ln.textContent = "";
    words.forEach((w, i) => {
      const s = document.createElement("span");
      s.className = "wd";
      s.style.setProperty("--i", i);
      s.innerHTML = w.replace(/\*(.+)\*/, "<em>$1</em>");
      ln.appendChild(s);
      if (i < words.length - 1) ln.appendChild(document.createTextNode("\u00A0"));
    });
  });

  /* 4 ─ header hide + scroll progress */
  const header = document.querySelector(".site-header");
  const progress = document.querySelector(".progress");
  let lastY = window.scrollY;
  const onScroll = () => {
    const y = window.scrollY;
    header?.classList.toggle("hidden", y > 160 && y > lastY);
    lastY = y;
    if (progress) {
      const max = document.documentElement.scrollHeight - innerHeight;
      progress.style.transform = `scaleX(${max > 0 ? y / max : 0})`;
    }
  };
  addEventListener("scroll", onScroll, { passive: true });
  onScroll();

  /* 5 ─ reveals */
  const io = new IntersectionObserver((es) => es.forEach((e) => {
    if (e.isIntersecting) { e.target.classList.add("in"); io.unobserve(e.target); }
  }), { rootMargin: "0px 0px -8% 0px", threshold: 0.05 });
  document.querySelectorAll(".reveal").forEach((el) => {
    const idx = el.parentElement ? [...el.parentElement.children].indexOf(el) : 0;
    el.style.setProperty("--d", `${Math.min(idx, 6) * 60}ms`);
    io.observe(el);
  });

  /* 6 ─ negative strip: vertical scroll advances the film */
  const stripSection = document.querySelector(".strip-section");
  const track = document.querySelector("[data-strip]");
  if (stripSection && track) {
    let active = false;
    const nativeMode = () => reduced || innerWidth < 760;
    const setup = () => {
      if (nativeMode()) {
        stripSection.classList.add("strip-native");
        stripSection.style.height = "";
        track.style.transform = "";
        const hint = document.querySelector("[data-strip-hint]");
        if (hint) hint.textContent = "Swipe — the film advances";
        active = false; return;
      }
      stripSection.classList.remove("strip-native");
      const head = stripSection.querySelector(".section-head");
      const overflow = track.scrollWidth - innerWidth;
      stripSection.style.height = overflow > 0
        ? `${overflow + innerHeight + (head ? head.offsetHeight : 0)}px` : "";
      active = overflow > 0;
    };
    const advance = () => {
      if (!active) return;
      const sticky = stripSection.querySelector(".strip-sticky");
      const r = sticky.getBoundingClientRect();
      const total = stripSection.offsetHeight - innerHeight;
      const top = stripSection.getBoundingClientRect().top;
      const p = Math.min(Math.max(-top / total, 0), 1);
      track.style.transform = `translateX(${-p * (track.scrollWidth - innerWidth)}px)`;
    };
    addEventListener("scroll", advance, { passive: true });
    addEventListener("resize", () => { setup(); advance(); });
    Promise.all([...track.querySelectorAll("img")].map((img) =>
      img.complete ? null : new Promise((res) => { img.onload = img.onerror = res; })
    )).then(() => { setup(); advance(); });
    setup();
  }

  /* 7 ─ collections stage crossfade (fixed frame, no cursor chasing) */
  const stage = document.querySelector(".col-stage-frame");
  if (stage) {
    const sImg = stage.querySelector("img");
    const sCap = document.querySelector("[data-stage-name]");
    const sCnt = document.querySelector("[data-stage-count]");
    let current = sImg.src;
    document.querySelectorAll(".col-row").forEach((row) => {
      const swap = () => {
        document.querySelectorAll(".col-row.active").forEach((r) => r.classList.remove("active"));
        row.classList.add("active");
        if (sCap) sCap.textContent = row.querySelector(".name").textContent;
        if (sCnt) sCnt.textContent = row.querySelector(".count").textContent;
        const src = row.dataset.preview;
        if (!src || src === current) return;
        current = src;
        if (reduced) { sImg.src = src; return; }
        stage.classList.add("fading");
        setTimeout(() => {
          sImg.onload = () => stage.classList.remove("fading");
          sImg.src = src;
        }, 220);
      };
      row.addEventListener("mouseenter", swap);
      row.addEventListener("focus", swap);
    });
  }

  /* 8 ─ lightbox */
  const box = document.querySelector(".lightbox");
  if (box) {
    const bImg = box.querySelector("img");
    const bCap = box.querySelector("figcaption");
    const bCnt = box.querySelector(".lightbox-counter");
    const items = [...document.querySelectorAll(".frame img, .p-item img")];
    let cur = -1;
    const pad = (n) => String(n).padStart(2, "0");
    const show = (i) => {
      cur = (i + items.length) % items.length;
      const img = items[cur];
      bImg.src = img.currentSrc || img.src;
      bImg.alt = img.alt || "";
      const cap = img.closest("figure")?.querySelector("figcaption");
      bCap.textContent = cap ? cap.textContent.trim() : (img.alt || "");
      bCnt.textContent = `${pad(cur + 1)} / ${pad(items.length)}`;
      box.hidden = false;
      document.body.style.overflow = "hidden";
    };
    const close = () => { box.hidden = true; document.body.style.overflow = ""; };
    items.forEach((img, i) => img.addEventListener("click", () => show(i)));
    box.querySelector(".lightbox-prev").addEventListener("click", (e) => { e.stopPropagation(); show(cur - 1); });
    box.querySelector(".lightbox-next").addEventListener("click", (e) => { e.stopPropagation(); show(cur + 1); });
    box.addEventListener("click", (e) => { if (e.target === box || e.target.closest(".lightbox-close")) close(); });
    addEventListener("keydown", (e) => {
      if (box.hidden) return;
      if (e.key === "Escape") close();
      if (e.key === "ArrowLeft") show(cur - 1);
      if (e.key === "ArrowRight") show(cur + 1);
    });
  }

  /* 9 ─ gold cursor dot */
  const cursor = document.querySelector(".cursor");
  if (cursor && finePointer && !reduced) {
    let cx = -100, cy = -100, mx = -100, my = -100;
    addEventListener("mousemove", (e) => { mx = e.clientX; my = e.clientY; cursor.classList.add("on"); }, { passive: true });
    (function follow() {
      cx += (mx - cx) * 0.22; cy += (my - cy) * 0.22;
      cursor.style.left = `${cx}px`; cursor.style.top = `${cy}px`;
      requestAnimationFrame(follow);
    })();
    document.querySelectorAll("a, button, summary, .frame, .p-item").forEach((el) => {
      el.addEventListener("mouseenter", () => cursor.classList.add("grow"));
      el.addEventListener("mouseleave", () => cursor.classList.remove("grow"));
    });
  }

  /* 10 ─ mobile nav */
  const toggle = document.querySelector(".nav-toggle");
  const nav = document.querySelector(".site-nav");
  if (toggle && nav) {
    toggle.addEventListener("click", () => {
      const open = nav.classList.toggle("open");
      toggle.setAttribute("aria-expanded", String(open));
    });
  }

  /* 11 ─ theme toggle (light / dark, remembered) */
  const themeBtn = document.querySelector("[data-theme-toggle]");
  if (themeBtn) {
    const root = document.documentElement;
    const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
    const current = () => {
      const set = root.getAttribute("data-theme");
      if (set) return set;
      return prefersDark ? "dark" : "light";
    };
    themeBtn.addEventListener("click", () => {
      const next = current() === "dark" ? "light" : "dark";
      root.setAttribute("data-theme", next);
      try { localStorage.setItem("lots-theme", next); } catch (e) {}
    });
  }
})();