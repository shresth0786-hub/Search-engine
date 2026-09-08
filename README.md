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

### 2. Inverted Index
Builds a dictionary mapping each unique term to the set of documents that
contain it. This powers fast Boolean search and candidate retrieval. The corpus
produces **124 unique terms** across 100 documents.

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

### 6. Query Expansion
Expands a query with related terms found by **co-occurrence** in the corpus
(terms that frequently appear together with the original query terms). The
expanded query is then run through the TF-IDF search.

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
| `and term1 term2` | Boolean AND search |
| `or term1 term2` | Boolean OR search |
| `not term1 term2` | Boolean NOT search |
| `expand your query` | Query expansion, then TF-IDF search |
| `cat category_name` | List documents in a category, e.g. `cat kurta` |
| `stats` | Show corpus statistics |
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
├── Document (dataclass)     holds one indexed document
├── ClothingIRModel           main engine
│   ├── load_corpus()         parse corpus_100.txt
│   ├── tokenize()            preprocessing pipeline
│   ├── build_index()         TF, IDF, inverted index, doc vectors
│   ├── tfidf_search()        ranked retrieval (cosine similarity)
│   ├── bm25_search()         ranked retrieval (BM25)
│   ├── boolean_search()      AND / OR / NOT set retrieval
│   ├── query_expansion()     related-term expansion
│   └── print_stats()         corpus statistics
└── interactive_mode()        command-line UI
```
