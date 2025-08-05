from services.query_service import apply_alias_mapping, extract_column_names

def test_apply_alias_mapping():
    """Test alias mapping replaces terms correctly."""
    question = "Show me all footballers"
    mapped = apply_alias_mapping(question)
    assert "players" in mapped.lower()
    assert mapped != question  # Should be changed

def test_apply_alias_mapping_no_change():
    """Test alias mapping leaves unknown words unchanged."""
    question = "Show me all astronauts"
    mapped = apply_alias_mapping(question)
    assert mapped == question

def test_extract_column_names_simple():
    """Test column extraction from simple SQL."""
    sql = "SELECT name, ovr FROM players"
    columns = extract_column_names(sql)
    assert columns == ["name", "ovr"]

def test_extract_column_names_default():
    """Test default columns when SQL parse fails."""
    sql = "INVALID SQL"
    columns = extract_column_names(sql)
    assert columns == ["rank", "name", "ovr", "position", "nation", "team"]
