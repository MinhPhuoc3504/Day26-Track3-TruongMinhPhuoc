# Testing Guide

## Quick Start

### 1. Verify Installation
```bash
cd implementation
python verify_server.py
```

Expected output: All 6 test suites should pass ✓

### 2. Test with MCP Inspector

Install and run MCP Inspector:
```bash
npx @modelcontextprotocol/inspector python implementation/mcp_server.py
```

This will open a web interface at http://localhost:5173

### 3. Test Tools in Inspector

#### Test Search Tool
```json
{
  "table": "students",
  "filters": {"cohort": "A1"},
  "limit": 10
}
```

Expected: Returns students in cohort A1

#### Test Insert Tool
```json
{
  "table": "students",
  "values": {
    "name": "New Student",
    "cohort": "A3",
    "email": "new.student@example.com"
  }
}
```

Expected: Returns inserted record with generated ID

#### Test Aggregate Tool
```json
{
  "table": "enrollments",
  "metric": "avg",
  "column": "score",
  "group_by": "course_id"
}
```

Expected: Returns average scores grouped by course

### 4. Test Resources in Inspector

- Click on "Resources" tab
- You should see:
  - `schema://database` - Full database schema
  - `schema://table/students` - Students table schema
  - `schema://table/courses` - Courses table schema
  - `schema://table/enrollments` - Enrollments table schema

### 5. Test Error Handling

Try these invalid requests to verify error handling:

#### Invalid Table
```json
{
  "table": "invalid_table"
}
```

Expected: Error message "Table 'invalid_table' does not exist"

#### Invalid Column
```json
{
  "table": "students",
  "columns": ["invalid_column"]
}
```

Expected: Error message about invalid column

#### Invalid Operator
```json
{
  "table": "students",
  "filters": {"name": {"op": "INVALID", "value": "test"}}
}
```

Expected: Error message about unsupported operator

## Integration with Claude Code

### Add Server to Claude Code

Option 1: Using CLI
```bash
claude mcp add sqlite-lab python C:\Users\admin\VINUNI\Day26-Track3-MCP-tool-integration\implementation\mcp_server.py
```

Option 2: Manual configuration
Copy `.mcp.json` to your project root or add to Claude Code settings.

### Test with Claude Code

After adding the server, you can ask Claude:
- "Search all students in cohort A1"
- "Insert a new student named John Doe in cohort A3"
- "What's the average score across all enrollments?"
- "Show me the database schema"

## Sample Queries

### Search Examples

1. All students:
```json
{"table": "students"}
```

2. Students in cohort A1:
```json
{"table": "students", "filters": {"cohort": "A1"}}
```

3. Enrollments with score > 90:
```json
{
  "table": "enrollments",
  "filters": {"score": {"op": ">", "value": 90}}
}
```

4. Ordered by name:
```json
{
  "table": "students",
  "order_by": "name",
  "descending": false
}
```

### Insert Examples

1. New student:
```json
{
  "table": "students",
  "values": {
    "name": "Jane Smith",
    "cohort": "A2",
    "email": "jane.smith@example.com"
  }
}
```

2. New course:
```json
{
  "table": "courses",
  "values": {
    "code": "CS501",
    "name": "Advanced AI",
    "credits": 4
  }
}
```

### Aggregate Examples

1. Count students:
```json
{"table": "students", "metric": "count"}
```

2. Average score:
```json
{"table": "enrollments", "metric": "avg", "column": "score"}
```

3. Count by cohort:
```json
{
  "table": "students",
  "metric": "count",
  "group_by": "cohort"
}
```

4. Max score per course:
```json
{
  "table": "enrollments",
  "metric": "max",
  "column": "score",
  "group_by": "course_id"
}
```

## Troubleshooting

### Server won't start
- Check Python version: `python --version` (should be 3.8+)
- Verify virtual environment is activated
- Reinstall dependencies: `pip install -r requirements.txt`

### Database not found
- Run `python implementation/init_db.py` to create database
- Check that `lab.db` exists in `implementation/` directory

### MCP Inspector connection issues
- Ensure no other process is using port 5173
- Try restarting the inspector
- Check that the Python path is correct

### Claude Code integration issues
- Verify the path in `.mcp.json` is absolute and correct
- Restart Claude Code after adding the server
- Check Claude Code logs for error messages

## Expected Results Summary

✓ Server starts without errors
✓ All 3 tools are discoverable (search, insert, aggregate)
✓ Schema resources are accessible
✓ Valid requests return correct data
✓ Invalid requests return clear error messages
✓ No SQL injection vulnerabilities
✓ All validation rules are enforced
