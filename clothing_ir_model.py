"""A small clothing-product information retrieval system.

The module parses the XML-like corpus, builds an inverted index, a positional
index, and TF-IDF vectors, and exposes TF-IDF, BM25, Boolean, Jaccard, phrase,
proximity, and query-expansion searches.  Includes Porter stemming,
precision/recall/F1 evaluation, and a query-history log.  Run the file directly
to start the interactive CLI.
"""

import re
import math
import os
from collections import defaultdict, Counter
from dataclasses import dataclass, field


# ---------------------------------------------------------------------------
#  Porter Stemmer  (self-contained, no external dependencies)
# ---------------------------------------------------------------------------

class PorterStemmer:
    """Minimal Porter stemming implementation for English search terms."""

    VOWELS = set('aeiou')

    def stem(self, word: str) -> str:
        if len(word) <= 2:
            return word
        word = self._step1a(word)
        word = self._step1b(word)
        word = self._step1c(word)
        word = self._step2(word)
        word = self._step3(word)
        word = self._step4(word)
        return word

    @staticmethod
    def _measure(stem: str) -> int:
        cv = re.sub(r'[^aeiou]', '', stem)
        return len(cv)

    def _ends_double_consonant(self, word: str) -> bool:
        return len(word) >= 2 and word[-1] == word[-2] and word[-1] not in self.VOWELS

    @staticmethod
    def _ends_cvc(word: str) -> bool:
        if len(word) < 3:
            return False
        c1, v, c2 = word[-3], word[-2], word[-1]
        if c1 in 'aeiou' or v not in 'aeiou' or c2 in 'aeiouwxy':
            return False
        return True

    @staticmethod
    def _replace_end(word: str, suffix: str, replacement: str) -> str:
        if word.endswith(suffix):
            return word[:-len(suffix)] + replacement
        return word

    def _step1a(self, word: str) -> str:
        for old, new in [('sses', 'ss'), ('ies', 'i'), ('ss', 'ss'), ('s', '')]:
            if word.endswith(old):
                return word[:-len(old)] + new
        return word

    def _step1b(self, word: str) -> str:
        for s in ('eed', 'ed', 'ing'):
            if word.endswith(s):
                stem = word[:-len(s)]
                if s == 'eed':
                    if self._measure(stem) > 0:
                        return stem + 'ee'
                    return word
                if any(ch in self.VOWELS for ch in stem):
                    if s == 'ed':
                        if self._ends_double_consonant(stem) and stem[-1] not in 'lsz':
                            stem = stem[:-1]
                    word = stem
                    for suffix in ('at', 'bl', 'iz'):
                        if word.endswith(suffix):
                            return word + 'e'
                    if self._ends_double_consonant(word) and word[-1] not in 'lsz':
                        return word[:-1]
                    if self._measure(word) == 1 and self._ends_cvc(word):
                        return word + 'e'
                    return word
        return word

    def _step1c(self, word: str) -> str:
        if word.endswith('y'):
            stem = word[:-1]
            if any(ch in self.VOWELS for ch in stem):
                return stem + 'i'
        return word

    def _step2(self, word: str) -> str:
        pairs = [
            ('ational', 'ate'), ('tional', 'tion'), ('enci', 'ence'),
            ('anci', 'ance'), ('izer', 'ize'), ('abli', 'able'),
            ('alli', 'al'), ('entli', 'ent'), ('eli', 'e'),
            ('ousli', 'ous'), ('ization', 'ize'), ('ation', 'ate'),
            ('ator', 'ate'), ('alism', 'al'), ('iveness', 'ive'),
            ('fulness', 'ful'), ('ousness', 'ous'), ('aliti', 'al'),
            ('iviti', 'ive'), ('biliti', 'ble'), ('logi', 'log'),
        ]
        for s, r in pairs:
            if word.endswith(s):
                stem = word[:-len(s)]
                if self._measure(stem) > 0:
                    return stem + r
        return word

    def _step3(self, word: str) -> str:
        pairs = [
            ('icate', 'ic'), ('ative', ''), ('alize', 'al'),
            ('iciti', 'ic'), ('ical', 'ic'), ('ful', ''), ('ness', ''),
        ]
        for s, r in pairs:
            if word.endswith(s):
                stem = word[:-len(s)]
                if self._measure(stem) > 0:
                    return stem + r
        return word

    def _step4(self, word: str) -> str:
        suffixes = [
            'al', 'ance', 'ence', 'er', 'ic', 'able', 'ible',
            'ant', 'ement', 'ment', 'ent', 'ion', 'ou', 'ism',
            'ate', 'iti', 'ous', 'ive', 'ize',
        ]
        for s in suffixes:
            if word.endswith(s):
                stem = word[:-len(s)]
                if s == 'ion':
                    if stem and stem[-1] in 'st' and self._measure(stem) > 1:
                        return stem
                elif self._measure(stem) > 1:
                    return stem
        return word


# ---------------------------------------------------------------------------
#  Data structures
# ---------------------------------------------------------------------------

@dataclass
class Document:
    """A corpus document and the terms/vectors generated during indexing."""

    doc_id: str
    category: str
    title: str
    text: str
    terms: list = field(default_factory=list)
    tf: dict = field(default_factory=dict)
    tfidf: dict = field(default_factory=dict)


# ---------------------------------------------------------------------------
#  Main IR model
# ---------------------------------------------------------------------------

class ClothingIRModel:
    """Index clothing documents and retrieve them with several IR methods."""

    def __init__(self):
        self.documents: list[Document] = []
        self.inverted_index: dict[str, set] = defaultdict(set)
        self.positional_index: dict[str, dict[str, list[int]]] = defaultdict(dict)
        self.idf: dict[str, float] = {}
        self.doc_vectors: dict[str, dict] = {}
        self.doc_lengths: dict[str, int] = {}
        self.avg_doc_length: float = 0.0
        self.num_docs: int = 0
        self.stemmer = PorterStemmer()
        self.query_history: list[dict] = []

    # -- corpus / index ---------------------------------------------------

    def load_corpus(self, filepath: str) -> None:
        """Parse corpus records from *filepath* and store them as documents."""
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        pattern = re.compile(
            r'<DOC>\s*'
            r'<DOCID>(.*?)</DOCID>\s*'
            r'<CATEGORY>(.*?)</CATEGORY>\s*'
            r'<TITLE>(.*?)</TITLE>\s*'
            r'<TEXT>(.*?)</TEXT>\s*'
            r'</DOC>',
            re.DOTALL
        )

        for match in pattern.finditer(content):
            doc = Document(
                doc_id=match.group(1).strip(),
                category=match.group(2).strip(),
                title=match.group(3).strip(),
                text=match.group(4).strip()
            )
            self.documents.append(doc)

        self.num_docs = len(self.documents)
        print(f"Loaded {self.num_docs} documents from corpus.")

    def tokenize(self, text: str) -> list[str]:
        """Normalize, remove stop-words, and stem tokens."""
        text = text.lower()
        text = re.sub(r"[^a-z0-9\s'-]", " ", text)
        tokens = text.split()
        stop_words = {
            'the', 'is', 'it', 'this', 'that', 'a', 'an', 'and', 'or', 'but',
            'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from', 'as',
            'has', 'have', 'had', 'was', 'were', 'be', 'been', 'being', 'are',
            'not', 'no', 'do', 'does', 'did', 'will', 'would', 'could', 'should',
            'may', 'might', 'shall', 'can', 'need', 'dare', 'ought', 'used',
            'its', 'their', 'his', 'her', 'my', 'your', 'our', 'they', 'them',
            'he', 'she', 'we', 'you', 'i', 'me', 'him', 'us', 'who', 'which',
            'what', 'when', 'where', 'how', 'all', 'each', 'every', 'both',
            'few', 'more', 'most', 'other', 'some', 'such', 'than', 'too',
            'very', 'just', 'about', 'above', 'after', 'again', 'also', 'any',
            'because', 'before', 'below', 'between', 'into', 'through', 'during',
            'out', 'off', 'over', 'under', 'only', 'own', 'same', 'so', 'then',
            'there', 'here', 'these', 'those', 'am', 'if', 'up', 'down',
        }
        result = []
        for t in tokens:
            if t not in stop_words and len(t) > 1:
                result.append(self.stemmer.stem(t))
        return result

    def build_index(self) -> None:
        """Build the inverted index, positional index, IDFs and document vectors."""
        for doc in self.documents:
            combined_text = f"{doc.title} {doc.text}"
            doc.terms = self.tokenize(combined_text)
            tf = Counter(doc.terms)
            max_freq = max(tf.values()) if tf else 1
            doc.tf = {term: count / max_freq for term, count in tf.items()}
            self.doc_lengths[doc.doc_id] = len(doc.terms)
            for term in set(doc.terms):
                self.inverted_index[term].add(doc.doc_id)
            for position, term in enumerate(doc.terms):
                self.positional_index[term].setdefault(doc.doc_id, []).append(position)

        self.avg_doc_length = (
            sum(self.doc_lengths.values()) / self.num_docs if self.num_docs else 0
        )

        for term, doc_ids in self.inverted_index.items():
            df = len(doc_ids)
            self.idf[term] = math.log((self.num_docs - df + 0.5) / (df + 0.5) + 1)

        for doc in self.documents:
            doc.tfidf = {
                term: tf_val * self.idf.get(term, 0)
                for term, tf_val in doc.tf.items()
            }
            norm = math.sqrt(sum(v ** 2 for v in doc.tfidf.values()))
            if norm > 0:
                doc.tfidf = {k: v / norm for k, v in doc.tfidf.items()}
            self.doc_vectors[doc.doc_id] = doc.tfidf

        print(f"Index built: {len(self.inverted_index)} unique terms.")

    # -- scoring helpers --------------------------------------------------

    def cosine_similarity(self, query_vec: dict, doc_id: str) -> float:
        """Return cosine similarity between a query vector and one document."""
        doc_vec = self.doc_vectors.get(doc_id, {})
        common = set(query_vec.keys()) & set(doc_vec.keys())
        if not common:
            return 0.0
        dot = sum(query_vec[t] * doc_vec[t] for t in common)
        q_norm = math.sqrt(sum(v ** 2 for v in query_vec.values()))
        d_norm = math.sqrt(sum(v ** 2 for v in doc_vec.values()))
        if q_norm == 0 or d_norm == 0:
            return 0.0
        return dot / (q_norm * d_norm)

    def bm25_score(self, query_terms: list[str], doc_id: str,
                   k1: float = 1.5, b: float = 0.75) -> float:
        """Calculate BM25 relevance for one document and a tokenized query."""
        score = 0.0
        doc = next((d for d in self.documents if d.doc_id == doc_id), None)
        if not doc:
            return 0.0
        doc_len = self.doc_lengths.get(doc_id, 0)
        term_freq = Counter(doc.terms)
        for term in query_terms:
            if term not in self.inverted_index:
                continue
            df = len(self.inverted_index[term])
            idf = math.log((self.num_docs - df + 0.5) / (df + 0.5) + 1)
            tf = term_freq.get(term, 0)
            numerator = tf * (k1 + 1)
            denominator = tf + k1 * (1 - b + b * doc_len / self.avg_doc_length)
            score += idf * (numerator / denominator)
        return score

    def jaccard_similarity(self, query_terms: list[str], doc_id: str) -> float:
        """Jaccard similarity between the query term set and document term set."""
        doc = next((d for d in self.documents if d.doc_id == doc_id), None)
        if not doc:
            return 0.0
        q_set = set(query_terms)
        d_set = set(doc.terms)
        intersection = q_set & d_set
        union = q_set | d_set
        if not union:
            return 0.0
        return len(intersection) / len(union)

    # -- search methods ---------------------------------------------------

    def boolean_search(self, query: str, mode: str = 'AND') -> list[Document]:
        """Return documents matching query terms with AND, OR, or NOT logic."""
        query_terms = self.tokenize(query)
        if not query_terms:
            return []

        result_sets = []
        for term in query_terms:
            if term in self.inverted_index:
                result_sets.append(self.inverted_index[term])
            else:
                result_sets.append(set())

        if mode == 'AND':
            result_ids = set.intersection(*result_sets) if result_sets else set()
        elif mode == 'OR':
            result_ids = set.union(*result_sets) if result_sets else set()
        elif mode == 'NOT':
            if len(result_sets) >= 2:
                result_ids = result_sets[0] - set.union(*result_sets[1:])
            else:
                all_ids = {d.doc_id for d in self.documents}
                result_ids = all_ids - result_sets[0]
        else:
            result_ids = set.intersection(*result_sets) if result_sets else set()

        return [d for d in self.documents if d.doc_id in result_ids]

    def tfidf_search(self, query: str, top_k: int = 10) -> list[tuple[Document, float]]:
        """Rank documents by cosine similarity in the TF-IDF vector space."""
        query_terms = self.tokenize(query)
        if not query_terms:
            return []

        tf_query = Counter(query_terms)
        max_freq = max(tf_query.values()) if tf_query else 1
        query_vec = {}
        for term, count in tf_query.items():
            tf_val = count / max_freq
            idf_val = self.idf.get(term, 0)
            query_vec[term] = tf_val * idf_val

        norm = math.sqrt(sum(v ** 2 for v in query_vec.values()))
        if norm > 0:
            query_vec = {k: v / norm for k, v in query_vec.items()}

        candidate_ids = set()
        for term in query_terms:
            candidate_ids.update(self.inverted_index.get(term, set()))

        scored = []
        for doc_id in candidate_ids:
            sim = self.cosine_similarity(query_vec, doc_id)
            if sim > 0:
                doc = next(d for d in self.documents if d.doc_id == doc_id)
                scored.append((doc, sim))

        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:top_k]

    def bm25_search(self, query: str, top_k: int = 10) -> list[tuple[Document, float]]:
        """Rank documents using BM25 and return at most *top_k* results."""
        query_terms = self.tokenize(query)
        if not query_terms:
            return []

        candidate_ids = set()
        for term in query_terms:
            candidate_ids.update(self.inverted_index.get(term, set()))

        scored = []
        for doc_id in candidate_ids:
            score = self.bm25_score(query_terms, doc_id)
            if score > 0:
                doc = next(d for d in self.documents if d.doc_id == doc_id)
                scored.append((doc, score))

        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:top_k]

    def jaccard_search(self, query: str, top_k: int = 10) -> list[tuple[Document, float]]:
        """Rank documents using Jaccard set similarity."""
        query_terms = self.tokenize(query)
        if not query_terms:
            return []

        candidate_ids = set()
        for term in query_terms:
            candidate_ids.update(self.inverted_index.get(term, set()))

        scored = []
        for doc_id in candidate_ids:
            sim = self.jaccard_similarity(query_terms, doc_id)
            if sim > 0:
                doc = next(d for d in self.documents if d.doc_id == doc_id)
                scored.append((doc, sim))

        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:top_k]

    def query_expansion(self, query: str) -> list[str]:
        """Add strongly co-occurring terms to a query for broader retrieval."""
        query_terms = self.tokenize(query)
        expanded = list(query_terms)
        for term in query_terms:
            if term in self.inverted_index:
                related = set()
                for doc_id in self.inverted_index[term]:
                    doc = next(d for d in self.documents if d.doc_id == doc_id)
                    for t in set(doc.terms) - {term}:
                        co_occur = len(
                            self.inverted_index[term] & self.inverted_index.get(t, set())
                        )
                        if co_occur >= 3:
                            related.add(t)
                for r in list(related)[:2]:
                    if r not in expanded:
                        expanded.append(r)
        return expanded

    # -- positional / phrase search ----------------------------------------

    @staticmethod
    def _find_phrase(posting_lists: list[list[int]], max_gap: int = 1) -> bool:
        """Check whether terms occur with in-order gaps of at most *max_gap*.

        Given one sorted position list per query term, scans position lists in
        order.  A match exists when each term appears to the right of the
        previous one and never by more than *max_gap* positions.

        *max_gap*=1 means the terms must be adjacent (phrase match);
        larger values allow words in between (proximity match).
        """
        if not posting_lists:
            return False
        ptrs = [0] * len(posting_lists)
        while True:
            current_pos = posting_lists[0][ptrs[0]]
            valid = True
            for i in range(1, len(posting_lists)):
                lst = posting_lists[i]
                while ptrs[i] < len(lst) and lst[ptrs[i]] <= current_pos:
                    ptrs[i] += 1
                if ptrs[i] >= len(lst):
                    return False
                if lst[ptrs[i]] - current_pos > max_gap:
                    valid = False
                current_pos = lst[ptrs[i]]
            if valid:
                return True
            ptrs[0] += 1
            if ptrs[0] >= len(posting_lists[0]):
                return False

    def phrase_search(self, query: str, max_gap: int = 1) -> list[Document]:
        """Return documents where query terms appear in order within *max_gap*.

        *max_gap*=1 (default) is exact phrase matching; higher values allow
        intervening terms so the query behaves like a proximity search.
        """
        query_terms = self.tokenize(query)
        if len(query_terms) < 2:
            return []

        common_ids = None
        for term in query_terms:
            doc_ids = set(self.inverted_index.get(term, set()))
            common_ids = doc_ids if common_ids is None else common_ids & doc_ids
        if not common_ids:
            return []

        matches = []
        for doc_id in sorted(common_ids):
            positions = [
                self.positional_index[term].get(doc_id, [])
                for term in query_terms
            ]
            if any(not p for p in positions):
                continue
            if self._find_phrase(positions, max_gap=max_gap):
                doc = next(d for d in self.documents if d.doc_id == doc_id)
                matches.append(doc)
        return matches

    def phrase_search_ranked(self, query: str, top_k: int = 10) -> list[tuple[Document, float]]:
        """Phrase search ranked by how many distinct term pairs match the window.

        Documents with the phrase are ranked first; ties broken by TF-IDF score.
        """
        query_terms = self.tokenize(query)
        if len(query_terms) < 2:
            return []

        phrase_docs = {d.doc_id for d in self.phrase_search(query, max_gap=1)}
        proximity_docs = {d.doc_id for d in self.phrase_search(query, max_gap=4)}

        scored = []
        for doc_id in phrase_docs:
            doc = next(d for d in self.documents if d.doc_id == doc_id)
            base = self.cosine_similarity(
                self._query_vector(query_terms), doc_id
            )
            scored.append((doc, 2.0 + base))
        for doc_id in proximity_docs - phrase_docs:
            doc = next(d for d in self.documents if d.doc_id == doc_id)
            base = self.cosine_similarity(
                self._query_vector(query_terms), doc_id
            )
            scored.append((doc, 1.0 + base))

        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:top_k]

    def _query_vector(self, query_terms: list[str]) -> dict:
        """Build an L2-normalized TF-IDF query vector from already-token terms."""
        tf_query = Counter(query_terms)
        max_freq = max(tf_query.values()) if tf_query else 1
        qvec = {t: (c / max_freq) * self.idf.get(t, 0) for t, c in tf_query.items()}
        norm = math.sqrt(sum(v ** 2 for v in qvec.values()))
        if norm > 0:
            qvec = {k: v / norm for k, v in qvec.items()}
        return qvec

    # -- evaluation -------------------------------------------------------

    def evaluate(self, query: str, relevant_doc_ids: set[str],
                 method: str = 'tfidf', top_k: int = 10) -> dict:
        """Compute precision, recall, and F1 for a single query.

        Parameters
        ----------
        query : str
            The text query.
        relevant_doc_ids : set[str]
            The ground-truth document IDs considered relevant.
        method : str
            One of 'tfidf', 'bm25', 'jaccard'.
        top_k : int
            Number of top results to evaluate.
        """
        if method == 'bm25':
            results = self.bm25_search(query, top_k)
        elif method == 'jaccard':
            results = self.jaccard_search(query, top_k)
        else:
            results = self.tfidf_search(query, top_k)

        retrieved_ids = {doc.doc_id for doc, _ in results}
        relevant_retrieved = retrieved_ids & relevant_doc_ids

        precision = len(relevant_retrieved) / len(retrieved_ids) if retrieved_ids else 0.0
        recall = len(relevant_retrieved) / len(relevant_doc_ids) if relevant_doc_ids else 0.0
        f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0

        return {
            'query': query,
            'method': method,
            'retrieved': len(retrieved_ids),
            'relevant': len(relevant_doc_ids),
            'relevant_retrieved': len(relevant_retrieved),
            'precision': precision,
            'recall': recall,
            'f1': f1,
        }

    def evaluate_all(self, test_queries: list[tuple[str, set[str]]],
                     method: str = 'tfidf', top_k: int = 10) -> dict:
        """Run evaluation across multiple queries and return aggregated metrics."""
        evals = []
        for query, relevant_ids in test_queries:
            result = self.evaluate(query, relevant_ids, method, top_k)
            evals.append(result)

        avg_p = sum(e['precision'] for e in evals) / len(evals) if evals else 0
        avg_r = sum(e['recall'] for e in evals) / len(evals) if evals else 0
        avg_f1 = sum(e['f1'] for e in evals) / len(evals) if evals else 0

        return {
            'method': method,
            'num_queries': len(evals),
            'avg_precision': avg_p,
            'avg_recall': avg_r,
            'avg_f1': avg_f1,
            'per_query': evals,
        }

    # -- display ----------------------------------------------------------

    def print_results(self, results: list[tuple[Document, float]], method: str = "TF-IDF") -> None:
        """Print ranked results with their score and a short text snippet."""
        if not results:
            print("  No results found.")
            return
        print(f"\n{'='*75}")
        print(f"  {method} Ranked Results ({len(results)} documents)")
        print(f"{'='*75}")
        for rank, (doc, score) in enumerate(results, 1):
            print(f"\n  Rank {rank}: [{doc.doc_id}] {doc.title}")
            print(f"  Category : {doc.category}")
            print(f"  Score    : {score:.6f}")
            snippet = doc.text[:120] + "..." if len(doc.text) > 120 else doc.text
            print(f"  Snippet  : {snippet}")
        print(f"\n{'='*75}")

    def print_boolean_results(self, results: list[Document]) -> None:
        """Print the unranked results returned by a Boolean query."""
        if not results:
            print("  No results found.")
            return
        print(f"\n  Boolean Search Results: {len(results)} documents found")
        print(f"  {'-'*60}")
        for doc in results:
            print(f"  [{doc.doc_id}] {doc.category}: {doc.title}")
        print()

    def print_stats(self) -> None:
        """Print corpus size, category counts, and the highest-IDF terms."""
        print(f"\n{'='*75}")
        print("  CORPUS STATISTICS")
        print(f"{'='*75}")
        print(f"  Total Documents    : {self.num_docs}")
        print(f"  Unique Terms       : {len(self.inverted_index)}")
        print(f"  Avg Doc Length     : {self.avg_doc_length:.2f} terms")

        categories = Counter(d.category for d in self.documents)
        print(f"\n  Category Distribution:")
        for cat, count in sorted(categories.items(), key=lambda x: -x[1]):
            print(f"    {cat:<15} : {count}")

        print(f"\n  Top 20 Terms by IDF:")
        top_idf = sorted(self.idf.items(), key=lambda x: -x[1])[:20]
        for term, idf_val in top_idf:
            df = len(self.inverted_index[term])
            print(f"    {term:<20} IDF={idf_val:.4f}  DF={df}")
        print(f"{'='*75}\n")

    def print_query_history(self) -> None:
        """Print the log of queries made during this session."""
        if not self.query_history:
            print("  No queries yet.")
            return
        print(f"\n{'='*75}")
        print("  QUERY HISTORY")
        print(f"{'='*75}")
        for i, entry in enumerate(self.query_history, 1):
            print(f"  {i:>3}. [{entry['method']:>8}] \"{entry['query']}\"  ->  {entry['results']} results")
        print(f"{'='*75}\n")

    def print_evaluation(self, eval_result: dict) -> None:
        """Pretty-print single-query or aggregated evaluation."""
        if 'per_query' in eval_result:
            print(f"\n{'='*75}")
            print(f"  EVALUATION: {eval_result['method'].upper()}")
            print(f"  Queries evaluated: {eval_result['num_queries']}")
            print(f"  Avg Precision     : {eval_result['avg_precision']:.4f}")
            print(f"  Avg Recall        : {eval_result['avg_recall']:.4f}")
            print(f"  Avg F1            : {eval_result['avg_f1']:.4f}")
            print(f"  {'-'*75}")
            for e in eval_result['per_query']:
                print(f"  Q: \"{e['query']}\"")
                print(f"      P={e['precision']:.4f}  R={e['recall']:.4f}  F1={e['f1']:.4f}"
                      f"  ({e['relevant_retrieved']}/{e['relevant']} relevant retrieved)"
                      f"  [top-{e['retrieved']} results]")
            print(f"{'='*75}\n")
        else:
            print(f"\n  Query: \"{eval_result['query']}\"  [{eval_result['method'].upper()}]")
            print(f"  P={eval_result['precision']:.4f}  R={eval_result['recall']:.4f}"
                  f"  F1={eval_result['f1']:.4f}"
                  f"  ({eval_result['relevant_retrieved']}/{eval_result['relevant']} relevant retrieved)")
            print()


# ---------------------------------------------------------------------------
#  Interactive CLI
# ---------------------------------------------------------------------------

def interactive_mode(ir: ClothingIRModel) -> None:
    """Run the command-line loop for searching an already-built model."""
    print(f"\n{'='*75}")
    print("  CLOTHING INFORMATION RETRIEVAL SYSTEM - Interactive Mode")
    print(f"{'='*75}")
    print("  Commands:")
    print("    [query]           - TF-IDF cosine similarity search")
    print("    bm25 [query]      - BM25 ranked search")
    print("    jaccard [query]   - Jaccard similarity search")
    print("    phrase [query]    - Phrase search (terms in order, adjacent)")
    print("    near [query]      - Proximity search (terms within 4 words)")
    print("    and [query]       - Boolean AND search")
    print("    or [query]        - Boolean OR search")
    print("    not [query]       - Boolean NOT search")
    print("    expand [query]    - Query expansion + TF-IDF search")
    print("    cat [category]    - Filter by category")
    print("    stats             - Show corpus statistics")
    print("    history           - Show query history")
    print("    eval              - Run evaluation on test queries")
    print("    help              - Show this help message")
    print("    quit              - Exit")
    print(f"{'='*75}\n")

    while True:
        try:
            user_input = input("  Query> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n  Goodbye!")
            break

        if not user_input:
            continue

        if user_input.lower() == 'quit':
            print("  Goodbye!")
            break

        elif user_input.lower() == 'help':
            print("  Commands: [query], bm25 [query], jaccard [query], phrase [query],")
            print("            near [query], and [query], or [query], not [query],")
            print("            expand [query], cat [category], stats, history, eval,")
            print("            help, quit")

        elif user_input.lower() == 'stats':
            ir.print_stats()

        elif user_input.lower() == 'history':
            ir.print_query_history()

        elif user_input.lower() == 'eval':
            print("  Running evaluation on test queries...")
            eval_result = ir.evaluate_all(TEST_QUERIES, method='tfidf')
            ir.print_evaluation(eval_result)

        elif user_input.lower().startswith('cat '):
            cat_name = user_input[4:].strip()
            matches = [d for d in ir.documents if d.category.lower() == cat_name.lower()]
            if matches:
                print(f"\n  Category '{cat_name}': {len(matches)} documents")
                for d in matches:
                    print(f"    [{d.doc_id}] {d.title}")
            else:
                print(f"  Category '{cat_name}' not found.")

        elif user_input.lower().startswith('bm25 '):
            query = user_input[5:].strip()
            results = ir.bm25_search(query)
            ir.print_results(results, method="BM25")
            ir.query_history.append({'query': query, 'method': 'bm25', 'results': len(results)})

        elif user_input.lower().startswith('jaccard '):
            query = user_input[8:].strip()
            results = ir.jaccard_search(query)
            ir.print_results(results, method="Jaccard")
            ir.query_history.append({'query': query, 'method': 'jaccard', 'results': len(results)})

        elif user_input.lower().startswith('phrase '):
            query = user_input[7:].strip()
            docs = ir.phrase_search(query, max_gap=1)
            if not docs:
                print("  No exact phrase matches found.")
            else:
                print(f"\n  Phrase Search Result (exact match): {len(docs)} documents")
                print(f"  {'-'*60}")
                for doc in docs:
                    print(f"  [{doc.doc_id}] {doc.category}: {doc.title}")
            ir.query_history.append({'query': query, 'method': 'phrase', 'results': len(docs)})

        elif user_input.lower().startswith('near '):
            query = user_input[5:].strip()
            docs = ir.phrase_search(query, max_gap=4)
            if not docs:
                print("  No proximity matches found.")
            else:
                print(f"\n  Proximity Search Result (within 4 words): {len(docs)} documents")
                print(f"  {'-'*60}")
                for doc in docs:
                    print(f"  [{doc.doc_id}] {doc.category}: {doc.title}")
            ir.query_history.append({'query': query, 'method': 'near', 'results': len(docs)})

        elif user_input.lower().startswith('and '):
            query = user_input[4:].strip()
            results = ir.boolean_search(query, mode='AND')
            ir.print_boolean_results(results)
            ir.query_history.append({'query': query, 'method': 'AND', 'results': len(results)})

        elif user_input.lower().startswith('or '):
            query = user_input[3:].strip()
            results = ir.boolean_search(query, mode='OR')
            ir.print_boolean_results(results)
            ir.query_history.append({'query': query, 'method': 'OR', 'results': len(results)})

        elif user_input.lower().startswith('not '):
            query = user_input[4:].strip()
            results = ir.boolean_search(query, mode='NOT')
            ir.print_boolean_results(results)
            ir.query_history.append({'query': query, 'method': 'NOT', 'results': len(results)})

        elif user_input.lower().startswith('expand '):
            query = user_input[7:].strip()
            expanded_terms = ir.query_expansion(query)
            expanded_query = ' '.join(expanded_terms)
            print(f"  Expanded terms: {expanded_terms}")
            results = ir.tfidf_search(expanded_query)
            ir.print_results(results, method="TF-IDF (Expanded)")
            ir.query_history.append({'query': query, 'method': 'expand', 'results': len(results)})

        else:
            results = ir.tfidf_search(user_input)
            ir.print_results(results, method="TF-IDF Cosine Similarity")
            ir.query_history.append({'query': user_input, 'method': 'tfidf', 'results': len(results)})


# ---------------------------------------------------------------------------
#  Evaluation test set
# ---------------------------------------------------------------------------

TEST_QUERIES: list[tuple[str, set[str]]] = [
    # (query, set of relevant doc IDs)
    (
        "black cotton t-shirt men",
        {"D001", "D011", "D021", "D031", "D041", "D051", "D061", "D071", "D081", "D091"},
    ),
    (
        "women printed saree",
        {"D005", "D015", "D025", "D035", "D045", "D055", "D065", "D075", "D085", "D095"},
    ),
    (
        "men slim fit jeans grey",
        {"D003", "D013", "D023", "D033", "D043", "D053", "D063", "D073", "D083", "D093"},
    ),
    (
        "women winter jacket",
        {"D008", "D018", "D028", "D038", "D048", "D058", "D068", "D078", "D088", "D098"},
    ),
    (
        "comfortable kurta breathable",
        {"D004", "D014", "D024", "D034", "D044", "D054", "D064", "D074", "D084", "D094"},
    ),
]


# ---------------------------------------------------------------------------
#  Entry point
# ---------------------------------------------------------------------------

def main():
    """Load the bundled corpus, initialize the model, and start interactive mode."""
    corpus_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'corpus_100.txt')

    ir = ClothingIRModel()
    ir.load_corpus(corpus_path)
    ir.build_index()
    ir.print_stats()

    interactive_mode(ir)


if __name__ == '__main__':
    main()
