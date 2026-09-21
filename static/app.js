(function () {
  'use strict';

  var queryInput = document.getElementById('queryInput');
  var searchBtn = document.getElementById('searchBtn');
  var exportBtn = document.getElementById('exportBtn');
  var resultsBox = document.getElementById('results');
  var resultsHeader = document.getElementById('resultsHeader');
  var emptyState = document.getElementById('emptyState');
  var toolMsg = document.getElementById('toolMsg');
  var correctionBar = document.getElementById('correctionBar');
  var currentSection = 'MEN';
  var lastResults = null;

  // Clothing icon per product type
  var ITEM_ICON = {
    't-shirt': '&#128087;', 'shirt': '&#128087;', 'jeans': '&#128088;',
    'kurta': '&#128087;', 'saree': '&#128094;', 'dress': '&#128087;',
    'hoodie': '&#128087;', 'jacket': '&#129524;', 'leggings': '&#128088;',
    'sweatshirt': '&#128087;'
  };
  var FABRIC_ICON = { 'cotton': '&#10024;', 'linen': '&#10024;', 'denim': '&#10024;',
                      'polyester': '&#10024;', 'wool': '&#10024;', 'silk': '&#10024;', 'woolen': '&#10024;' };

  // soft gradient for the image area
  var GRADS = [
    'linear-gradient(135deg,#eef1ff,#dfe7ff)',
    'linear-gradient(135deg,#ffeef3,#ffe3ec)',
    'linear-gradient(135deg,#eefbf3,#dcf7e8)',
    'linear-gradient(135deg,#fff7e9,#ffeeD2)',
    'linear-gradient(135deg,#f2f0ff,#e9e4ff)'
  ];

  // ---------------------------------------------------------------- sections
  var sectButtons = document.querySelectorAll('#sectionTabs .sect');
  sectButtons.forEach(function (btn) {
    btn.addEventListener('click', function () {
      sectButtons.forEach(function (b) { b.classList.remove('active'); });
      btn.classList.add('active');
      currentSection = btn.getAttribute('data-section');
      if (queryInput.value.trim()) search();
    });
  });

  // ---------------------------------------------------------------- api
  function fetchJson(url) {
    return fetch(url).then(function (r) { return r.json(); });
  }

  // ---------------------------------------------------------------- helpers
  function iconFor(category, text) {
    var key = (category || '').split('-')[0].trim().toLowerCase();
    if (ITEM_ICON[key]) return ITEM_ICON[key];
    var t = (text || '').toLowerCase();
    for (var i in ITEM_ICON) {
      if (t.indexOf(i) !== -1) return ITEM_ICON[i];
    }
    return '&#128717;';
  }

  function colourFrom(text) {
    var t = (text || '').toLowerCase();
    var colours = {
      'black': '#22272e', 'white': '#f4f6f8', 'grey': '#8b939e', 'gray': '#8b939e',
      'navy blue': '#25335a', 'navy': '#25335a', 'blue': '#3d6fd6', 'maroon': '#6e2430',
      'mustard': '#d8a41b', 'olive green': '#6b7343', 'olive': '#6b7343', 'green': '#4c8a4a',
      'pink': '#e78aa4', 'floral pink': '#e78aa4', 'floral': '#d87f9a', 'teal': '#2f8f83',
      'sky blue': '#8fc5ea', 'beige': '#d9c3a0', 'yellow': '#e8c84f', 'purple': '#7d5ba6',
      'red': '#c94f4f', 'wine': '#7a2c3c', 'lavender': '#b9a6d4', 'lavend': '#b9a6d4'
    };
    for (var c in colours) {
      if (t.indexOf(c) !== -1) return { name: c, hex: colours[c] };
    }
    return { name: null, hex: '#93c6e0' };
  }

  function fabricFrom(text) {
    var t = (text || '').toLowerCase();
    for (var f in FABRIC_ICON) {
      if (t.indexOf(f) !== -1) return f.charAt(0).toUpperCase() + f.slice(1);
    }
    return null;
  }

  // ---------------------------------------------------------------- render
  function renderResults(data, label) {
    lastResults = data;
    emptyState.classList.add('hidden');
    if (data.results.length === 0) {
      resultsHeader.innerHTML = 'No matching clothes in <strong>' + data.section + '</strong>';
      resultsBox.innerHTML = '';
      emptyState.classList.remove('hidden');
      emptyState.querySelector('p').textContent = 'No "' + data.query + '" items found in the ' + data.section + ' section.';
      return;
    }
    resultsHeader.innerHTML = data.query
      ? 'Results for <strong>"' + data.query + '"</strong>'
      : 'Results';
    resultsHeader.innerHTML += '<span class="count-pill">' + data.count + ' products</span>';

    var html = '';
    data.results.forEach(function (r, idx) {
      var colour = colourFrom(r.title);
      var fabric = fabricFrom(r.snippet + ' ' + r.title);
      var icon = iconFor(r.category, r.title);
      var grad = GRADS[idx % GRADS.length];
      var swatch = colour.name
        ? '<span class="colour-dot" style="background:' + colour.hex + '"></span> ' + colour.name
        : '';
      html +=
        '<div class="product-card">' +
        '<div class="product-img" style="background:' + grad + '">' +
          '<span class="tag section-' + r.section + '">' + r.section + '</span>' +
          '<span class="rank-badge">#' + r.rank + '</span>' +
          '<span>' + icon + '</span>' +
        '</div>' +
        '<div class="product-body">' +
          '<div class="product-title">' + r.title + '</div>' +
          '<div class="product-meta">[' + r.doc_id + ']' + (fabric ? ' &middot; ' + fabric : '') + (swatch ? ' &middot; ' + swatch : '') + '</div>' +
          '<div class="product-snippet">' + r.snippet + '</div>' +
          '<div class="product-foot">' +
            '<span class="cat-chip">' + r.category + '</span>' +
            (r.score !== null && r.score !== undefined ? '<span class="score-pill">' + r.score + '</span>' : '') +
          '</div>' +
        '</div>' +
        '</div>';
    });
    resultsBox.innerHTML = html;
  }

  function showMsg(text, isError) {
    toolMsg.textContent = text;
    toolMsg.classList.remove('hidden', 'error');
    if (isError) toolMsg.classList.add('error');
    setTimeout(function () { toolMsg.classList.add('hidden'); }, 5000);
  }

  function hideMsg() { toolMsg.classList.add('hidden'); }

  // ---------------------------------------------------------------- search
  function search() {
    var q = queryInput.value.trim();
    if (!q) return;
    hideMsg();
    correctionBar.classList.add('hidden');
    emptyState.classList.add('hidden');
    var url = '/api/search?method=tfidf&section=' + encodeURIComponent(currentSection) +
            '&q=' + encodeURIComponent(q);
    fetchJson(url).then(function (data) {
      if (data.error) { showMsg(data.error, true); return; }
      renderResults(data, data.method);
    });
  }

  searchBtn.addEventListener('click', search);
  queryInput.addEventListener('keydown', function (e) { if (e.key === 'Enter') search(); });

  // ---------------------------------------------------------------- export
  exportBtn.addEventListener('click', function () {
    if (!lastResults || lastResults.results.length === 0) {
      showMsg('Nothing to export yet - run a search first.', true);
      return;
    }
    var lines = ['ClothiQ - ' + lastResults.method + ' Results (' + lastResults.section + ')', '='.repeat(60), ''];
    lastResults.results.forEach(function (r) {
      lines.push('Rank ' + r.rank + ': [' + r.doc_id + '] ' + r.title);
      lines.push('  Category: ' + r.category + '   Score: ' + r.score);
      lines.push('  ' + r.snippet);
      lines.push('');
    });
    var blob = new Blob([lines.join('\n')], { type: 'text/plain' });
    var a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = 'results_output.txt';
    a.click();
    URL.revokeObjectURL(a.href);
    showMsg('Exported ' + lastResults.results.length + ' results to results_output.txt');
  });
})();