"""Flask web front end for the clothing IR system.

Runs the ClothingIRModel behind a JSON API and serves the browser UI.
Start with:  python webapp.py
Then open:   http://127.0.0.1:5000
"""

import os

from flask import Flask, jsonify, render_template, request

from clothing_ir_model import ClothingIRModel, TEST_QUERIES

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CORPUS_PATH = os.path.join(BASE_DIR, 'corpus_100.txt')

app = Flask(__name__)
ir = ClothingIRModel()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/stats')
def api_stats():
    from collections import Counter as _Counter
    sections = _Counter(d.section for d in ir.documents)
    return jsonify({
        'num_docs': ir.num_docs,
        'num_terms': len(ir.inverted_index),
        'avg_doc_length': round(ir.avg_doc_length, 2),
        'categories': dict(_Counter(d.category for d in ir.documents)),
        'sections': dict(sections),
        'top_idf': [
            {'term': t, 'idf': round(ir.idf[t], 4), 'df': len(ir.inverted_index[t])}
            for t in sorted(ir.idf, key=lambda x: -ir.idf[x])[:20]
        ],
    })


def _filter_by_section(items, section):
    """Keep only documents whose section matches, unless section is ALL/empty."""
    section = (section or 'ALL').upper()
    if section in ('', 'ALL'):
        return items
    return [it for it in items if (it[0].section if isinstance(it, tuple) else it.section) == section]


def _serialize(results, method_label=''):
    """Convert (doc, score) or [doc] results into JSON-safe dictionaries."""
    payload = []
    for i, item in enumerate(results, 1):
        if isinstance(item, tuple):
            doc, score = item
            score_v = round(float(score), 4) if isinstance(score, (int, float)) else score
        else:
            doc = item
            score_v = None
        payload.append({
            'rank': i,
            'doc_id': doc.doc_id,
            'title': doc.title,
            'category': doc.category,
            'section': doc.section,
            'score': score_v,
            'snippet': doc.text[:160] + ('...' if len(doc.text) > 160 else ''),
        })
    return payload


@app.route('/api/search')
def api_search():
    """Ranked search.  method = tfidf|bm25|jaccard|phrase|near|and|or|not """
    query = (request.args.get('q') or '').strip()
    method = (request.args.get('method') or 'tfidf').strip().lower()
    section = (request.args.get('section') or 'ALL').strip()
    top_k = int(request.args.get('top_k', 10))
    if not query:
        return jsonify({'error': 'empty query', 'results': []})

    if method == 'bm25':
        results = ir.bm25_search(query, top_k)
        label = 'BM25'
    elif method == 'jaccard':
        results = ir.jaccard_search(query, top_k)
        label = 'Jaccard'
    elif method == 'phrase':
        result_ids = ir.phrase_search(query, max_gap=1)
        results = [(d, 1.0) for d in result_ids][:top_k]
        label = 'Phrase (exact, in order)'
    elif method == 'near':
        result_ids = ir.phrase_search(query, max_gap=4)
        results = [(d, 1.0) for d in result_ids][:top_k]
        label = 'Proximity (within 4 words)'
    elif method in ('and', 'or', 'not'):
        docs = ir.boolean_search(query, mode=method.upper())
        results = [(d, 0.0) for d in docs][:top_k]
        label = f'Boolean {method.upper()}'
    else:
        results = ir.tfidf_search(query, top_k)
        label = 'TF-IDF Cosine Similarity'

    results = _filter_by_section(results, section)
    ir.query_history.append({'query': query, 'method': method, 'results': len(results)})

    return jsonify({
        'query': query,
        'method': label,
        'section': section or 'ALL',
        'count': len(results),
        'results': _serialize(results),
    })


@app.route('/api/suggest')
def api_suggest():
    """Spelling-corrected search."""
    query = (request.args.get('q') or '').strip()
    section = (request.args.get('section') or 'ALL').strip()
    if not query:
        return jsonify({'error': 'empty query'})
    correction = ir.did_you_mean(query)
    used = correction or query
    results = ir.tfidf_search(used, 10)
    results = _filter_by_section(results, section)
    ir.query_history.append({'query': query, 'method': 'suggest', 'results': len(results)})
    return jsonify({
        'original': query,
        'correction': correction,
        'searched': used,
        'section': section or 'ALL',
        'results': _serialize(results),
    })


@app.route('/api/feedback')
def api_feedback():
    """Pseudo-relevance feedback search."""
    query = (request.args.get('q') or '').strip()
    section = (request.args.get('section') or 'ALL').strip()
    if not query:
        return jsonify({'error': 'empty query'})
    terms = ir.pseudo_relevance_feedback(query)
    expanded = ' '.join(terms)
    results = ir.tfidf_search(expanded, 10)
    results = _filter_by_section(results, section)
    ir.query_history.append({'query': query, 'method': 'feedback', 'results': len(results)})
    return jsonify({
        'query': query,
        'expanded_terms': terms,
        'expanded_query': expanded,
        'section': section or 'ALL',
        'results': _serialize(results),
    })


@app.route('/api/eval')
def api_eval():
    """Run the evaluation across all ranking methods."""
    output = []
    for method in ('tfidf', 'bm25', 'jaccard'):
        result = ir.evaluate_all(TEST_QUERIES, method=method)
        output.append({
            'method': method,
            'map': round(result['map'], 4),
            'mean_ndcg': round(result['mean_ndcg'], 4),
            'avg_precision': round(result['avg_precision'], 4),
            'avg_recall': round(result['avg_recall'], 4),
            'avg_f1': round(result['avg_f1'], 4),
            'per_query': [
                {'query': e['query'], 'precision': round(e['precision'], 4),
                 'recall': round(e['recall'], 4), 'f1': round(e['f1'], 4),
                 'ap': round(e['ap'], 4), 'ndcg': round(e['ndcg'], 4),
                 'relevant': e['relevant_retrieved'], 'total': e['relevant']}
                for e in result['per_query']
            ],
        })
    return jsonify(output)


if __name__ == '__main__':
    ir.load_corpus(CORPUS_PATH)
    ir.build_index()
    print('Clothing IR system loaded:', ir.num_docs, 'documents,',
          len(ir.inverted_index), 'unique terms.')
    print('Open http://127.0.0.1:5000 in your browser.')
    app.run(host='127.0.0.1', port=5000, debug=False)