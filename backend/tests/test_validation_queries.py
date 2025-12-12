# backend/tests/test_validation_queries.py
"""
Real model validation tests using the stored sample queries and expected SQL outputs.
This test suite validates that the AI model (OpenAI) generates correct SQL for known questions.

⚠️  IMPORTANT: These tests call the REAL OpenAI API and cost money!
    Run manually when you need to validate model quality.
"""
import json
import os
import pytest
from pathlib import Path
from services.query_service import handle_query, clean_sql_query


# ============================================
# Load Validation Dataset
# ============================================
def load_validation_queries():
    """Load validation queries from JSON file."""
    fixtures_path = Path(__file__).parent / "fixtures" / "validation_queries.json"
    with open(fixtures_path, "r", encoding="utf-8") as f:
        return json.load(f)


VALIDATION_QUERIES = load_validation_queries()


# ============================================
# Real Model Validation Tests
# ============================================
@pytest.mark.no_mock  # ← This ensures tests use REAL OpenAI API
class TestRealModelValidation:
    """
    Test suite for validating AI model's SQL generation against expected outputs.
    
    ⚠️  These tests use the REAL OpenAI API and cost money!
    
    Usage:
        # Run all validation tests
        pytest tests/test_validation_queries.py -v
        
        # Run specific query
        pytest tests/test_validation_queries.py -k "Q1" -v
        
        # Generate validation report
        python tests/validate_model.py
    """
    
    @pytest.mark.parametrize("query_data", VALIDATION_QUERIES, ids=lambda q: f"Q{q['id']}: {q['question'][:50]}")
    def test_sql_generation_and_execution(self, query_data):
        """
        Test that the AI model generates correct SQL and executes successfully.
        Combines quality validation and execution check to avoid duplicate API calls.
        
        This test:
        1. Calls OpenAI API once to generate SQL
        2. Checks that execution succeeded
        3. Validates SQL quality against expected output
        """
        question = query_data["question"]
        expected_sql = query_data["expected_sql"]
        category = query_data["category"]
        
        # Get SQL from REAL OpenAI API (only once!)
        result = handle_query(question)
        generated_sql = clean_sql_query(result.sql_query).upper().strip()
        expected_sql_clean = clean_sql_query(expected_sql).upper().strip()
        
        # Check 1: Execution succeeded (fail fast if execution failed)
        assert result.status == "success", \
            f"Query execution failed\nQ: {question}\nSQL: {result.sql_query}\nError: {getattr(result, 'error_message', 'Unknown')}"
        
        # Check 2: Basic validation
        assert result.sql_query, f"No SQL generated for: {question}"
        assert result.sql_query.strip().upper().startswith("SELECT"), \
            f"Generated SQL doesn't start with SELECT\nQ: {question}\nGot: {result.sql_query}"
        
        # Check 3: SQL quality validation (flexible validation)
        import re
        critical_issues = []
        
        # Extract filtering columns from both queries
        def extract_where_columns(sql: str) -> set:
            if "WHERE" not in sql:
                return set()
            where_part = sql.split("WHERE")[1].split("ORDER BY")[0].split("GROUP BY")[0].split("LIMIT")[0]
            columns = re.findall(r'["\'`]?(\w+)["\'`]?\s*(?:=|<|>|<=|>=|<>|!=|LIKE|BETWEEN|IN)', where_part)
            return set(col.lower() for col in columns)
        
        expected_columns = extract_where_columns(expected_sql_clean)
        generated_columns = extract_where_columns(generated_sql)
        
        # Critical: Must have ORDER BY if it's a ranking query
        if "ORDER BY" in expected_sql_clean and "ORDER BY" not in generated_sql:
            if "LIMIT" in expected_sql_clean:
                critical_issues.append("Missing ORDER BY (ranking query)")
        
        # Smart filtering validation
        if "WHERE" in expected_sql_clean:
            if "WHERE" not in generated_sql:
                # Check if it's a "high X" query where sorting by X DESC is acceptable
                if "ORDER BY" in generated_sql:
                    order_match = expected_sql_clean.split("ORDER BY")[1].split()[0].strip(',')
                    if order_match not in generated_sql:
                        critical_issues.append("Missing WHERE clause (no filtering)")
                else:
                    critical_issues.append("Missing WHERE clause (no filtering)")
            else:
                # Has WHERE, but check if filtering the right columns
                if expected_columns and generated_columns:
                    missing_key_columns = expected_columns - generated_columns
                    if 'position' in missing_key_columns:
                        critical_issues.append(f"Missing position filtering")
        
        # Check for team/league name matching
        if "TEAM" in expected_sql_clean and "LIKE" in expected_sql_clean:
            if "TEAM" in generated_sql and "LIKE" not in generated_sql:
                critical_issues.append("Uses = for team name (should use LIKE)")
        
        # Report only critical issues
        if critical_issues:
            failure_msg = (
                f"\n{'='*80}\n"
                f"❌ VALIDATION FAILED - Critical SQL Issues\n"
                f"{'='*80}\n"
                f"Question: {question}\n"
                f"Category: {category}\n"
                f"Issues: {', '.join(critical_issues)}\n"
                f"\n📝 Expected SQL:\n{expected_sql}\n"
                f"\n🤖 Generated SQL:\n{result.sql_query}\n"
                f"{'='*80}"
            )
            pytest.fail(failure_msg)


# ============================================
# Dataset Integrity Tests (Fast, No API Calls)
# ============================================
class TestValidationDatasetIntegrity:
    """Tests to verify the validation dataset itself is well-formed."""
    
    def test_dataset_loads_successfully(self):
        """Test that validation dataset loads without errors."""
        queries = load_validation_queries()
        assert len(queries) > 0, "Validation dataset is empty"
    
    def test_all_queries_have_required_fields(self):
        """Test that all validation queries have required fields."""
        queries = load_validation_queries()
        required_fields = ["id", "question", "expected_sql", "category", "description"]
        
        for query in queries:
            for field in required_fields:
                assert field in query, f"Query {query.get('id', 'unknown')} missing field: {field}"
                assert query[field], f"Query {query['id']} has empty {field}"
    
    def test_all_expected_sql_start_with_select(self):
        """Test that all expected SQL queries start with SELECT."""
        queries = load_validation_queries()
        
        for query in queries:
            sql = query["expected_sql"].strip().upper()
            assert sql.startswith("SELECT"), \
                f"Query {query['id']} expected_sql doesn't start with SELECT: {query['expected_sql']}"
    
    def test_no_duplicate_ids(self):
        """Test that all query IDs are unique."""
        queries = load_validation_queries()
        ids = [q["id"] for q in queries]
        
        assert len(ids) == len(set(ids)), f"Duplicate IDs found in validation dataset"
    
    def test_no_duplicate_questions(self):
        """Test that all questions are unique."""
        queries = load_validation_queries()
        questions = [q["question"].lower().strip() for q in queries]
        
        duplicates = [q for q in questions if questions.count(q) > 1]
        assert len(set(duplicates)) == 0, f"Duplicate questions found: {set(duplicates)}"
    
    def test_categories_are_valid(self):
        """Test that all categories are from expected set."""
        queries = load_validation_queries()
        valid_categories = {"ranking", "filtering", "complex", "aggregation", "join"}
        
        for query in queries:
            category = query["category"]
            assert category in valid_categories, \
                f"Query {query['id']} has invalid category: {category}. Valid: {valid_categories}"


# ============================================
# Usage Instructions
# ============================================
if __name__ == "__main__":
    print("\n" + "="*80)
    print("REAL MODEL VALIDATION TEST SUITE")
    print("="*80)
    print("\nWARNING: These tests call the REAL OpenAI API and cost money!")
    print("\nUsage:")
    print("  # Run all validation tests")
    print("  pytest tests/test_validation_queries.py -v")
    print("\n  # Run specific query by ID")
    print("  pytest tests/test_validation_queries.py -k 'Q1' -v")
    print("\n  # Run only dataset integrity tests (free, no API calls)")
    print("  pytest tests/test_validation_queries.py::TestValidationDatasetIntegrity -v")
    print("\n  # Generate detailed validation report")
    print("  python tests/validate_model.py")
    print("\n" + "="*80)
    
    # Show dataset summary
    queries = load_validation_queries()
    categories = {}
    for query in queries:
        cat = query["category"]
        categories[cat] = categories.get(cat, 0) + 1
    
    print(f"\nValidation Dataset: {len(queries)} queries")
    for cat, count in sorted(categories.items()):
        print(f"  - {cat}: {count}")
    print("\n" + "="*80 + "\n")
