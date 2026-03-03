from report_tool.extraction import extract_conditions_from_text


def test_extracts_categories_and_conditions_from_mixed_format():
    text = """
CATEGORY: Cardiovascular
- LDL Cholesterol
- Blood Pressure

METABOLIC
1) Insulin Resistance
2) Fasting Glucose
"""
    result = extract_conditions_from_text(text)
    assert "Cardiovascular" in result.grouped_conditions
    assert "Ldl Cholesterol" not in result.grouped_conditions.get("Cardiovascular", [])
    assert "LDL Cholesterol" in result.grouped_conditions["Cardiovascular"]
    assert "Metabolic" in result.grouped_conditions
    assert "Insulin Resistance" in result.grouped_conditions["Metabolic"]


def test_marks_uncertain_when_minimal_data_found():
    result = extract_conditions_from_text("- One")
    assert result.uncertain is True
    assert result.warnings
