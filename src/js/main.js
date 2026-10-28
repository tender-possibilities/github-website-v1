(function () {
  var header = document.getElementById('header');
  var toggle = document.querySelector('.menu-toggle');
  var menu = document.getElementById('mobile-menu');

  function onScroll() {
    header.classList.toggle('shrink', window.scrollY > 10);
  }
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  // Mobile menu
  toggle.addEventListener('click', function () {
    var open = toggle.getAttribute('aria-expanded') === 'true';
    toggle.setAttribute('aria-expanded', String(!open));
    toggle.setAttribute('aria-label', open ? 'Open Menu' : 'Close Menu');
    menu.hidden = open;
    document.body.style.overflow = open ? '' : 'hidden';
  });

  // Folder (Summer Series) buttons
  document.querySelectorAll('.folder-toggle').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var li = btn.parentElement;
      var open = li.classList.toggle('open');
      btn.setAttribute('aria-expanded', String(open));
    });
  });
  document.addEventListener('click', function (e) {
    if (!e.target.closest('.site-nav .has-folder')) {
      document.querySelectorAll('.site-nav .has-folder.open').forEach(function (li) { li.classList.remove('open'); });
    }
  });

  // Accordions
  document.querySelectorAll('.accordion-title').forEach(function (btn) {
    btn.addEventListener('click', function () {
      btn.setAttribute('aria-expanded', String(btn.getAttribute('aria-expanded') !== 'true'));
    });
  });

  // Big title text that stretches to the width of its block
  function fitText() {
    document.querySelectorAll('.sqsrte-scaled-text-container').forEach(function (box) {
      var span = box.querySelector('.sqsrte-scaled-text');
      if (!span) return;
      span.style.fontSize = '100px';
      var w = span.getBoundingClientRect().width;
      if (w) span.style.fontSize = (100 * box.clientWidth / w) + 'px';
    });
  }
  fitText();
  window.addEventListener('resize', fitText);
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(fitText);

  // Fade/slide things in as they scroll into view
  var targets = document.querySelectorAll('.block .text > *, .event-body > *, .event-meta, .event-title, .event-nav, .block .img');
  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting || entry.boundingClientRect.top < 0) {
          var el = entry.target;
          var img = el.querySelector(':scope > .img, :scope > a > .img');
          (img || el).classList.add('is-in');
          io.unobserve(el);
        }
      });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.05 });
    targets.forEach(function (el, i) {
      el.style.transitionDelay = (i % 5) * 0.06 + 's';
      // clipped images never report as visible, so watch the block around them
      io.observe(el.classList.contains('img') ? el.parentElement : el);
    });
  } else {
    targets.forEach(function (el) { el.classList.add('is-in'); });
  }

  // Past events: open flyers full size
  document.querySelectorAll('.lightbox-link').forEach(function (a) {
    a.addEventListener('click', function (e) {
      e.preventDefault();
      var box = document.createElement('div');
      box.className = 'lightbox';
      var img = document.createElement('img');
      img.src = a.href;
      img.alt = a.querySelector('img').alt;
      box.appendChild(img);
      function close() { box.remove(); document.removeEventListener('keydown', onKey); }
      function onKey(ev) { if (ev.key === 'Escape') close(); }
      box.addEventListener('click', close);
      document.addEventListener('keydown', onKey);
      document.body.appendChild(box);
    });
  });
})();
