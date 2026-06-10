/* founder.js — Vizolane Founder Profile */

// ── MOUSE GLOW ────────────────────────────────────────────────────────────
(function initMouseGlow() {
  const glow = document.createElement('div');
  glow.className = 'mouse-glow';
  document.body.appendChild(glow);
  let mx = 0, my = 0, cx = 0, cy = 0;
  document.addEventListener('mousemove', e => { mx = e.clientX; my = e.clientY; });
  function tick() {
    cx += (mx - cx) * 0.08;
    cy += (my - cy) * 0.08;
    glow.style.left = cx + 'px';
    glow.style.top  = cy + 'px';
    requestAnimationFrame(tick);
  }
  tick();
})();

// ── PARTICLES ─────────────────────────────────────────────────────────────
(function initParticles() {
  const container = document.getElementById('particles');
  if (!container) return;
  for (let i = 0; i < 30; i++) {
    const p = document.createElement('div');
    p.className = 'particle';
    const size = Math.random() * 3 + 1;
    const left = Math.random() * 100;
    const delay = Math.random() * 10;
    const dur   = 8 + Math.random() * 12;
    const top   = Math.random() * 100;
    p.style.cssText = `
      width:${size}px; height:${size}px;
      left:${left}%;  top:${top}%;
      animation-duration:${dur}s;
      animation-delay:${delay}s;
      filter:blur(${size > 2 ? 1 : 0}px);
    `;
    container.appendChild(p);
  }
})();

// ── NAV SCROLL ────────────────────────────────────────────────────────────
(function initNav() {
  const nav = document.getElementById('nav');
  const burger = document.getElementById('navBurger');
  window.addEventListener('scroll', () => {
    nav.classList.toggle('scrolled', window.scrollY > 40);
  }, { passive: true });
  burger && burger.addEventListener('click', () => {
    nav.classList.toggle('mobile-open');
  });
  // close on nav link click
  document.querySelectorAll('.nav__links a').forEach(a => {
    a.addEventListener('click', () => nav.classList.remove('mobile-open'));
  });
})();

// ── ROLE TYPER ────────────────────────────────────────────────────────────
(function initRoleTyper() {
  const el = document.querySelector('.role-static');
  if (!el) return;
  const roles = [
    'Technology Strategist',
    'AI Solutions Architect',
    'Data Engineer',
    'Startup Founder',
  ];
  let ri = 0, ci = 0, deleting = false;

  // Add cursor
  const cursor = document.createElement('span');
  cursor.className = 'cursor';
  el.insertAdjacentElement('afterend', cursor);

  function type() {
    const current = roles[ri];
    if (!deleting) {
      el.textContent = current.slice(0, ++ci);
      if (ci === current.length) {
        deleting = true;
        setTimeout(type, 1800);
        return;
      }
      setTimeout(type, 65);
    } else {
      el.textContent = current.slice(0, --ci);
      if (ci === 0) {
        deleting = false;
        ri = (ri + 1) % roles.length;
        setTimeout(type, 350);
        return;
      }
      setTimeout(type, 35);
    }
  }
  type();
})();

// ── SCROLL REVEAL ─────────────────────────────────────────────────────────
(function initReveal() {
  const items = document.querySelectorAll('[data-reveal]');
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (!entry.isIntersecting) return;
      const el = entry.target;
      const delay = parseInt(el.dataset.delay || 0);
      setTimeout(() => el.classList.add('revealed'), delay);
      observer.unobserve(el);
    });
  }, { threshold: 0.12 });
  items.forEach(el => observer.observe(el));
})();

// ── COUNTER ANIMATION ─────────────────────────────────────────────────────
(function initCounters() {
  const counters = document.querySelectorAll('[data-count]');
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (!entry.isIntersecting) return;
      const el = entry.target;
      const target = parseInt(el.dataset.count);
      const duration = 1200;
      const start = performance.now();
      function step(now) {
        const progress = Math.min((now - start) / duration, 1);
        const ease = 1 - Math.pow(1 - progress, 3);
        el.textContent = Math.round(ease * target);
        if (progress < 1) requestAnimationFrame(step);
        else el.textContent = target;
      }
      requestAnimationFrame(step);
      observer.unobserve(el);
    });
  }, { threshold: 0.5 });
  counters.forEach(el => observer.observe(el));
})();

// ── TIMELINE LINE ANIMATION ───────────────────────────────────────────────
(function initTimelineLine() {
  const line = document.getElementById('timelineLine');
  if (!line) return;
  const observer = new IntersectionObserver((entries) => {
    if (entries[0].isIntersecting) {
      setTimeout(() => line.classList.add('animated'), 200);
      observer.disconnect();
    }
  }, { threshold: 0.1 });
  observer.observe(line.parentElement);
})();

// ── FLOATING CARD PARALLAX ────────────────────────────────────────────────
(function initFloatParallax() {
  const cards = document.querySelectorAll('.float-card');
  if (!cards.length) return;
  const factors = [0.015, -0.02, -0.012, 0.018];
  document.addEventListener('mousemove', e => {
    const cx = window.innerWidth  / 2;
    const cy = window.innerHeight / 2;
    const dx = e.clientX - cx;
    const dy = e.clientY - cy;
    cards.forEach((card, i) => {
      const f = factors[i] || 0.015;
      card.style.transform = `translate(${dx * f}px, ${dy * f}px)`;
    });
  });
})();

// ── SMOOTH SECTION HIGHLIGHT (active nav) ────────────────────────────────
(function initActiveNav() {
  const sections = document.querySelectorAll('section[id]');
  const links = document.querySelectorAll('.nav__links a');
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (!entry.isIntersecting) return;
      links.forEach(a => a.style.color = '');
      const match = document.querySelector(`.nav__links a[href="#${entry.target.id}"]`);
      if (match) match.style.color = '#60A5FA';
    });
  }, { rootMargin: '-40% 0px -50% 0px' });
  sections.forEach(s => observer.observe(s));
})();
