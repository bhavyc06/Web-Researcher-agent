# Web-Researcher-agent


A minimal multi-step agent that:

1. Accepts a natural-language research question  
2. Searches the web (DuckDuckGo) ± news feeds  
3. Scrapes top pages, summarises with spaCy  
4. Fuses summaries into a plain-text report with an open HuggingFace model (BART)  
5. Saves a JSON execution trace (MCP-style) for transparency  
6. Presents the answer via Streamlit

## Quick Start

```bash
git clone …/web_research_agent.git
cd web_research_agent
python -m venv .venv && source .venv/bin/activate        # or `.\.venv\Scripts\activate`
pip install -r requirements.txt
python -m spacy download en_core_web_sm                  # one-time download
streamlit run app.py
