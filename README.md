# Clothing Information Retrieval System

An information retrieval (IR) model that indexes a corpus of 100 clothing product
documents and lets you search them using multiple retrieval techniques.

## Project Files

| File | Description |
|------|-------------|
| `corpus_100.txt` | Input corpus: 100 clothing documents in XML-like format |
| `clothing_ir_model.py` | The IR system (indexer + search engine + interactive UI) |

Each document in the corpus has four fields:

```
<DOC>
  <DOCID>     unique identifier (D001 ... D100)
  <CATEGORY>  product type (T-Shirt, Shirt, Jeans, Kurta, Saree, Dress, Hoodie, Jacket, Leggings, Sweatshirt)
  <TITLE>     product name
  <TEXT>      product description
</DOC>
```

There are 10 documents per category = 100 documents total.

## How It Works

### 1. Preprocessing
When a document is indexed, its `TITLE` and `TEXT` are combined, then:
- Converted to **lowercase**
- Punctuation and special characters removed
- Split into tokens (words)
- **Stop-words removed** (`the`, `and`, `for`, `with`, `this`, etc.)
- Single-character tokens dropped
- **Porter stemming** applied to reduce words to root forms
  (e.g. "checked" → "check", "lavender" → "lavend", "polyester" → "polyest")

### 2. Inverted Index
Builds a dictionary mapping each unique stemmed term to the set of documents that
contain it. This powers fast Boolean search and candidate retrieval. The corpus
produces **122 unique terms** across 100 documents after stemming.

### 3. TF-IDF + Cosine Similarity (default search)
- **TF (term frequency):** how often a term appears in a document, normalized
  by the document's most frequent term.
- **IDF (inverse document frequency):** terms that appear in few documents get
  higher weight — they are more discriminating.
- Each document is converted into a TF-IDF vector, then **L2-normalized**.
- A query is converted into the same vector space, and documents are ranked by
  **cosine similarity** between the query vector and document vector.
- Higher score = more relevant.

### 4. BM25 (probabilistic ranking)
An alternative ranking model based on probabilistic IR. It uses term frequency,
document frequency, and document length normalization (parameters k1 = 1.5,
b = 0.75). Often improves ranking compared to plain TF-IDF.

### 5. Boolean Search
Set-based retrieval using the inverted index with three modes:
- **AND** — document must contain **all** query terms
- **OR** — document must contain **any** query term
- **NOT** — first term must be present, remaining terms must be absent

Returns an unranked list of matching documents.

### 6. Jaccard Similarity
Set-based similarity between the query term set and each document's term set.
Score = |intersection| / |union|. Simple but effective for comparing query and
document vocabulary overlap.

### 7. Query Expansion
Expands a query with related terms found by **co-occurrence** in the corpus
(terms that frequently appear together with the original query terms). The
expanded query is then run through the TF-IDF search.

### 8. Porter Stemming
A self-contained Porter stemmer reduces words to their root forms before
indexing and querying. This means queries like "shirts" or "breathable" match
documents containing "shirt" or "breathable" without needing exact token
matches.

### 9. Precision / Recall / F1 Evaluation
Built-in evaluation with 5 predefined test queries and relevance judgments.
Run with the `eval` command to see per-query and average precision, recall,
and F1 scores for TF-IDF retrieval.

### 10. Query History
All searches are logged during the session. Use the `history` command to
review what queries were run and how many results each returned.

## How to Run

Open PowerShell and run:

```
cd "C:\Users\SHRESTH\OneDrive\Desktop\CSD\IR\Assignments"
python clothing_ir_model.py
```

If `python` is not recognized, use `py` instead:

```
py clothing_ir_model.py
```

## What Happens When You Run It

1. Loads and parses all 100 documents.
2. Builds the inverted index.
3. Prints **corpus statistics**:
   - Total documents
   - Unique terms
   - Average document length
   - Category distribution
   - Top terms by IDF
4. Starts an **interactive prompt** where you type your own queries.

## Interactive Commands

| Command | Description |
|---------|-------------|
| `your query here` | TF-IDF cosine similarity ranked search |
| `bm25 your query` | BM25 ranked search |
| `jaccard your query` | Jaccard set similarity search |
| `and term1 term2` | Boolean AND search |
| `or term1 term2` | Boolean OR search |
| `not term1 term2` | Boolean NOT search |
| `expand your query` | Query expansion, then TF-IDF search |
| `cat category_name` | List documents in a category, e.g. `cat kurta` |
| `stats` | Show corpus statistics |
| `history` | Show query history |
| `eval` | Run precision/recall/F1 evaluation |
| `help` | Show available commands |
| `quit` | Exit the program |

### Example interactive session

```
Query> black cotton t-shirt
[TF-IDF results with scores]

Query> bm25 women winter jacket
[BM25 results with scores]

Query> and cotton breathable
[Documents containing both "cotton" AND "breathable"]

Query> quit
Goodbye!
```

## Results Format

Each ranked result shows:
- **Rank** — position in the ranked list
- **DOCID + Title** — which document matched
- **Category** — product type
- **Score** — relevance score (cosine similarity or BM25 score)
- **Snippet** — first part of the description

## Summary of Components

```
clothing_ir_model.py
├── PorterStemmer              self-contained English stemmer
├── Document (dataclass)       holds one indexed document
├── ClothingIRModel            main engine
│   ├── load_corpus()          parse corpus_100.txt
│   ├── tokenize()             preprocessing + stemming pipeline
│   ├── build_index()          TF, IDF, inverted index, doc vectors
│   ├── tfidf_search()         ranked retrieval (cosine similarity)
│   ├── bm25_search()          ranked retrieval (BM25)
│   ├── jaccard_search()       ranked retrieval (Jaccard similarity)
│   ├── boolean_search()       AND / OR / NOT set retrieval
│   ├── query_expansion()      related-term expansion
│   ├── evaluate()             precision / recall / F1 per query
│   ├── evaluate_all()         aggregated evaluation across queries
│   ├── print_query_history()  session query log
│   └── print_stats()          corpus statistics
└── interactive_mode()         command-line UI
```

## Code Documentation

The Python module includes docstrings for the `Document` data class, the
`ClothingIRModel` class, every public search/indexing method, and the
interactive entry points. Inline comments are limited to the TF-IDF/BM25 IDF
calculation and vector normalization, where the implementation is easiest to
misread without context.

### Programmatic Usage

The model can also be used without the interactive prompt:

```python
from clothing_ir_model import ClothingIRModel

ir = ClothingIRModel()
ir.load_corpus("corpus_100.txt")
ir.build_index()

results = ir.tfidf_search("black cotton shirt", top_k=5)
for document, score in results:
  print(document.title, score)
```

Call `load_corpus()` before `build_index()`. The search methods should be used
after indexing; otherwise the model has no terms or document vectors to rank.
