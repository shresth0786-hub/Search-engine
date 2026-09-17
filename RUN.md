# READ ME FIRST - How To Run Everything

All paths below use the project folder on this computer:

    C:\Users\SHRESTH\OneDrive\Desktop\CSD\IR\Assignments

Open a PowerShell window and copy-paste the commands.

--------------------------------------------------------------
1. RUN THE COMMAND-LINE (interactive terminal) VERSION
--------------------------------------------------------------

Open PowerShell, then:

    cd "C:\Users\SHRESTH\OneDrive\Desktop\CSD\IR\Assignments"
    python clothing_ir_model.py

If "python" is not recognized, try:

    py clothing_ir_model.py

You will see corpus statistics printed, then a "Query>" prompt.
Type a query and press Enter.

  Example commands you can type at the prompt:

    black cotton t-shirt              -> TF-IDF ranked search (default)
    bm25 women winter jacket          -> BM25 ranked search
    jaccard comfortable kurta         -> Jaccard similarity search
    phrase regular fit                -> exact phrase search
    near casual dress                 -> proximity search (words within 4)
    and cotton breathable             -> Boolean AND
    or cotton wool                    -> Boolean OR
    not winter cotton                 -> Boolean NOT
    expand comfortable kurta          -> query expansion + TF-IDF
    suggest black coton shrt          -> spelling correction (did-you-mean)
    feedback women winter jacket      -> pseudo-relevance feedback
    export black cotton t-shirt       -> save results to results_output.txt
    cat kurta                         -> list documents in a category
    stats                             -> corpus statistics
    history                           -> session query log
    eval                              -> evaluation (P/R/F1, MAP, NDCG)
    help                              -> list of all commands
    quit                              -> close the program

--------------------------------------------------------------
2. RUN THE WEB FRONT END (browser version)
--------------------------------------------------------------

Open PowerShell, then:

    cd "C:\Users\SHRESTH\OneDrive\Desktop\CSD\IR\Assignments"
    pip install flask
    python webapp.py

Then open your browser and go to:

    http://127.0.0.1:5000

The page lets you:
  - click method tabs (TF-IDF / BM25 / Jaccard / Phrase / Proximity / AND / OR / NOT)
  - type a query in the search box and press Enter
  - use the Spell check, Feedback, and Evaluate buttons
  - press "Export results (.txt)" to download the last search

Press Ctrl+C in the PowerShell window to stop the web server.

--------------------------------------------------------------
3. REGENERATE THE DOCUMENTS (Word + PDFs)
--------------------------------------------------------------

    python make_docx.py               -> updates IR_Assignment_Documentation.docx
    python make_frontend_pdf.py       -> updates IR_Frontend_Study_Guide.pdf
    python make_demo_pdf.py           -> updates IR_DEMO_Presentation.pdf
    python make_updates_pdf.py        -> updates IR_Updates.pdf

--------------------------------------------------------------
4. GIT (push new changes to GitHub)
--------------------------------------------------------------

    cd "C:\Users\SHRESTH\OneDrive\Desktop\CSD\IR\Assignments"
    git add .
    git commit -m "describe your change"
    git push

The repository is: https://github.com/shresth0786-hub/Search-engine