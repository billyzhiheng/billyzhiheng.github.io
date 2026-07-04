(function () {
  var KEY = 'polyu-matrix-theme';
  function decodeEmail() {
    // Obfuscated char codes to avoid exposing full email in raw HTML.
    var userCodes = [122, 104, 105, 104, 101, 110, 103, 46, 122, 104, 97, 111];
    var domainCodes = [112, 111, 108, 121, 117, 46, 101, 100, 117, 46, 104, 107];
    var user = String.fromCharCode.apply(null, userCodes);
    var domain = String.fromCharCode.apply(null, domainCodes);
    return user + '@' + domain;
  }

  function initProtectedEmails() {
    var email = decodeEmail();
    var links = document.querySelectorAll('a.js-email[data-email="primary"]');
    links.forEach(function (link) {
      link.setAttribute('href', 'mailto:' + email);
      link.textContent = email;
      link.setAttribute('aria-label', 'Send email to ' + email);
    });
  }

  function initVisitorMapModal() {
    var trigger = document.querySelector('[data-visitor-map-trigger]');
    var modal = document.querySelector('[data-visitor-map-modal]');
    var container = document.querySelector('[data-visitor-map-container]');
    if (!trigger || !modal || !container) return;

    var loaded = false;

    function open() {
      modal.hidden = false;
      modal.setAttribute('aria-hidden', 'false');
      document.documentElement.classList.add('modal-open');

      if (!loaded) {
        loaded = true;
        var frame = document.createElement('iframe');
        frame.className = 'visitor-map-frame';
        frame.setAttribute('title', 'Visitor map');
        frame.setAttribute('loading', 'lazy');
        // Use a real page URL (not srcdoc) so the visitor map image loads reliably on GitHub Pages.
        frame.src = 'visitor-map-embed.html';
        container.appendChild(frame);
      }

      try {
        trigger.blur();
      } catch (e) {}
    }

    function close() {
      modal.hidden = true;
      modal.setAttribute('aria-hidden', 'true');
      document.documentElement.classList.remove('modal-open');
    }

    trigger.addEventListener('click', open);

    modal.addEventListener('click', function (e) {
      var el = e.target;
      if (el && el.hasAttribute && el.hasAttribute('data-visitor-map-close')) {
        close();
      }
    });

    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && !modal.hidden) close();
    });
  }

  function getTheme() {
    try {
      return localStorage.getItem(KEY) || 'light';
    } catch (e) {
      return 'light';
    }
  }
  function setTheme(value) {
    try {
      localStorage.setItem(KEY, value);
    } catch (e) {}
    document.documentElement.classList.toggle('dark-mode', value === 'dark');
    var radios = document.querySelectorAll('input[name="color"]');
    radios.forEach(function (r) {
      r.checked = r.value === value;
    });
  }
  function init() {
    initProtectedEmails();
    initVisitorMapModal();
    var theme = getTheme();
    document.documentElement.classList.toggle('dark-mode', theme === 'dark');
    var radios = document.querySelectorAll('input[name="color"]');
    radios.forEach(function (r) {
      r.checked = r.value === theme;
      r.addEventListener('change', function () {
        setTheme(this.value);
      });
    });
  }
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
