/* Procurement CV: browser-language selection with explicit visitor preference.
   Search crawlers can access each canonical language URL without redirect. */
(function () {
  'use strict';
  var path = location.pathname;
  var match = path.match(/^(.*\/procurement-specialist\/)(?:en\/)?(?:index\.html)?$/i);
  if (!match || !/^https?:$/.test(location.protocol)) return;
  var root = match[1];
  var isEnglish = /^en\//i.test(path.slice(root.length));
  var params = new URLSearchParams(location.search);
  var requested = params.get('lang');
  var validManual = requested === 'ar' || requested === 'en';
  var key = 'majd-cv-preferred-language';
  var saved = '';
  try {
    if (validManual) localStorage.setItem(key, requested);
    saved = localStorage.getItem(key) || '';
  } catch (_) {}
  var bot = /googlebot|bingbot|yandexbot|duckduckbot|baiduspider|facebookexternalhit|twitterbot|slackbot|linkedinbot|pinterestbot/i.test(navigator.userAgent || '');
  if (bot && !validManual) return;
  var browserLanguages = navigator.languages && navigator.languages.length ? navigator.languages : [navigator.language || 'en'];
  var detected = /^ar(?:-|$)/i.test(browserLanguages[0] || '') ? 'ar' : 'en';
  var desired = validManual ? requested : ((saved === 'ar' || saved === 'en') ? saved : detected);
  var targetEnglish = desired === 'en';
  var target = root + (targetEnglish ? 'en/' : '');
  if (isEnglish !== targetEnglish) {
    location.replace(target + location.hash);
    return;
  }
  if (validManual) {
    params.delete('lang');
    var query = params.toString();
    var cleanURL = location.pathname + (query ? '?' + query : '') + location.hash;
    try { history.replaceState(null, '', cleanURL); } catch (_) {}
  }
})();