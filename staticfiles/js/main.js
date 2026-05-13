// Autocomplete search
(function() {
  const input    = document.getElementById('nav-search-input');
  const dropdown = document.getElementById('autocomplete-dropdown');
  if (!input || !dropdown) return;

  let timer;
  input.addEventListener('input', function() {
    clearTimeout(timer);
    const q = this.value.trim();
    if (q.length < 2) { dropdown.style.display = 'none'; return; }
    timer = setTimeout(() => {
      fetch(`/search/?q=${encodeURIComponent(q)}`)
        .then(r => r.text())
        .then(() => {});
    }, 250);
    input.addEventListener('keydown', e => {
      if (e.key === 'Enter') {
        window.location = `/search/?q=${encodeURIComponent(input.value.trim())}`;
      }
    });
  });

  document.addEventListener('click', e => {
    if (!input.contains(e.target) && !dropdown.contains(e.target))
      dropdown.style.display = 'none';
  });
})();

// Auto-dismiss messages
document.querySelectorAll('.message-toast').forEach(el => {
  setTimeout(() => {
    el.style.transition = 'opacity 0.4s';
    el.style.opacity = '0';
    setTimeout(() => el.remove(), 400);
  }, 4000);
});

// Lazy load images
if ('IntersectionObserver' in window) {
  const imgs = document.querySelectorAll('img[data-src]');
  const obs  = new IntersectionObserver((entries, o) => {
    entries.forEach(e => {
      if (e.isIntersecting) {
        e.target.src = e.target.dataset.src;
        e.target.removeAttribute('data-src');
        o.unobserve(e.target);
      }
    });
  }, { rootMargin: '100px' });
  imgs.forEach(img => obs.observe(img));
}

// Animated bar charts
document.querySelectorAll('.chart-bar-fill[data-width]').forEach(el => {
  setTimeout(() => { el.style.width = el.dataset.width + '%'; }, 100);
});

// Card tilt effect
document.querySelectorAll('.pokemon-card').forEach(card => {
  card.addEventListener('mousemove', e => {
    const rect = card.getBoundingClientRect();
    const x = (e.clientX - rect.left) / rect.width  - 0.5;
    const y = (e.clientY - rect.top)  / rect.height - 0.5;
    card.style.transform = `translateY(-4px) rotateY(${x * 8}deg) rotateX(${-y * 8}deg)`;
  });
  card.addEventListener('mouseleave', () => {
    card.style.transition = 'transform 0.4s ease';
    card.style.transform  = '';
  });
  card.addEventListener('mouseenter', () => {
    card.style.transition = 'transform 0.15s ease';
  });
});