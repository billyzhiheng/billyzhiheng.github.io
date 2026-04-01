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
    var frame = null;

    function setMoreHref(href) {
      if (!moreLink) return;
      if (href && href !== '#') moreLink.href = href;
    }

    function open() {
      modal.hidden = false;
      modal.setAttribute('aria-hidden', 'false');
      document.documentElement.classList.add('modal-open');

      if (!loaded) {
        loaded = true;
        frame = document.createElement('iframe');
        frame.className = 'visitor-map-frame';
        frame.setAttribute('title', 'Visitor map');
        frame.setAttribute('loading', 'lazy');
        // Keep scripts working but prevent the widget from navigating the top page.
        frame.setAttribute('sandbox', 'allow-scripts allow-same-origin');

        var srcdoc =
          '<!doctype html><html><head><meta charset="utf-8">' +
          '<meta name="viewport" content="width=device-width,initial-scale=1">' +
          '<style>html,body{margin:0;padding:0;background:transparent;}#wrap{display:flex;justify-content:center;}</style>' +
          '</head><body>' +
          '<div id="wrap"><div id="map"></div></div>' +
          '<script>' +
          '(function(){' +
          'function postMore(){try{var a=document.querySelector("a[href*=\\"clustrmaps.com\\"]"); if(a&&a.href){parent.postMessage({type:\\"clustrmaps:more\\", href:a.href}, \\"*\\");}}catch(e){}}' +
          'function softenClickThrough(){' +
          'try{' +
          'var anchors=[].slice.call(document.querySelectorAll("a[href]"));' +
          'anchors.forEach(function(a){' +
          'var href=a.getAttribute("href")||"";' +
          '// Disable the big click-through overlay (traffic link), but keep Leaflet zoom controls clickable.' +
          'if(href.indexOf("clustrmaps.com")!==-1){a.style.pointerEvents="none";}' +
          '});' +
          'var leaflet=document.querySelector(".leaflet-control-container");' +
          'if(leaflet){leaflet.style.pointerEvents="auto"; var zs=leaflet.querySelectorAll("a,button"); zs.forEach(function(el){el.style.pointerEvents="auto";});}' +
          '}catch(e){}' +
          '}' +
          'var mo=new MutationObserver(function(){softenClickThrough(); postMore();});' +
          'mo.observe(document.documentElement,{childList:true,subtree:true});' +
          'window.addEventListener("load",function(){softenClickThrough(); postMore();});' +
          '})();' +
          '</script>' +
          '<script type="text/javascript" id="clustrmaps" src="' +
          CLUSTR_SRC +
          '"></script>' +
          '</body></html>';
        frame.srcdoc = srcdoc;
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

    // Receive "More" link from iframe once the widget injects it.
    window.addEventListener('message', function (e) {
      if (!e || !e.data) return;
      if (e.data.type === 'clustrmaps:more' && typeof e.data.href === 'string') {
        setMoreHref(e.data.href);
      }
    });

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
