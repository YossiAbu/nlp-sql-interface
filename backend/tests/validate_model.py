#!/usr/bin/env python3
"""
AI Model Validation Script

This script runs all validation queries through the REAL OpenAI API
and generates a detailed quality report.

⚠️  WARNING: This calls the real OpenAI API and costs money!

Usage:
    python tests/validate_model.py
    
    # With detailed output
    python tests/validate_model.py --verbose
    
    # Save report to file
    python tests/validate_model.py --output validation_report.txt
"""

import json
import sys
import time
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.query_service import handle_query, clean_sql_query


def load_validation_queries() -> List[Dict]:
    """Load validation queries from JSON file."""
    fixtures_path = Path(__file__).parent / "fixtures" / "validation_queries.json"
    with open(fixtures_path, "r", encoding="utf-8") as f:
        return json.load(f)


def extract_where_columns(sql: str) -> set:
    """Extract column names mentioned in WHERE clause."""
    import re
    sql_upper = sql.upper()
    
    if "WHERE" not in sql_upper:
        return set()
    
    # Get WHERE clause
    where_part = sql_upper.split("WHERE")[1].split("ORDER BY")[0].split("GROUP BY")[0].split("LIMIT")[0]
    
    # Extract column names (simple approach - looks for identifiers before operators)
    # Matches: word characters (possibly quoted) before =, <, >, LIKE, BETWEEN, etc.
    columns = re.findall(r'["\'`]?(\w+)["\'`]?\s*(?:=|<|>|<=|>=|<>|!=|LIKE|BETWEEN|IN)', where_part)
    
    return set(col.lower() for col in columns)


def check_sql_similarity(generated: str, expected: str) -> Tuple[bool, List[str]]:
    """
    Check if generated SQL is semantically similar to expected SQL.
    Uses flexible rules - AI can use alternative valid approaches.
    Returns (passed, warnings)
    """
    generated_clean = clean_sql_query(generated).upper().strip()
    expected_clean = clean_sql_query(expected).upper().strip()
    
    warnings = []
    critical_issues = []
    
    # Extract filtering columns from both queries
    expected_columns = extract_where_columns(expected_clean)
    generated_columns = extract_where_columns(generated_clean)
    
    # Critical: Must have ORDER BY if expected has it (for ranking queries)
    if "ORDER BY" in expected_clean and "ORDER BY" not in generated_clean:
        # Only critical if it's a ranking/sorting query
        if "LIMIT" in expected_clean:  # Ranking queries usually have LIMIT
            critical_issues.append("Missing ORDER BY (ranking query)")
        else:
            warnings.append("Missing ORDER BY (but query might work)")
    
    # Smart filtering validation
    if "WHERE" in expected_clean:
        if "WHERE" not in generated_clean:
            # Check if it's a "high X" query where sorting by X DESC is acceptable
            # Pattern: "high/best/top" + sorting by that attribute
            if "ORDER BY" in generated_clean:
                # Extract ORDER BY column
                order_match = expected_clean.split("ORDER BY")[1].split()[0].strip(',')
                if order_match in generated_clean:
                    warnings.append(f"No WHERE but sorts by {order_match} (acceptable for ranking)")
                else:
                    critical_issues.append("Missing WHERE clause (no filtering)")
            else:
                critical_issues.append("Missing WHERE clause (no filtering)")
        else:
            # Has WHERE, but are we filtering the right columns?
            # Check if key filtering columns from expected appear in generated
            if expected_columns and generated_columns:
                missing_key_columns = expected_columns - generated_columns
                if missing_key_columns:
                    # Special case: filtering by related column is okay (def vs position for defenders)
                    # But position filtering is critical for role-based queries
                    if 'position' in missing_key_columns:
                        critical_issues.append(f"Missing position filtering (filters by {', '.join(generated_columns)} instead)")
                    else:
                        warnings.append(f"Filters different columns: expected {expected_columns}, got {generated_columns}")
    
    # Check for team/league name matching - LIKE is important for partial matches
    if "TEAM" in expected_clean and "LIKE" in expected_clean:
        if "TEAM" in generated_clean and "LIKE" not in generated_clean:
            critical_issues.append("Uses = for team name (should use LIKE for variations like 'FC Barcelona')")
    
    if "LEAGUE" in expected_clean and "LIKE" in expected_clean:
        if "LEAGUE" in generated_clean and "LIKE" not in generated_clean:
            warnings.append("Uses = for league name (LIKE might be safer for variations)")
    
    # Flexible: BETWEEN can be replaced with >= AND <=
    if "BETWEEN" in expected_clean and "BETWEEN" not in generated_clean:
        if ">=" in generated_clean or "<=" in generated_clean:
            warnings.append("Uses >= AND <= instead of BETWEEN (valid alternative)")
        else:
            warnings.append("Missing BETWEEN or range check")
    
    # Pass if no critical issues
    passed = len(critical_issues) == 0
    
    # Combine critical issues and warnings for reporting
    all_notes = critical_issues + warnings
    
    return passed, all_notes


def run_validation(verbose: bool = False) -> Dict:
    """Run validation on all queries and return results."""
    queries = load_validation_queries()
    results = []
    
    print("\n" + "="*80)
    print("🤖 AI MODEL VALIDATION - Running Real OpenAI API Tests")
    print("="*80)
    print(f"\nTotal queries to validate: {len(queries)}")
    print("⚠️  This will call the OpenAI API and cost money!\n")
    
    start_time = time.time()
    
    for i, query_data in enumerate(queries, 1):
        question = query_data["question"]
        expected_sql = query_data["expected_sql"]
        category = query_data["category"]
        query_id = query_data["id"]
        
        print(f"[{i}/{len(queries)}] Testing Q{query_id}: {question[:60]}...", end=" ", flush=True)
        
        try:
            # Call real OpenAI API
            result = handle_query(question)
            generated_sql = result.sql_query
            
            # Check quality
            passed, missing = check_sql_similarity(generated_sql, expected_sql)
            
            results.append({
                "id": query_id,
                "question": question,
                "category": category,
                "expected_sql": expected_sql,
                "generated_sql": generated_sql,
                "passed": passed,
                "missing_components": missing,
                "execution_status": result.status,
                "execution_time": result.execution_time
            })
            
            if passed:
                if missing:  # Has warnings but passed
                    print(f"✅ PASS (Notes: {', '.join(missing)})")
                else:
                    print("✅ PASS")
            else:
                print(f"❌ FAIL ({', '.join(missing)})")
            
            if verbose:
                print(f"  Expected: {expected_sql}")
                print(f"  Generated: {generated_sql}")
                print()
            
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
            results.append({
                "id": query_id,
                "question": question,
                "category": category,
                "expected_sql": expected_sql,
                "generated_sql": None,
                "passed": False,
                "missing_components": [],
                "execution_status": "error",
                "error": str(e)
            })
    
    elapsed_time = time.time() - start_time
    
    return {
        "results": results,
        "total": len(queries),
        "passed": sum(1 for r in results if r["passed"]),
        "failed": sum(1 for r in results if not r["passed"]),
        "elapsed_time": elapsed_time,
        "timestamp": datetime.now().isoformat()
    }


def generate_report(validation_data: Dict) -> str:
    """Generate a formatted validation report."""
    results = validation_data["results"]
    total = validation_data["total"]
    passed = validation_data["passed"]
    failed = validation_data["failed"]
    accuracy = (passed / total * 100) if total > 0 else 0
    
    report = []
    report.append("\n" + "="*80)
    report.append("📊 AI MODEL VALIDATION REPORT")
    report.append("="*80)
    report.append(f"\nGenerated: {validation_data['timestamp']}")
    report.append(f"Execution Time: {validation_data['elapsed_time']:.2f} seconds")
    report.append("\n✅ Flexible Validation: AI can use valid alternatives (= instead of LIKE, >= instead of BETWEEN)")
    report.append("❌ Critical Issues: Missing required filtering or sorting for query type")
    report.append(f"\n{'='*80}")
    report.append("\n📈 SUMMARY")
    report.append("="*80)
    report.append(f"Total Queries: {total}")
    report.append(f"✅ Passed: {passed} ({accuracy:.1f}%)")
    report.append(f"❌ Failed: {failed} ({100-accuracy:.1f}%)")
    
    # Category breakdown
    category_stats = {}
    for r in results:
        cat = r["category"]
        if cat not in category_stats:
            category_stats[cat] = {"total": 0, "passed": 0}
        category_stats[cat]["total"] += 1
        if r["passed"]:
            category_stats[cat]["passed"] += 1
    
    report.append(f"\n{'='*80}")
    report.append("📂 BY CATEGORY")
    report.append("="*80)
    for cat in sorted(category_stats.keys()):
        stats = category_stats[cat]
        cat_accuracy = (stats["passed"] / stats["total"] * 100) if stats["total"] > 0 else 0
        report.append(f"  {cat.upper()}: {stats['passed']}/{stats['total']} ({cat_accuracy:.1f}%)")
    
    # Failed queries details
    failed_results = [r for r in results if not r["passed"]]
    if failed_results:
        report.append(f"\n{'='*80}")
        report.append("❌ FAILED QUERIES")
        report.append("="*80)
        for r in failed_results:
            report.append(f"\n[Q{r['id']}] {r['question']}")
            report.append(f"Category: {r['category']}")
            if r.get("missing_components"):
                report.append(f"Issues: {', '.join(r['missing_components'])}")
            report.append(f"\n📝 Expected SQL:")
            report.append(f"   {r['expected_sql']}")
            if r.get("generated_sql"):
                report.append(f"\n🤖 Generated SQL:")
                report.append(f"   {r['generated_sql']}")
            if r.get("error"):
                report.append(f"\n⚠️  Error: {r['error']}")
            report.append("\n" + "-"*80)
    
    # Passed queries summary
    passed_results = [r for r in results if r["passed"]]
    if passed_results:
        report.append(f"\n{'='*80}")
        report.append(f"✅ PASSED QUERIES ({len(passed_results)})")
        report.append("="*80)
        for r in passed_results:
            report.append(f"  [Q{r['id']}] {r['question']}")
    
    report.append("\n" + "="*80)
    report.append(f"{'🎉 ALL TESTS PASSED!' if failed == 0 else '⚠️  SOME TESTS FAILED'}")
    report.append("="*80 + "\n")
    
    return "\n".join(report)


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Validate AI model SQL generation quality")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show detailed output")
    parser.add_argument("--output", "-o", help="Save report to file")
    args = parser.parse_args()
    
    # Run validation
    validation_data = run_validation(verbose=args.verbose)
    
    # Generate report
    report = generate_report(validation_data)
    
    # Print report
    print(report)
    
    # Save to file if requested
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"\n📄 Report saved to: {args.output}")
    
    # Exit with appropriate code
    sys.exit(0 if validation_data["failed"] == 0 else 1)


if __name__ == "__main__":
    main()

