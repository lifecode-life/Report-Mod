from report_tool.filtering import apply_filters


def test_excludes_categories_and_conditions_consistently():
    grouped = {
        "Cardiovascular": ["LDL Cholesterol", "Blood Pressure"],
        "Metabolic": ["Insulin Resistance", "Fasting Glucose"],
    }

    filtered = apply_filters(
        grouped,
        excluded_categories=["Metabolic"],
        excluded_conditions=["Blood Pressure"],
    )

    assert "Metabolic" not in filtered
    assert filtered["Cardiovascular"] == ["LDL Cholesterol"]
