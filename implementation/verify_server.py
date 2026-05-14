#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verification script for the SQLite MCP Server.
Tests all tools and resources to ensure they work correctly.
"""

import sys
import os
import io

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Add implementation directory to path
sys.path.insert(0, os.path.dirname(__file__))

from db import SQLiteAdapter, ValidationError
from init_db import create_database


def test_database_creation():
    """Test database creation and initialization."""
    print("\n=== Testing Database Creation ===")
    db_path = "lab.db"

    try:
        create_database(db_path)
        print("✓ Database created successfully")
        return True
    except Exception as e:
        print(f"✗ Database creation failed: {e}")
        return False


def test_adapter_connection():
    """Test database adapter connection."""
    print("\n=== Testing Adapter Connection ===")

    try:
        adapter = SQLiteAdapter("lab.db")
        adapter.connect()
        print("✓ Adapter connected successfully")

        tables = adapter.list_tables()
        print(f"✓ Found tables: {tables}")

        return True
    except Exception as e:
        print(f"✗ Adapter connection failed: {e}")
        return False


def test_search_tool():
    """Test the search tool."""
    print("\n=== Testing Search Tool ===")
    adapter = SQLiteAdapter("lab.db")

    tests = [
        {
            "name": "Search all students",
            "args": {"table": "students"},
            "should_pass": True
        },
        {
            "name": "Search students in cohort A1",
            "args": {"table": "students", "filters": {"cohort": "A1"}},
            "should_pass": True
        },
        {
            "name": "Search with column selection",
            "args": {"table": "students", "columns": ["name", "cohort"]},
            "should_pass": True
        },
        {
            "name": "Search with ordering",
            "args": {"table": "students", "order_by": "name", "descending": False},
            "should_pass": True
        },
        {
            "name": "Search with operator filter",
            "args": {"table": "enrollments", "filters": {"score": {"op": ">", "value": 90}}},
            "should_pass": True
        },
        {
            "name": "Search invalid table",
            "args": {"table": "invalid_table"},
            "should_pass": False
        },
        {
            "name": "Search invalid column",
            "args": {"table": "students", "columns": ["invalid_column"]},
            "should_pass": False
        }
    ]

    passed = 0
    for test in tests:
        try:
            result = adapter.search(**test["args"])
            if test["should_pass"]:
                print(f"✓ {test['name']}: {len(result)} rows")
                passed += 1
            else:
                print(f"✗ {test['name']}: Should have failed but passed")
        except ValidationError as e:
            if not test["should_pass"]:
                print(f"✓ {test['name']}: Correctly rejected ({e})")
                passed += 1
            else:
                print(f"✗ {test['name']}: {e}")
        except Exception as e:
            print(f"✗ {test['name']}: Unexpected error: {e}")

    print(f"\nSearch tests: {passed}/{len(tests)} passed")
    return passed == len(tests)


def test_insert_tool():
    """Test the insert tool."""
    print("\n=== Testing Insert Tool ===")
    adapter = SQLiteAdapter("lab.db")

    tests = [
        {
            "name": "Insert valid student",
            "args": {
                "table": "students",
                "values": {"name": "Test Student", "cohort": "A3", "email": "test@example.com"}
            },
            "should_pass": True
        },
        {
            "name": "Insert into invalid table",
            "args": {
                "table": "invalid_table",
                "values": {"name": "Test"}
            },
            "should_pass": False
        },
        {
            "name": "Insert with invalid column",
            "args": {
                "table": "students",
                "values": {"invalid_column": "value"}
            },
            "should_pass": False
        },
        {
            "name": "Insert empty values",
            "args": {
                "table": "students",
                "values": {}
            },
            "should_pass": False
        }
    ]

    passed = 0
    for test in tests:
        try:
            result = adapter.insert(**test["args"])
            if test["should_pass"]:
                print(f"✓ {test['name']}: Inserted with ID {result.get('id')}")
                passed += 1
            else:
                print(f"✗ {test['name']}: Should have failed but passed")
        except ValidationError as e:
            if not test["should_pass"]:
                print(f"✓ {test['name']}: Correctly rejected ({e})")
                passed += 1
            else:
                print(f"✗ {test['name']}: {e}")
        except Exception as e:
            print(f"✗ {test['name']}: Unexpected error: {e}")

    print(f"\nInsert tests: {passed}/{len(tests)} passed")
    return passed == len(tests)


def test_aggregate_tool():
    """Test the aggregate tool."""
    print("\n=== Testing Aggregate Tool ===")
    adapter = SQLiteAdapter("lab.db")

    tests = [
        {
            "name": "Count all students",
            "args": {"table": "students", "metric": "count"},
            "should_pass": True
        },
        {
            "name": "Average score",
            "args": {"table": "enrollments", "metric": "avg", "column": "score"},
            "should_pass": True
        },
        {
            "name": "Count with group by",
            "args": {"table": "enrollments", "metric": "count", "group_by": "course_id"},
            "should_pass": True
        },
        {
            "name": "Sum with filters",
            "args": {"table": "enrollments", "metric": "sum", "column": "score", "filters": {"student_id": 1}},
            "should_pass": True
        },
        {
            "name": "Invalid metric",
            "args": {"table": "students", "metric": "invalid_metric"},
            "should_pass": False
        },
        {
            "name": "AVG without column",
            "args": {"table": "enrollments", "metric": "avg"},
            "should_pass": False
        },
        {
            "name": "Aggregate on invalid table",
            "args": {"table": "invalid_table", "metric": "count"},
            "should_pass": False
        }
    ]

    passed = 0
    for test in tests:
        try:
            result = adapter.aggregate(**test["args"])
            if test["should_pass"]:
                print(f"✓ {test['name']}: {result}")
                passed += 1
            else:
                print(f"✗ {test['name']}: Should have failed but passed")
        except ValidationError as e:
            if not test["should_pass"]:
                print(f"✓ {test['name']}: Correctly rejected ({e})")
                passed += 1
            else:
                print(f"✗ {test['name']}: {e}")
        except Exception as e:
            print(f"✗ {test['name']}: Unexpected error: {e}")

    print(f"\nAggregate tests: {passed}/{len(tests)} passed")
    return passed == len(tests)


def test_schema_resources():
    """Test schema resources."""
    print("\n=== Testing Schema Resources ===")
    adapter = SQLiteAdapter("lab.db")

    try:
        # Test full database schema
        tables = adapter.list_tables()
        print(f"✓ Database has {len(tables)} tables: {tables}")

        # Test individual table schemas
        for table in tables:
            schema = adapter.get_table_schema(table)
            print(f"✓ Table '{table}' has {len(schema)} columns")

        # Test invalid table
        try:
            adapter.get_table_schema("invalid_table")
            print("✗ Should have rejected invalid table")
            return False
        except ValidationError:
            print("✓ Correctly rejected invalid table")

        return True
    except Exception as e:
        print(f"✗ Schema resource test failed: {e}")
        return False


def main():
    """Run all verification tests."""
    print("=" * 60)
    print("SQLite MCP Server Verification")
    print("=" * 60)

    results = []

    results.append(("Database Creation", test_database_creation()))
    results.append(("Adapter Connection", test_adapter_connection()))
    results.append(("Search Tool", test_search_tool()))
    results.append(("Insert Tool", test_insert_tool()))
    results.append(("Aggregate Tool", test_aggregate_tool()))
    results.append(("Schema Resources", test_schema_resources()))

    print("\n" + "=" * 60)
    print("Verification Summary")
    print("=" * 60)

    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {name}")

    total_passed = sum(1 for _, passed in results if passed)
    total_tests = len(results)

    print(f"\nTotal: {total_passed}/{total_tests} test suites passed")

    if total_passed == total_tests:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print("\n⚠️  Some tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
