(function () {
  'use strict';

  var queryInput = document.getElementById('queryInput');
  var searchBtn = document.getElementById('searchBtn');
  var exportBtn = document.getElementById('exportBtn');
  var resultsBox = document.getElementById('results');
  var resultsHeader = document.getElementById('resultsHeader');
  var toolMsg = document.getElementById('toolMsg');
  var correctionBar = document.getElementById('correctionBar');
  var currentMethod = 'tfidf';
  var lastResults = null;

  // ---------------------------------------------------------------- tabs
  var tabs = document.querySelectorAll('#methodTabs .tab');
  tabs.forEach(function (tab) {
    tab.addEventListener('click', function () {
      tabs.forEach(function (t) { t.classList.remove('active'); });
      tab.classList.add('active');
      currentMethod = tab.getAttribute('data-method');
      if (queryInput.value.trim()) search();
    });
  });

  // ---------------------------------------------------------------- api
  function fetchJson(url) {
    return fetch(url).then(function (r) { return r.json(); });
  }

  // ---------------------------------------------------------------- render
  function renderResults(data, label) {
    lastResults = data;
    if (data.results.length === 0) {
      resultsHeader.innerHTML = '<strong>' + label + '</strong> &middot; no documents matched the query.';
      resultsBox.innerHTML = '<div class="no-results">No results. Try fewer words, the "Spell check" tool, or another method.</div>';
      return;
    }
    resultsHeader.innerHTML = '<strong>' + data.method + '</strong> &middot; ' + data.count + ' results';
    var html = '';
    data.results.forEach(function (r) {
      html +=
        '<div class="result-card">' +
        '<div class="title"><span class="rk">' + r.rank + '</span>' + r.title + '</div>' +
        '<div class="meta">[' + r.doc_id + '] &nbsp;<span class="cat">' + r.category + '</span> &nbsp; score ' + r.score + '</div>' +
        '<div class="snippet">' + r.snippet + '</div>' +
        '</div>';
    });
    resultsBox.innerHTML = html;
  }

  function renderCorrection(correction, searched) {
    if (correction && correction !== searched) {
      correctionBar.innerHTML =
        'Did you mean: <a id="useCorrection">"' + correction + '"</a>  (searching the corrected query)';
      correctionBar.classList.remove('hidden');
      document.getElementById('useCorrection').addEventListener('click', function () {
        queryInput.value = correction;
        search();
      });
    } else {
      correctionBar.innerHTML = 'No spelling correction needed for this query.';
      correctionBar.classList.remove('hidden');
    }
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
    var url = '/api/search?method=' + currentMethod + '&q=' + encodeURIComponent(q);
    fetchJson(url).then(function (data) {
      if (data.error) { showMsg(data.error, true); return; }
      renderResults(data, data.method);
    });
  }

  searchBtn.addEventListener('click', search);
  queryInput.addEventListener('keydown', function (e) { if (e.key === 'Enter') search(); });

  // ---------------------------------------------------------------- tools
  document.querySelectorAll('.tool-btn').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var q = queryInput.value.trim();
      var tool = btn.getAttribute('data-tool');
      if (tool === 'eval') { runEval(); return; }
      if (!q) { showMsg('Type a query first.', true); return; }

      if (tool === 'suggest') {
        fetchJson('/api/suggest?q=' + encodeURIComponent(q)).then(function (data) {
          if (data.error) { showMsg(data.error, true); return; }
          renderCorrection(data.correction, data.searched);
          renderResults(data, 'Spelling-corrected');
          showMsg('Searched: "' + data.searched + '"');
        });
      } else if (tool === 'feedback') {
        fetchJson('/api/feedback?q=' + encodeURIComponent(q)).then(function (data) {
          if (data.error) { showMsg(data.error, true); return; }
          renderResults(data, 'Pseudo-Relevance Feedback');
          showMsg('Expanded with terms: ' + data.expanded_terms.join(', '));
        });
      }
    });
  });

  function runEval() {
    hideMsg();
    correctionBar.classList.add('hidden');
    fetchJson('/api/eval').then(function (data) {
      var html = '<div class="results-header"><strong>Evaluation on the 5 benchmark queries</strong> &middot; gold relevance = 10 documents per query</div>';
      data.forEach(function (m) {
        html += '<table class="eval-table"><thead><tr><th>Method</th><th>MAP</th><th>Mean NDCG</th><th>Per-query (P/R/F1/AP/NDCG)</th></tr></thead><tbody>';
        html += '<tr><td><strong>' + m.method.toUpperCase() + '</strong></td>' +
          '<td class="' + (m.map >= 0.99 ? 'perfect' : 'weak') + '">' + m.map + '</td>' +
          '<td class="' + (m.mean_ndcg >= 0.99 ? 'perfect' : 'weak') + '">' + m.mean_ndcg + '</td><td>';
        m.per_query.forEach(function (e) {
          html += '<em>"' + e.query + '"</em>: P=' + e.precision + ' R=' + e.recall + ' F1=' + e.f1 +
            ' AP=' + e.ap + ' NDCG=' + e.ndcg + ' (' + e.relevant + '/' + e.total + ' rel) &nbsp;';
        });
        html += '</td></tr></tbody></table>';
      });
      lastResults = null;
      resultsHeader.innerHTML = '';
      resultsBox.innerHTML = html;
    });
  }

  // ---------------------------------------------------------------- export
  exportBtn.addEventListener('click', function () {
    if (!lastResults || lastResults.results.length === 0) {
      showMsg('Nothing to export yet - run a search first.', true);
      return;
    }
    var lines = ['Clothing IR System - ' + lastResults.method + ' Results', '='.repeat(60), ''];
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

  // ---------------------------------------------------------------- stats
  fetchJson('/api/stats').then(function (s) {
    var row = document.getElementById('statsRow');
    row.innerHTML =
      card(s.num_docs, 'Documents') +
      card(s.num_terms, 'Unique terms') +
      card(s.avg_doc_length, 'Avg doc length') +
      card(countCats(s.categories), 'Categories');
  });

  function card(num, lbl) {
    return '<div class="stat-card"><div class="num">' + num + '</div><div class="lbl">' + lbl + '</div></div>';
  }
  function countCats(c) { return Object.keys(c || {}).length; }
})();