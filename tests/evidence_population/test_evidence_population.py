from claire.evidence_population.evidence_quality_checker import EvidenceQualityChecker
from claire.evidence_population.population_report_builder import PopulationReportBuilder

def test_quality_checker_detects_missing():
    result = EvidenceQualityChecker().check({"id": "x"})
    assert result["status"] == "incomplete"

def test_population_report_coverage():
    report = PopulationReportBuilder().build_report([{"review_status": "reviewed"}])
    assert report["review_coverage"] == 1.0
