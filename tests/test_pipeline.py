from web_research_agent.orchestrator import run_research_pipeline

def test_pipeline_smoke():
    res = run_research_pipeline("Tallest mountain in the world", use_news=False)
    assert "mountain" in res["report"].lower()
    assert len(res["report"]) > 20
