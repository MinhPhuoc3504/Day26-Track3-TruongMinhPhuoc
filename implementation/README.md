# SQLite MCP Server Lab - Implementation

**Student:** Trương Minh Phước  
**Student ID:** 2A202600330  
**Course:** VinUni - MCP Integration Lab

## Overview

This project implements a Model Context Protocol (MCP) server using FastMCP that exposes a SQLite database through three main tools: `search`, `insert`, and `aggregate`. The server also provides schema information through MCP resources.

## Features

### Tools
1. **search** - Query database tables with filters, column selection, ordering, and pagination
2. **insert** - Insert new rows into tables with validation
3. **aggregate** - Perform aggregate operations (COUNT, AVG, SUM, MIN, MAX) with optional grouping

### Resources
1. **schema://database** - Full database schema for all tables
2. **schema://table/{table_name}** - Schema for a specific table

### Database Schema
- **students** - Student information (id, name, cohort, email)
- **courses** - Course information (id, code, name, credits)
- **enrollments** - Student enrollments with scores (id, student_id, course_id, score)

## Setup Instructions

### Prerequisites
- Python 3.8 or higher
- Virtual environment (recommended)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd Day26-Track3-MCP-tool-integration
```

2. Create and activate virtual environment:
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Initialize the database:
```bash
cd implementation
python init_db.py
```

## Running the Server

### Start the MCP Server
```bash
cd implementation
python mcp_server.py
```

The server will run in stdio mode by default, suitable for MCP client integration.

### Verify the Server
Run the verification script to test all functionality:
```bash
cd implementation
python verify_server.py
```

## Testing with MCP Inspector

To test the server with MCP Inspector:

```bash
npx @modelcontextprotocol/inspector python implementation/mcp_server.py
```

This will open a web interface where you can:
- Discover available tools and resources
- Test tool calls with different parameters
- View schema resources
- Test error handling

## Client Configuration Examples

### Claude Code

Add to your `.mcp.json` or use `claude mcp add`:

```json
{
  "mcpServers": {
    "sqlite-lab": {
      "command": "python",
      "args": ["C:/Users/admin/VINUNI/Day26-Track3-MCP-tool-integration/implementation/mcp_server.py"],
      "description": "SQLite lab FastMCP server"
    }
  }
}
```

### Gemini CLI

```bash
gemini mcp add sqlite-lab /path/to/python /path/to/implementation/mcp_server.py --description "SQLite lab FastMCP server" --timeout 10000
gemini mcp list
```

Test with:
```bash
gemini --allowed-mcp-server-names sqlite-lab --yolo -p "Search all students in cohort A1"
```

## Example Usage

### Search Examples

1. Search all students:
```json
{
  "table": "students"
}
```

2. Search students in cohort A1:
```json
{
  "table": "students",
  "filters": {"cohort": "A1"}
}
```

3. Search with operator:
```json
{
  "table": "enrollments",
  "filters": {"score": {"op": ">", "value": 90}}
}
```

4. Search with ordering:
```json
{
  "table": "students",
  "order_by": "name",
  "descending": false
}
```

### Insert Examples

1. Insert a new student:
```json
{
  "table": "students",
  "values": {
    "name": "John Doe",
    "cohort": "A3",
    "email": "john.doe@example.com"
  }
}
```

2. Insert a new enrollment:
```json
{
  "table": "enrollments",
  "values": {
    "student_id": 1,
    "course_id": 3,
    "score": 95.0
  }
}
```

### Aggregate Examples

1. Count all students:
```json
{
  "table": "students",
  "metric": "count"
}
```

2. Average score:
```json
{
  "table": "enrollments",
  "metric": "avg",
  "column": "score"
}
```

3. Count enrollments by course:
```json
{
  "table": "enrollments",
  "metric": "count",
  "group_by": "course_id"
}
```

4. Average score by cohort:
```json
{
  "table": "enrollments",
  "metric": "avg",
  "column": "score",
  "group_by": "student_id"
}
```

### Resource Examples

1. Get full database schema:
   - Resource URI: `schema://database`

2. Get specific table schema:
   - Resource URI: `schema://table/students`
   - Resource URI: `schema://table/courses`
   - Resource URI: `schema://table/enrollments`

## Error Handling

The server validates all requests and returns clear error messages for:
- Unknown table names
- Unknown column names
- Unsupported filter operators
- Invalid aggregate requests
- Empty insert values
- SQL injection attempts

Example error response:
```json
{
  "success": false,
  "error": "Table 'invalid_table' does not exist"
}
```

## Project Structure

```
implementation/
├── db.py              # SQLite adapter with validation
├── init_db.py         # Database initialization and seeding
├── mcp_server.py      # FastMCP server with tools and resources
├── verify_server.py   # Verification and testing script
└── lab.db            # SQLite database (generated)
```

## Security Features

- **SQL Injection Prevention**: All queries use parameterized statements
- **Identifier Validation**: Table and column names are validated with regex
- **Operator Whitelisting**: Only safe operators are allowed in filters
- **Schema Validation**: All operations validate against actual database schema

## Testing Checklist

- [x] Server starts correctly
- [x] Three tools are discoverable (search, insert, aggregate)
- [x] Schema resources are discoverable
- [x] Valid tool calls return useful results
- [x] Invalid tool calls return clear errors
- [x] Database validation prevents SQL injection
- [x] All edge cases are handled properly

## Demo Video

[Link to demo video - to be added]

## References

- FastMCP Documentation: https://gofastmcp.com/v2/getting-started/quickstart
- MCP Inspector: https://modelcontextprotocol.io/docs/tools/inspector
- Claude Code MCP: https://code.claude.com/docs/en/mcp

## License

This project is created for educational purposes as part of VinUni coursework.
