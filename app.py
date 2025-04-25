
import streamlit as st
from web_research_agent.orchestrator import run_research_pipeline

st.set_page_config(page_title="Web Research Agent", layout="wide")

st.title("🔎 Web Research Agent (OSS)")
st.markdown(
    "Enter a research question.  The agent will search the open web, analyse sources, "
    "and generate a concise plain-text report.  "
    "A JSON trace of every step is downloadable for auditing."
)

query = st.text_input("Your question:", placeholder="e.g. Economic impact of electric cars in Europe")
do_news = st.checkbox("Include recent news feeds", value=True)

if st.button("Run research") and query.strip():
    with st.spinner("Working… this may take ~30 s on first run (model download)."):
        result = run_research_pipeline(query.strip(), use_news=do_news)
    st.subheader("📄 Report")
    st.write(result["report"])
    st.download_button(
        label="Download execution trace (JSON)",
        data=open(result["trace_path"], "rb").read(),
        file_name="execution_trace.json",
        mime="application/json"
    )
