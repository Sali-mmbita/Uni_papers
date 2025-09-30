/* app/static/js/home.js
   Interactivity:
   - typed headline
   - navbar background on scroll
   - mobile nav toggle
   - progress-line fill based on intersection of steps
   - smooth scrolling for anchor links
*/

document.addEventListener('DOMContentLoaded', function() {
  // ======== Typed effect (simple, small)
  const typedEl = document.getElementById('typed');
  const phrases = ['CogniPrep', 'Find Past Papers Fast', 'Revise Smarter'];
  let charIndex = 0, phraseIndex = 0, typing = true;

  function doType() {
    const current = phrases[phraseIndex];
    if (charIndex <= current.length) {
      typedEl.textContent = current.slice(0,charIndex);
      charIndex++;
      setTimeout(doType, 80);
    } else {
      // pause, then delete
      setTimeout(() => erase(), 900);
    }
  }
  function erase() {
    const current = phrases[phraseIndex];
    if (charIndex > 0) {
      typedEl.textContent = current.slice(0,charIndex-1);
      charIndex--;
      setTimeout(erase, 40);
    } else {
      phraseIndex = (phraseIndex + 1) % phrases.length;
      setTimeout(doType, 200);
    }
  }
  doType();

  // ======== Navbar background toggle on scroll
  const header = document.getElementById('site-header');
  function onScroll() {
    if (window.scrollY > 20) header.classList.add('scrolled');
    else header.classList.remove('scrolled');
  }
  window.addEventListener('scroll', onScroll);
  onScroll();

  // ======== Mobile nav toggle
  const navToggle = document.getElementById('nav-toggle');
  const navLinks = document.querySelector('.nav-links');
  if (navToggle) {
    navToggle.addEventListener('click', () => {
      navLinks.classList.toggle('visible');
    });
  }

  // ======== Smooth anchor scrolling
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
      const target = document.querySelector(this.getAttribute('href'));
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });

  // ======== Progress line fill via IntersectionObserver
  const steps = document.querySelectorAll('.how .step');
  const progressLine = document.getElementById('progress-line');
  // observe each step to determine how many are visible
  const observer = new IntersectionObserver((entries) => {
    let visibleCount = 0;
    entries.forEach(en => {
      if (en.isIntersecting) visibleCount++;
    });

    // compute percent based on how many steps are on screen
    // (cap at 100)
    const fraction = Math.min(1, visibleCount / steps.length);
    const percent = Math.round(fraction * 100);
    if (progressLine) {
      progressLine.querySelector('::after');
      // set pseudo-element height via inline style on element by using css variable
      // we'll use transform trick: set style property on element so CSS can read it via --fill
      progressLine.style.setProperty('--fill-percent', percent + '%');
      // fallback: change child pseudo via inline style hack -> use element's child overlay
      // simpler: set its background height via style
      const fillBar = progressLine.querySelector('.fill-bar');
      if (!fillBar) {
        const f = document.createElement('div');
        f.className = 'fill-bar';
        f.style.position = 'absolute';
        f.style.left = 0;
        f.style.right = 0;
        f.style.bottom = 0;
        f.style.background = 'linear-gradient(var(--accent), var(--primary))';
        f.style.borderRadius = '6px';
        f.style.width = '100%';
        f.style.height = percent + '%';
        progressLine.appendChild(f);
      } else {
        fillBar.style.height = percent + '%';
      }
    }
  }, { threshold: 0.25 });

  steps.forEach(s => observer.observe(s));

  // ======== Simple accessibility: remove cursor blink when page hidden
  document.addEventListener('visibilitychange', () => {
    const cursor = document.querySelector('.cursor');
    if (!cursor) return;
    cursor.style.opacity = document.hidden ? 0 : 1;
  });
});
