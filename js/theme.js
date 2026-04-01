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
      'https://cdn.clustrmaps.com/map_v2.js?cl=ffffff&w=300&t=tt&d=1CBNZi8bKxprKVZkGSt6htJ7dHSEdmLkUldnOU1MJDE&co=2d78ad&cmo=3acc3a&cmn=ff5353&ct=ffffff';
    var loaded = false;
    var frame = null;

    function setMoreHref(href) {
      if (!moreLink) return;
      if (href && href !== '#') {
        moreLink.href = href;
        moreLink.removeAttribute('aria-disabled');
        moreLink.dataset.ready = '1';
      }
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
          'function postMore(){' +
          'try{' +
          'var as=[].slice.call(document.querySelectorAll("a[href]"));' +
          'var pick=null;' +
          'as.forEach(function(a){' +
          'var href=(a.getAttribute("href")||"").trim();' +
          'if(!href||href==="#"||href.indexOf("javascript:")===0) return;' +
          '// Try to find the traffic/details link (usually contains clustrmaps and is not the JS asset).' +
          'var h=(a.href||href).toLowerCase();' +
          'if(h.indexOf("clustrmaps")!==-1 && h.indexOf("map_v2.js")===-1 && h.indexOf(".js")===-1){' +
          'pick=a.href||href;' +
          '}' +
          '});' +
          'if(pick){parent.postMessage({type:"clustrmaps:more", href:pick}, "*");}' +
          '}catch(e){}' +
          '}' +
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

    if (moreLink) {
      moreLink.setAttribute('aria-disabled', 'true');
      moreLink.dataset.ready = '0';
      moreLink.addEventListener('click', function (e) {
        // If we haven't obtained the real traffic link yet, don't jump to "#".
        if (!moreLink.href || moreLink.getAttribute('href') === '#' || moreLink.dataset.ready !== '1') {
          e.preventDefault();
        }
      });
    }

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
