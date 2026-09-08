import re
import math
import os
from collections import defaultdict, Counter
from dataclasses import dataclass, field


@dataclass
class Document:
    doc_id: str
    category: str
    title: str
    text: str
    terms: list = field(default_factory=list)
    tf: dict = field(default_factory=dict)
    tfidf: dict = field(default_factory=dict)


class ClothingIRModel:
    def __init__(self):
        self.documents: list[Document] = []
        self.inverted_index: dict[str, set] = defaultdict(set)
        self.idf: dict[str, float] = {}
        self.doc_vectors: dict[str, dict] = {}
        self.doc_lengths: dict[str, int] = {}
        self.avg_doc_length: float = 0.0
        self.num_docs: int = 0

    def load_corpus(self, filepath: str) -> None:
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

    @staticmethod
    def tokenize(text: str) -> list[str]:
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
        return [t for t in tokens if t not in stop_words and len(t) > 1]

    def build_index(self) -> None:
        for doc in self.documents:
            combined_text = f"{doc.title} {doc.text}"
            doc.terms = self.tokenize(combined_text)
            tf = Counter(doc.terms)
            max_freq = max(tf.values()) if tf else 1
            doc.tf = {term: count / max_freq for term, count in tf.items()}
            self.doc_lengths[doc.doc_id] = len(doc.terms)
            for term in set(doc.terms):
                self.inverted_index[term].add(doc.doc_id)

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

    def cosine_similarity(self, query_vec: dict, doc_id: str) -> float:
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

    def bm25_score(self, query_terms: list[str], doc_id: str, k1: float = 1.5, b: float = 0.75) -> float:
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

    def boolean_search(self, query: str, mode: str = 'AND') -> list[Document]:
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

    def print_results(self, results: list[tuple[Document, float]], method: str = "TF-IDF") -> None:
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
        if not results:
            print("  No results found.")
            return
        print(f"\n  Boolean Search Results: {len(results)} documents found")
        print(f"  {'-'*60}")
        for doc in results:
            print(f"  [{doc.doc_id}] {doc.category}: {doc.title}")
        print()

    def print_stats(self) -> None:
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

    def query_expansion(self, query: str) -> list[str]:
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


def interactive_mode(ir: ClothingIRModel) -> None:
    print(f"\n{'='*75}")
    print("  CLOTHING INFORMATION RETRIEVAL SYSTEM - Interactive Mode")
    print(f"{'='*75}")
    print("  Commands:")
    print("    [query]           - TF-IDF cosine similarity search")
    print("    bm25 [query]      - BM25 ranked search")
    print("    and [query]       - Boolean AND search")
    print("    or [query]        - Boolean OR search")
    print("    not [query]       - Boolean NOT search")
    print("    expand [query]    - Query expansion + TF-IDF search")
    print("    cat [category]    - Filter by category")
    print("    stats             - Show corpus statistics")
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
            interactive_mode.__doc__  # just re-show
            print("  Commands: [query], bm25 [query], and [query], or [query],")
            print("            not [query], expand [query], cat [category], stats, quit")
        elif user_input.lower() == 'stats':
            ir.print_stats()
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
        elif user_input.lower().startswith('and '):
            query = user_input[4:].strip()
            results = ir.boolean_search(query, mode='AND')
            ir.print_boolean_results(results)
        elif user_input.lower().startswith('or '):
            query = user_input[3:].strip()
            results = ir.boolean_search(query, mode='OR')
            ir.print_boolean_results(results)
        elif user_input.lower().startswith('not '):
            query = user_input[4:].strip()
            results = ir.boolean_search(query, mode='NOT')
            ir.print_boolean_results(results)
        elif user_input.lower().startswith('expand '):
            query = user_input[7:].strip()
            expanded_terms = ir.query_expansion(query)
            expanded_query = ' '.join(expanded_terms)
            print(f"  Expanded terms: {expanded_terms}")
            results = ir.tfidf_search(expanded_query)
            ir.print_results(results, method="TF-IDF (Expanded)")
        else:
            results = ir.tfidf_search(user_input)
            ir.print_results(results, method="TF-IDF Cosine Similarity")


def main():
    corpus_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'corpus_100.txt')

    ir = ClothingIRModel()
    ir.load_corpus(corpus_path)
    ir.build_index()
    ir.print_stats()

    print("Running sample queries...\n")

    sample_queries = [
        "black cotton t-shirt for men",
        "women's winter jacket warm fabric",
        "breathable comfortable kurta",
        "slim fit shirt button closure",
        "printed saree festive wear",
        "stretch denim jeans grey",
    ]

    for q in sample_queries:
        print(f"\n>>> Query: \"{q}\"")
        results = ir.tfidf_search(q, top_k=5)
        ir.print_results(results, "TF-IDF Cosine Similarity")

        bm25_results = ir.bm25_search(q, top_k=5)
        ir.print_results(bm25_results, "BM25")

    print("\n\nSample Boolean Queries:\n")
    boolean_queries = [
        ("cotton AND breathable", "AND"),
        ("black OR white", "OR"),
        ("winter NOT jacket", "NOT"),
    ]
    for q, mode in boolean_queries:
        print(f">>> Boolean {mode}: \"{q}\"")
        results = ir.boolean_search(q, mode=mode)
        ir.print_boolean_results(results)

    print("\n\nSample Query Expansion:\n")
    for q in ["cotton comfortable", "winter warm"]:
        print(f">>> Original: \"{q}\"")
        expanded = ir.query_expansion(q)
        print(f"    Expanded terms: {expanded}")
        results = ir.tfidf_search(' '.join(expanded), top_k=5)
        ir.print_results(results, "TF-IDF (Expanded)")

    interactive_mode(ir)


if __name__ == '__main__':
    main()
