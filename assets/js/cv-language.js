/* CV language preference: keep each canonical URL directly accessible.
 * Use browser language only to offer an optional switch; never force a redirect.
 */
(function () {
  'use strict';
  if (!/^https?:$/.test(location.protocol)) return;
  var match = location.pathname.match(/^(.*\/procurement-specialist\/)(?:en\/)?(?:index\.html)?$/i);
  if (!match) return;
  var root = match[1];
  var current = /^en\//i.test(location.pathname.slice(root.length)) ? 'en' : 'ar';
  var query = new URLSearchParams(location.search);
  var manual = query.get('lang');
  var explicit = manual === 'ar' || manual === 'en';
  var key = 'majd-cv-preferred-language';
  var preferred = '';
  try {
    if (explicit) localStorage.setItem(key, manual);
    preferred = localStorage.getItem(key) || '';
  } catch (_) {}
  if (explicit) {
    query.delete('lang');
    var clean = location.pathname + (query.toString() ? '?' + query.toString() : '') + location.hash;
    try { history.replaceState(null, '', clean); } catch (_) {}
  }
  var langs = navigator.languages && navigator.languages.length ? navigator.languages : [navigator.language || 'en'];
  var detected = /^ar(?:-|$)/i.test(langs[0] || '') ? 'ar' : 'en';
  var desired = (preferred === 'ar' || preferred === 'en') ? preferred : detected;
  if (desired === current || explicit) return;
  function displayNotice() {
    var notice = document.getElementById('cv-language-notice');
    if (!notice) return;
    var dismissedKey = 'majd-cv-lang-dismissed-' + current + '-' + desired;
    try { if (sessionStorage.getItem(dismissedKey) === '1') return; } catch (_) {}
    var target = root + (desired === 'en' ? 'en/' : '') + '?lang=' + desired;
    var link = notice.querySelector('a[data-cv-language-link]');
    var close = notice.querySelector('button[data-cv-language-dismiss]');
    if (!link || !close) return;
    link.href = target;
    notice.hidden = false;
    close.addEventListener('click', function () {
      notice.hidden = true;
      try { sessionStorage.setItem(dismissedKey, '1'); } catch (_) {}
    });
  }
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', displayNotice, {once:true});
  } else {
    displayNotice();
  }
})();