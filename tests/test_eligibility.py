"""Basic tests for CivicGuardian AI eligibility and agents."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from servers.scheme_server import SchemeServer
from agents.eligibility_agent import EligibilityAgent
from agents.planner_agent import PlannerAgent
from agents.readiness_agent import ReadinessAgent
from agents.scheme_agent import SchemeAgent

def test_farmer_eligibility():
    server = SchemeServer()
    agent = EligibilityAgent(server)
    profile = {"occupation":"Farmer","income":150000,"age":35,"state":"Maharashtra","gender":"MALE","disability":False,"caste":"General"}
    results = agent.evaluate(profile)
    assert len(results) > 0, "Farmer should match at least one scheme"
    ids = [r["id"] for r in results]
    assert "pm_kisan" in ids, "PM-KISAN should match for farmer"
    print(f"✅ Farmer: {len(results)} schemes matched")

def test_student_eligibility():
    server = SchemeServer()
    agent = EligibilityAgent(server)
    profile = {"occupation":"Student","income":200000,"age":20,"state":"Delhi","gender":"MALE","disability":False,"caste":"General"}
    results = agent.evaluate(profile)
    assert len(results) > 0
    print(f"✅ Student: {len(results)} schemes matched")

def test_senior_citizen():
    server = SchemeServer()
    agent = EligibilityAgent(server)
    profile = {"occupation":"Senior Citizen","income":80000,"age":65,"state":"Kerala","gender":"FEMALE","disability":False,"caste":"General"}
    results = agent.evaluate(profile)
    assert any(r["id"] == "pm_vaya_vandana" for r in results)
    print(f"✅ Senior Citizen: {len(results)} schemes matched")

def test_income_filter():
    server = SchemeServer()
    agent = EligibilityAgent(server)
    profile = {"occupation":"Farmer","income":5000000,"age":35,"state":"Punjab","gender":"MALE","disability":False,"caste":"General"}
    results = agent.evaluate(profile)
    ids = [r["id"] for r in results]
    assert "pm_kisan" not in ids, "High income farmer should not match PM-KISAN"
    print(f"✅ Income filter: high-income farmer correctly filtered")

def test_planner():
    planner = PlannerAgent()
    schemes = [{"documents":["Aadhaar","PAN","Income Certificate"]}]
    result = planner.build_plan(schemes, ["Aadhaar"])
    assert "PAN" in result["missing"]
    assert "Aadhaar" in result["uploaded"]
    assert len(result["action_plan"]) == 2
    print(f"✅ Planner: correct plan generated")

def test_readiness():
    agent = ReadinessAgent()
    result = agent.compute(["Aadhaar","PAN","Income Certificate"], ["Aadhaar","PAN"])
    assert result["score"] == 66
    print(f"✅ Readiness: score computed correctly")

def test_scheme_cards():
    server = SchemeServer()
    ea = EligibilityAgent(server)
    sa = SchemeAgent()
    profile = {"occupation":"Farmer","income":100000,"age":30,"state":"UP","gender":"MALE","disability":False,"caste":"General"}
    eligible = ea.evaluate(profile)
    cards = sa.build_cards(eligible)
    assert len(cards) == len(eligible)
    assert all("income_limit_display" in c for c in cards)
    print(f"✅ Scheme cards: {len(cards)} cards built")

if __name__ == "__main__":
    test_farmer_eligibility()
    test_student_eligibility()
    test_senior_citizen()
    test_income_filter()
    test_planner()
    test_readiness()
    test_scheme_cards()
    print("\n🎉 All tests passed!")
