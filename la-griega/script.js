/* La Griega — Interactive Behaviors */

/* Navbar: add .scrolled class on scroll */
const navbar = document.getElementById('navbar');
window.addEventListener('scroll', () => {
  navbar.classList.toggle('scrolled', window.scrollY > 60);
}, { passive: true });

/* Mobile menu toggle */
const navToggle = document.getElementById('navToggle');
const navMenu   = document.getElementById('navMenu');
navToggle.addEventListener('click', () => {
  const isOpen = navMenu.classList.toggle('open');
  navToggle.setAttribute('aria-expanded', isOpen);
});

/* Close menu on link click */
navMenu.querySelectorAll('a').forEach(link => {
  link.addEventListener('click', () => {
    navMenu.classList.remove('open');
    navToggle.setAttribute('aria-expanded', false);
  });
});

/* Scroll Reveal */
const revealEls = document.querySelectorAll('.reveal');
const revealObs = new IntersectionObserver((entries) => {
  entries.forEach((entry, i) => {
    if (!entry.isIntersecting) return;
    /* stagger siblings in the same parent */
    const siblings = [...entry.target.parentElement.querySelectorAll('.reveal:not(.visible)')];
    const order = siblings.indexOf(entry.target);
    setTimeout(() => {
      entry.target.classList.add('visible');
    }, order * 80);
    revealObs.unobserve(entry.target);
  });
}, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });

revealEls.forEach(el => revealObs.observe(el));

/* Smooth scroll for anchor links */
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
  anchor.addEventListener('click', (e) => {
    const target = document.querySelector(anchor.getAttribute('href'));
    if (!target) return;
    e.preventDefault();
    const offset = navbar.offsetHeight + 12;
    window.scrollTo({ top: target.offsetTop - offset, behavior: 'smooth' });
  });
});

/* Active nav link highlight on scroll */
const sections = document.querySelectorAll('section[id]');
const navLinks = document.querySelectorAll('.navbar__nav a[href^="#"]');

const sectionObs = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (!entry.isIntersecting) return;
    navLinks.forEach(link => link.classList.remove('active'));
    const active = document.querySelector(`.navbar__nav a[href="#${entry.target.id}"]`);
    if (active) active.classList.add('active');
  });
}, { rootMargin: '-40% 0px -55% 0px' });

sections.forEach(s => sectionObs.observe(s));

/* Price counter animation */
function animatePrice(el) {
  const target = parseInt(el.textContent.replace(/\s/g, ''), 10);
  const duration = 900;
  const start = performance.now();

  const step = (now) => {
    const progress = Math.min((now - start) / duration, 1);
    const eased = 1 - Math.pow(1 - progress, 3);
    const current = Math.round(eased * target);
    el.textContent = current.toLocaleString('es-CR').replace(',', ' ');
    if (progress < 1) requestAnimationFrame(step);
    else el.textContent = target.toLocaleString('es-CR').replace(',', ' ');
  };
  requestAnimationFrame(step);
}

const priceEls = document.querySelectorAll('.price__amount');
const priceObs = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (!entry.isIntersecting) return;
    animatePrice(entry.target);
    priceObs.unobserve(entry.target);
  });
}, { threshold: 0.5 });

priceEls.forEach(el => priceObs.observe(el));

/* Parallax subtle on hero drops */
const drops = document.querySelectorAll('.drop');
window.addEventListener('scroll', () => {
  const y = window.scrollY;
  drops[0] && (drops[0].style.transform = `rotate(15deg) translateY(${y * 0.08}px)`);
  drops[1] && (drops[1].style.transform = `rotate(-20deg) translateY(${-y * 0.05}px)`);
}, { passive: true });
