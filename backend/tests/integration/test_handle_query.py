from services.query_service import handle_query

def test_handle_query_with_mock():
    """Test handle_query directly using the mocked DB chain"""
    question = "Who are the best players?"
    result = handle_query(question)

    # Check QueryResponse fields
    assert result.sql_query.strip().upper() == "SELECT NAME, OVR FROM PLAYERS LIMIT 3"
    assert result.results == "Top players list"
    assert result.status == "success"
    assert isinstance(result.execution_time, int)
    assert result.raw_rows == [
        {"name": "Messi", "ovr": 93},
        {"name": "Ronaldo", "ovr": 92},
        {"name": "Mbappe", "ovr": 91}
    ]
