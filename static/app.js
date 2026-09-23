(function () {
  'use strict';

  var queryInput = document.getElementById('queryInput');
  var searchBtn = document.getElementById('searchBtn');
  var exportBtn = document.getElementById('exportBtn');
  var resultsBox = document.getElementById('results');
  var resultsHeader = document.getElementById('resultsHeader');
  var resultsCount = document.getElementById('resultsCount');
  var emptyState = document.getElementById('emptyState');
  var loading = document.getElementById('loading');
  var toolMsg = document.getElementById('toolMsg');
  var sortSelect = document.getElementById('sortSelect');
  var colourFilter = document.getElementById('colourFilter');
  var fabricFilter = document.getElementById('fabricFilter');

  var currentSection = 'MEN';
  var currentCategory = '';
  var lastResults = null;
  var lastQuery = '';

  var FABRICS = { 'cotton': 1, 'linen': 1, 'denim': 1, 'polyester': 1, 'wool': 1, 'woolen': 1, 'silk': 1 };

  // ---------------------------------------------------------------- sections
  var sectButtons = document.querySelectorAll('#sectionTabs .sect');
  sectButtons.forEach(function (btn) {
    btn.addEventListener('click', function () {
      sectButtons.forEach(function (b) { b.classList.remove('active'); });
      btn.classList.add('active');
      currentSection = btn.getAttribute('data-section');
      if (lastQuery) {
        search();
      } else if (currentCategory) {
        browseCategory(currentCategory);
      }
    });
  });

  // ---------------------------------------------------------------- category strip
  var catItems = document.querySelectorAll('.cat-strip .cat-item');
  catItems.forEach(function (item) {
    item.addEventListener('click', function () {
      catItems.forEach(function (c) { c.classList.remove('active'); });
      item.classList.add('active');
      currentCategory = item.getAttribute('data-cat');
      browseCategory(currentCategory);
    });
  });

  // ---------------------------------------------------------------- nav links
  document.querySelectorAll('.nav-link').forEach(function (link) {
    var txt = link.textContent.trim().toLowerCase();
    if (txt === 'men' || txt === 'women' || txt === 'kids') {
      link.addEventListener('click', function () {
        var sec = txt.toUpperCase();
        sectButtons.forEach(function (b) { b.classList.toggle('active', b.getAttribute('data-section') === sec); });
        currentSection = sec;
        if (lastQuery) search(); else if (currentCategory) browseCategory(currentCategory);
      });
    }
  });

  // ---------------------------------------------------------------- sort / filters
  function applySortFilters() {
    if (!lastResults) return;
    var res = lastResults.results.slice();
    var cF = colourFilter.value.toLowerCase();
    var fF = fabricFilter.value.toLowerCase();
    if (cF) res = res.filter(function (r) { return colourName(r).toLowerCase() === cF; });
    if (fF) res = res.filter(function (r) { return fabricName(r).toLowerCase() === fF; });

    var sort = sortSelect.value;
    if (sort === 'colour') {
      res.sort(function (a, b) { return colourName(a).localeCompare(colourName(b)); });
    } else if (sort === 'title') {
      res.sort(function (a, b) { return a.title.localeCompare(b.title); });
    } else {
      res.sort(function (a, b) { return (b.score || 0) - (a.score || 0); });
    }
    res.forEach(function (r, i) { r.rank = i + 1; });
    resultsBox.innerHTML = buildCards(res);
    resultsCount.textContent = res.length + ' items';
  }

  sortSelect.addEventListener('change', applySortFilters);
  colourFilter.addEventListener('change', applySortFilters);
  fabricFilter.addEventListener('change', applySortFilters);

  function colourName(r) {
    var t = r.title.toLowerCase();
    var cols = { 'black': 0, 'grey': 0, 'white': 0, 'navy blue': 0, 'navy': 0, 'blue': 0,
                 'maroon': 0, 'mustard': 0, 'olive green': 0, 'olive': 0, 'green': 0,
                 'pink': 0, 'floral pink': 0, 'floral': 0, 'teal': 0, 'sky blue': 0,
                 'beige': 0, 'yellow': 0, 'purple': 0, 'red': 0, 'wine': 0, 'lavender': 0 };
    for (var c in cols) { if (t.indexOf(c) !== -1) return c; }
    return 'multi';
  }

  function fabricName(r) {
    var t = (r.snippet + ' ' + r.title).toLowerCase();
    for (var f in FABRICS) { if (t.indexOf(f) !== -1) return f; }
    return '';
  }

  // ---------------------------------------------------------------- render
  function buildCards(res) {
    setTimeout(function () { loading.classList.add('hidden'); }, 0);
    var html = '';
    res.forEach(function (r, idx) {
      var col = colourName(r);
      var fab = fabricName(r);
      var imgUrl = '/api/img?category=' + encodeURIComponent(r.category) + '&colour=' + encodeURIComponent(col);
      var chip = '<span class="product-title">' + r.title + '</span>' +
        '<div class="product-meta">[' + r.doc_id + ']' +
        (fab ? ' &middot; <span style="text-transform:capitalize">' + fab + '</span>' : '') +
        ' &middot; <span style="text-transform:capitalize">' + col + '</span></div>' +
        '<div class="product-snippet">' + r.snippet + '</div>' +
        '<div class="product-foot">' +
        '<span class="cat-chip">' + r.category + '</span>' +
        (r.score !== null && r.score !== undefined ? '<span class="score-pill">' + r.score + '</span>' : '') +
        '</div>';
      html +=
        '<div class="product-card">' +
        '<div class="product-img">' +
          '<span class="tag section-' + r.section + '">' + r.section + '</span>' +
          '<img src="' + imgUrl + '" alt="' + r.category + '" loading="lazy">' +
          '<span class="rank-badge">#' + r.rank + '</span>' +
        '</div>' +
        '<div class="product-body">' + chip + '</div>' +
        '</div>';
    });
    return html;
  }

  function renderCards(res) {
    var html = buildCards(res);
    resultsBox.innerHTML = html;
    return res;
  }

  function showState(kind, html) {
    loading.classList.add('hidden');
    if (kind === 'empty') { emptyState.classList.remove('hidden'); resultsBox.innerHTML = ''; }
    else if (kind === 'results') { emptyState.classList.add('hidden'); resultsBox.innerHTML = html; }
  }

  function showMsg(text, isError) {
    toolMsg.textContent = text;
    toolMsg.classList.remove('hidden', 'error');
    if (isError) toolMsg.classList.add('error');
    setTimeout(function () { toolMsg.classList.add('hidden'); }, 5000);
  }

  function fetchJson(url) {
    return fetch(url).then(function (r) { return r.json(); });
  }

  // ---------------------------------------------------------------- search
  function search() {
    var q = queryInput.value.trim();
    if (!q) { browseCategory(currentCategory); return; }
    lastQuery = q;
    currentCategory = '';
    catItems.forEach(function (c) { c.classList.remove('active'); });
    resultsHeader.classList.remove('hidden');
    emptyState.classList.add('hidden');
    loading.classList.remove('hidden');
    var url = '/api/search?method=tfidf&section=' + encodeURIComponent(currentSection) +
              '&q=' + encodeURIComponent(q) + '&category=' + encodeURIComponent('') + '&top_k=24';
    fetchJson(url).then(function (data) {
      if (data.error) { showMsg(data.error, true); return; }
      lastResults = data;
      sortSelect.value = 'relevance';
      resultsHeader.innerHTML = 'Results for <strong>"' + data.query + '"</strong>' +
        '<span class="count-pill">' + data.count + ' products</span>' +
        '<span class="cat-label">' + data.section + '</span>';
      applySortFilters();
    });
  }

  function browseCategory(cat) {
    lastQuery = '';
    resultsHeader.classList.remove('hidden');
    emptyState.classList.add('hidden');
    loading.classList.remove('hidden');
    var url = '/api/search?method=tfidf&section=' + encodeURIComponent(currentSection) +
              '&q=' + encodeURIComponent('') + '&category=' + encodeURIComponent(cat) + '&top_k=24';
    fetchJson(url).then(function (data) {
      if (data.error) { showMsg(data.error, true); return; }
      lastResults = data;
      sortSelect.value = 'relevance';
      resultsHeader.innerHTML = '<span class="cat-label" style="margin:0">' + cat + '</span> &middot; ' + data.section +
        '<span class="count-pill">' + data.count + ' products</span>';
      applySortFilters();
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
    var lines = ['Vastra - ' + lastResults.method + ' Results (' + lastResults.section + ')', '='.repeat(60), ''];
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