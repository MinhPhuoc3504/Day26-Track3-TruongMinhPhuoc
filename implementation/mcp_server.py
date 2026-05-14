from fastmcp import FastMCP
import json
import os
from db import SQLiteAdapter, ValidationError

# Create the server object
mcp = FastMCP("SQLite Lab MCP Server")

# Initialize database adapter
DB_PATH = os.path.join(os.path.dirname(__file__), "lab.db")
adapter = SQLiteAdapter(DB_PATH)


@mcp.tool(name="search")
def search(
    table: str,
    filters: dict = None,
    columns: list = None,
    limit: int = 20,
    offset: int = 0,
    order_by: str = None,
    descending: bool = False
):
    """
    Search for rows in a table with optional filters, column selection, ordering, and pagination.

    Args:
        table: Name of the table to search
        filters: Dictionary of filters {column: value} or {column: {"op": operator, "value": value}}
        columns: List of column names to return (default: all columns)
        limit: Maximum number of rows to return (default: 20)
        offset: Number of rows to skip (default: 0)
        order_by: Column name to order results by
        descending: If True, order results in descending order (default: False)

    Returns:
        Dictionary with rows and metadata

    Example:
        search("students", filters={"cohort": "A1"}, limit=10)
        search("enrollments", filters={"score": {"op": ">", "value": 90}})
    """
    try:
        rows = adapter.search(
            table=table,
            columns=columns,
            filters=filters,
            limit=limit,
            offset=offset,
            order_by=order_by,
            descending=descending
        )

        return {
            "success": True,
            "table": table,
            "count": len(rows),
            "rows": rows,
            "limit": limit,
            "offset": offset
        }
    except ValidationError as e:
        return {
            "success": False,
            "error": str(e)
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}"
        }


@mcp.tool(name="insert")
def insert(table: str, values: dict):
    """
    Insert a new row into a table.

    Args:
        table: Name of the table to insert into
        values: Dictionary of column-value pairs to insert

    Returns:
        Dictionary with inserted values including generated ID

    Example:
        insert("students", {"name": "John Doe", "cohort": "A3", "email": "john@example.com"})
    """
    try:
        result = adapter.insert(table=table, values=values)

        return {
            "success": True,
            "table": table,
            "inserted": result
        }
    except ValidationError as e:
        return {
            "success": False,
            "error": str(e)
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}"
        }


@mcp.tool(name="aggregate")
def aggregate(
    table: str,
    metric: str,
    column: str = None,
    filters: dict = None,
    group_by: str = None
):
    """
    Perform aggregate operations on a table (COUNT, AVG, SUM, MIN, MAX).

    Args:
        table: Name of the table to aggregate
        metric: Aggregate function (count, avg, sum, min, max)
        column: Column name to aggregate (required for avg, sum, min, max)
        filters: Dictionary of filters {column: value} for WHERE clause
        group_by: Column name to group results by

    Returns:
        Dictionary with aggregate results

    Example:
        aggregate("students", metric="count")
        aggregate("enrollments", metric="avg", column="score", group_by="course_id")
        aggregate("enrollments", metric="count", filters={"score": {"op": ">", "value": 90}})
    """
    try:
        rows = adapter.aggregate(
            table=table,
            metric=metric,
            column=column,
            filters=filters,
            group_by=group_by
        )

        return {
            "success": True,
            "table": table,
            "metric": metric,
            "column": column,
            "group_by": group_by,
            "results": rows
        }
    except ValidationError as e:
        return {
            "success": False,
            "error": str(e)
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}"
        }


@mcp.resource("schema://database")
def database_schema():
    """
    Get the complete database schema including all tables and their columns.

    Returns:
        JSON text describing the full database schema
    """
    try:
        tables = adapter.list_tables()
        schema = {}

        for table in tables:
            schema[table] = adapter.get_table_schema(table)

        return json.dumps(schema, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.resource("schema://table/{table_name}")
def table_schema(table_name: str):
    """
    Get the schema for a specific table.

    Args:
        table_name: Name of the table

    Returns:
        JSON text describing the table schema
    """
    try:
        schema = adapter.get_table_schema(table_name)
        return json.dumps({
            "table": table_name,
            "columns": schema
        }, indent=2)
    except ValidationError as e:
        return json.dumps({"error": str(e)})
    except Exception as e:
        return json.dumps({"error": f"Unexpected error: {str(e)}"})


if __name__ == "__main__":
    # Initialize database if it doesn't exist
    if not os.path.exists(DB_PATH):
        print("Database not found. Creating database...")
        from init_db import create_database
        create_database(DB_PATH)

    # Run the MCP server
    mcp.run()
