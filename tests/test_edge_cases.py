from web_research_agent.orchestrator import run_research_pipeline

def test_recent_intent():
    rep = run_research_pipeline("latest covid news", use_news=True)["report"]
    assert "covid" in rep.lower()

def test_compare_query():
    rep = run_research_pipeline("Tesla vs Ford profits 2024", use_news=False)["report"]
    assert "Tesla" in rep and "Ford" in rep
