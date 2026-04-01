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
    var moreLink = document.querySelector('[data-visitor-map-more]');
    if (!trigger || !modal || !container) return;

    var CLUSTR_SRC =
      'https://clustrmaps.com/map_v2.js?d=1CBNZi8bKxprKVZkGSt6htJ7dHSEdmLkUldnOU1MJDE&cl=ffffff&w=a';
    var loaded = false;

    function syncMoreLinkHref() {
      if (!moreLink) return;
      // ClustrMaps usually wraps the map with an <a href="...traffic...">...</a>.
      var a = container.querySelector('a[href]');
      if (a && a.href) {
        moreLink.href = a.href;
        moreLink.removeAttribute('aria-disabled');
      }
    }

    function open() {
      modal.hidden = false;
      modal.setAttribute('aria-hidden', 'false');
      document.documentElement.classList.add('modal-open');

      if (!loaded) {
        loaded = true;
        var script = document.createElement('script');
        script.type = 'text/javascript';
        script.id = 'clustrmaps';
        script.async = true;
        script.src = CLUSTR_SRC;
        container.appendChild(script);

        // Wait for ClustrMaps to inject DOM, then wire up "More".
        var tries = 0;
        var timer = setInterval(function () {
          tries += 1;
          syncMoreLinkHref();
          if ((moreLink && moreLink.href && moreLink.href !== '#') || tries >= 40) {
            clearInterval(timer);
          }
        }, 250);
      } else {
        syncMoreLinkHref();
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

    // Prevent the embedded map's default click-to-traffic navigation,
    // while still allowing the map's internal UI (zoom buttons, drag, etc).
    container.addEventListener(
      'click',
      function (e) {
        var target = e.target;
        if (!target) return;
        var a = target.closest ? target.closest('a[href]') : null;
        if (a && container.contains(a)) {
          e.preventDefault();
        }
      },
      true
    );

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
