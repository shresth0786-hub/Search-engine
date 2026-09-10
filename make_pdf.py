import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fpdf import FPDF


class IRDocPDF(FPDF):
    def header(self):
        self.set_font('Helvetica', 'B', 10)
        self.set_text_color(120, 120, 120)
        self.cell(0, 8, 'Clothing Information Retrieval System', 0, 0, 'L')
        self.cell(0, 8, f'Page {self.page_no()}', 0, 1, 'R')
        self.ln(2)
        self.set_draw_color(120, 120, 120)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(4)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 10, 'IR Assignment 1 - Clothing Information Retrieval', 0, 0, 'C')

    def chapter_title(self, title):
        self.set_font('Helvetica', 'B', 15)
        self.set_text_color(20, 20, 20)
        self.cell(0, 10, title, 0, 1, 'L')
        self.ln(2)

    def section_title(self, title):
        self.set_font('Helvetica', 'B', 12)
        self.set_text_color(30, 30, 90)
        self.cell(0, 8, title, 0, 1, 'L')
        self.ln(1)

    def subsection_title(self, title):
        self.set_font('Helvetica', 'B', 11)
        self.set_text_color(40, 40, 40)
        self.cell(0, 7, title, 0, 1, 'L')
        self.ln(1)

    def body(self, text):
        self.set_font('Helvetica', '', 10.5)
        self.set_text_color(40, 40, 40)
        self.multi_cell(0, 5.5, text)
        self.ln(2)

    def bullet(self, text):
        self.set_font('Helvetica', '', 10.5)
        self.set_text_color(40, 40, 40)
        self.set_x(14)
        self.multi_cell(0, 5.5, '  -  ' + text)
        self.ln(1)

    def code_block(self, text):
        self.set_font('Courier', '', 9)
        self.set_fill_color(240, 240, 244)
        self.set_text_color(30, 30, 30)
        self.ln(1)
        lines = text.split('\n')
        for line in lines:
            self.set_x(14)
            self.cell(0, 5, line, 0, 1, 'L', fill=True)
        self.ln(3)

    def spacer(self, h=6):
        self.ln(h)


def generate_pdf(path):
    pdf = IRDocPDF()
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()

    # Title page
    pdf.set_font('Helvetica', 'B', 26)
    pdf.set_text_color(20, 20, 80)
    pdf.cell(0, 16, '', 0, 1, 'C')
    pdf.cell(0, 16, 'Clothing Information', 0, 1, 'C')
    pdf.cell(0, 16, 'Retrieval System', 0, 1, 'C')
    pdf.ln(4)
    pdf.set_font('Helvetica', '', 13)
    pdf.set_text_color(60, 60, 60)
    pdf.cell(0, 8, 'Assignment 1 - Information Retrieval', 0, 1, 'C')
    pdf.cell(0, 8, 'Project Documentation', 0, 1, 'C')
    pdf.ln(10)
    pdf.set_font('Helvetica', 'I', 10)
    pdf.cell(0, 6, 'A term-based search engine over a 100-document clothing corpus', 0, 1, 'C')
    pdf.cell(0, 6, 'implemented from scratch in Python.', 0, 1, 'C')
    pdf.add_page()

    # 1. Overview
    pdf.chapter_title('1. Overview')
    pdf.body(
        'This project implements a complete Information Retrieval (IR) system for a corpus of 100 '
        'clothing product documents. Each document describes a single garment with a document ID, '
        'category, title, and free-text description. The system indexes the corpus and lets the user '
        'retrieve relevant documents using several retrieval models: TF-IDF with cosine similarity, '
        'BM25, Boolean set retrieval, Jaccard similarity, and phrase/proximity search through a '
        'positional index. Comprehensive evaluation metrics (precision, recall, F1, AP, MAP, NDCG) '
        'are included, along with optional query expansion and an interactive command-line interface.'
    )
    pdf.body(
        'All components - preprocessing, stemming, indexing, and ranking - are implemented from '
        'scratch in a single Python module with no third-party dependencies.'
    )

    # 2. Corpus
    pdf.chapter_title('2. Corpus')
    pdf.body(
        'The corpus file corpus_100.txt contains 100 documents in an XML-like format. Each document '
        'has four fields:'
    )
    pdf.code_block(
        '<DOC>\n'
        '  <DOCID>     D001 ... D100\n'
        '  <CATEGORY>  T-Shirt | Shirt | Jeans | Kurta | Saree | Dress |\n'
        '              Hoodie | Jacket | Leggings | Sweatshirt\n'
        '  <TITLE>     product name (gender, style, garment, colour)\n'
        '  <TEXT>      fabric, features, sizing and usage description\n'
        '</DOC>'
    )
    pdf.body('There are exactly 10 documents per category, giving a balanced 10 x 10 corpus.')
    pdf.subsection_title('Corpus Statistics')
    pdf.bullet('Total documents: 100')
    pdf.bullet('Unique terms after stemming and stop-word removal: 122')
    pdf.bullet('Categories (10 each): T-Shirt, Shirt, Jeans, Kurta, Saree, Dress, Hoodie, Jacket, Leggings, Sweatshirt')

    # 3. Pipeline
    pdf.chapter_title('3. Processing Pipeline')
    pdf.section_title('3.1 Preprocessing')
    pdf.body(
        "Every document's title and text are combined and run through the preprocessing pipeline:"
    )
    pdf.bullet('Lowercasing - all text converted to lowercase.')
    pdf.bullet('Punctuation removal - non-alphanumeric characters stripped.')
    pdf.bullet('Tokenization - text split into individual words.')
    pdf.bullet('Stop-word removal - a list of ~90 common English stop-words removed (the, and, for, with...).')
    pdf.bullet('Short-token removal - single-character tokens dropped.')
    pdf.bullet('Stemming - a self-contained Porter stemmer reduces words to root forms (checked->check, lavender->lavend).')

    pdf.section_title('3.2 Index Construction')
    pdf.body(
        'Two indexes are built over the preprocessed tokens:'
    )
    pdf.bullet(
        'Inverted index: term -> set of document IDs containing the term. This powers Boolean search '
        'and candidate retrieval for ranked search.'
    )
    pdf.bullet(
        'Positional index: term -> {doc_id: [positions]}. Stores the exact position of each term in '
        'each document so phrase and proximity queries can be answered by merging position lists.'
    )
    pdf.body(
        'The model also computes IDF (inverse document frequency) for every term and a normalized '
        'TF-IDF vector for every document. The average document length is recorded for BM25.'
    )

    # 4. Retrieval models
    pdf.chapter_title('4. Retrieval Models')
    pdf.section_title('4.1 TF-IDF with Cosine Similarity')
    pdf.body(
        'TF-IDF weights each term by how often it appears in a document (TF) and how rare it is across '
        'the corpus (IDF). Documents and queries are represented as L2-normalized TF-IDF vectors and '
        'ranked by cosine similarity (dot product of normalized vectors). Higher scores mean stronger '
        'relevance.'
    )
    pdf.section_title('4.2 BM25')
    pdf.body(
        'BM25 is a probabilistic ranking function. Each query term contributes an IDF score scaled by '
        'its term frequency and dampened by document length (parameters k1 = 1.5, b = 0.75). It is '
        'well suited to documents of varying length and often outperforms plain TF-IDF.'
    )
    pdf.section_title('4.3 Boolean Search (AND / OR / NOT)')
    pdf.body(
        'Classic set-based retrieval over the inverted index. AND returns documents containing all query '
        'terms, OR returns documents containing any term, and NOT subtracts documents of later terms '
        'from the first. Results are unranked.'
    )
    pdf.section_title('4.4 Jaccard Similarity')
    pdf.body(
        'Treats query and document as sets of terms and scores them by |intersection| / |union|. A '
        'simple overlap measure that ignores term weight, used here as a comparison baseline.'
    )
    pdf.section_title('4.5 Phrase and Proximity Search (Positional Index)')
    pdf.body(
        'Because the positional index records term positions, the system answers two further query types:'
    )
    pdf.bullet(
        'Phrase search (phrase [query]): query terms must appear adjacent and in order. '
        'e.g. phrase regular fit matches "Men\'s Regular Fit Kurta - Pink".'
    )
    pdf.bullet(
        'Proximity search (near [query]): query terms must appear in order within a small window '
        '(4 positions). e.g. near winter jacket matches "Women\'s Quilted Winter Jacket".'
    )
    pdf.body(
        'Position lists are merged with a pointer-scanning algorithm that walks each term\'s position '
        'list and accepts a document when every query term occurs within the allowed gap in order.'
    )
    pdf.section_title('4.6 Query Expansion')
    pdf.body(
        'Expands a query with related terms that co-occur frequently with the original terms across the '
        'corpus, then re-runs the expanded query through TF-IDF. Broadens retrieval when the user is '
        'unsure of the exact vocabulary.'
    )

    # 5. Evaluation
    pdf.chapter_title('5. Evaluation Metrics')
    pdf.body(
        'Five predefined test queries with gold relevance judgments evaluate the retrieval quality of '
        'TF-IDF, BM25, and Jaccard. Correct documents per query are the 10 documents of the target '
        'category.'
    )
    pdf.section_title('5.1 Precision, Recall, F1')
    pdf.bullet('Precision = (relevant retrieved) / (total retrieved).')
    pdf.bullet('Recall = (relevant retrieved) / (total relevant).')
    pdf.bullet('F1 = 2PR / (P + R), the harmonic mean of the two.')
    pdf.section_title('5.2 Average Precision (AP) and MAP')
    pdf.body(
        'AP is computed at every rank where a relevant document appears, making it sensitive to ranking '
        'order. MAP averages AP over all test queries. A perfect ordering gives AP = MAP = 1.0.'
    )
    pdf.section_title('5.3 NDCG (Normalized Discounted Cumulative Gain)')
    pdf.body(
        'NDCG values documents by rank, discounting the gain of lower-ranked documents by log2(rank). '
        'It is normalized by the ideal ranking, so NDCG = 1.0 means the top documents are exactly the '
        'relevant ones in the best order.'
    )
    pdf.subsection_title('Results on the test set')
    pdf.body(
        'TF-IDF and BM25 both achieve perfect scores (P = R = F1 = AP = MAP = NDCG = 1.0) because the '
        'test queries were built to match their categories exactly. Jaccard scores lower overall '
        '(MAP = 0.846, mean NDCG = 0.885); on the first query only 3 of its 10 hits are relevant, '
        'giving AP = 0.23 and NDCG = 0.42. This demonstrates that the ranking-aware metrics can '
        'differentiate methods with identical precision.'
    )

    # 6. Usage
    pdf.chapter_title('6. Usage')
    pdf.subsection_title('Requirements')
    pdf.bullet('Python 3.8+ (developed and tested on Python 3.13).')
    pdf.bullet('No third-party packages required.')
    pdf.subsection_title('Running the system')
    pdf.code_block(
        'cd "C:\\Users\\SHRESTH\\OneDrive\\Desktop\\CSD\\IR\\Assignments"\n'
        'python clothing_ir_model.py\n'
        '(or: py clothing_ir_model.py)'
    )
    pdf.body(
        'The program loads the corpus, builds the indexes, prints corpus statistics, and enters an '
        'interactive prompt.'
    )
    pdf.subsection_title('Interactive commands')
    pdf.code_block(
        '[query]        TF-IDF cosine similarity ranked search\n'
        'bm25 [query]   BM25 ranked search\n'
        'jaccard [query] Jaccard set similarity search\n'
        'phrase [query] Exact phrase search (adjacent, in order)\n'
        'near [query]   Proximity search (in order, within 4 words)\n'
        'and [query]    Boolean AND     or [query]  Boolean OR\n'
        'not [query]    Boolean NOT     expand [q]  Query expansion\n'
        'cat [name]     List docs in a category\n'
        'stats          Corpus statistics   history  Query log\n'
        'eval           Run P/R/F1/AP/MAP/NDCG evaluation on all methods\n'
        'help           Show commands      quit      Exit'
    )

    # 7. Programmatic usage
    pdf.chapter_title('7. Programmatic Usage')
    pdf.body('The model can also be used from Python code without the interactive prompt:')
    pdf.code_block(
        'from clothing_ir_model import ClothingIRModel\n'
        '\n'
        'ir = ClothingIRModel()\n'
        'ir.load_corpus("corpus_100.txt")\n'
        'ir.build_index()\n'
        '\n'
        'results = ir.tfidf_search("black cotton shirt", top_k=5)\n'
        'for doc, score in results:\n'
        '    print(doc.title, score)'
    )

    # 8. Project structure
    pdf.chapter_title('8. Project Files')
    pdf.code_block(
        'clothing_ir_model.py   - the full IR system (indexing, search, CLI)\n'
        'corpus_100.txt         - the 100-document input corpus\n'
        'README.md              - markdown documentation\n'
        'Assignment_Clothing_IR.pdf - this document'
    )

    # 9. Summary of components
    pdf.chapter_title('9. Component Map')
    pdf.code_block(
        'PorterStemmer            -> protected English stemmer\n'
        'Document (dataclass)     -> one indexed document\n'
        'ClothingIRModel          -> main engine\n'
        '  load_corpus()          parse corpus_100.txt\n'
        '  tokenize()             preprocessing + stemming\n'
        '  build_index()          TF, IDF, inverted, positional index\n'
        '  tfidf_search()         cosine similarity ranking\n'
        '  bm25_search()          BM25 ranking\n'
        '  jaccard_search()       Jaccard ranking\n'
        '  phrase_search()        positional phrase matching\n'
        '  phrase_search_ranked() phrase ranking with TF-IDF\n'
        '  boolean_search()       AND / OR / NOT\n'
        '  query_expansion()      co-occurrence expansion\n'
        '  average_precision()    AP metric\n'
        '  ndcg()                 NDCG metric\n'
        '  evaluate()             P/R/F1/AP/NDCG per query\n'
        '  evaluate_all()         MAP, mean NDCG across queries\n'
        'interactive_mode()       command-line user interface'
    )

    pdf.output(path)
    return path


if __name__ == '__main__':
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Assignment_Clothing_IR.pdf')
    print('Generating', out)
    generate_pdf(out)
    print('PDF generated successfully:', out)