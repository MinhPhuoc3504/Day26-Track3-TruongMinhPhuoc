import sqlite3
import re


class ValidationError(Exception):
    """Raised when a request cannot be safely executed."""
    pass


class SQLiteAdapter:
    """
    SQLite database adapter with validation and safe query execution.
    """

    def __init__(self, db_path):
        self.db_path = db_path
        self._conn = None

    def connect(self):
        """Open SQLite connection with row_factory enabled."""
        if self._conn is None:
            self._conn = sqlite3.connect(self.db_path)
            self._conn.row_factory = sqlite3.Row
        return self._conn

    def close(self):
        """Close the database connection."""
        if self._conn:
            self._conn.close()
            self._conn = None

    def _validate_identifier(self, identifier):
        """
        Validate that an identifier (table or column name) is safe.
        Only allows alphanumeric characters and underscores.
        """
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', identifier):
            raise ValidationError(f"Invalid identifier: {identifier}")
        return identifier

    def list_tables(self):
        """Query sqlite_master and return non-internal tables."""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
        )
        return [row[0] for row in cursor.fetchall()]

    def get_table_schema(self, table):
        """Run PRAGMA table_info(table) and return normalized result."""
        self._validate_identifier(table)

        # Check if table exists
        if table not in self.list_tables():
            raise ValidationError(f"Table '{table}' does not exist")

        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA table_info({table})")

        columns = []
        for row in cursor.fetchall():
            columns.append({
                "name": row[1],
                "type": row[2],
                "notnull": bool(row[3]),
                "default": row[4],
                "pk": bool(row[5])
            })
        return columns

    def search(self, table, columns=None, filters=None, limit=20, offset=0, order_by=None, descending=False):
        """
        Execute a SELECT query with filters, ordering, and pagination.

        Args:
            table: Table name
            columns: List of column names to select (None = all)
            filters: Dict of {column: value} or {column: {"op": operator, "value": value}}
            limit: Maximum number of rows to return
            offset: Number of rows to skip
            order_by: Column name to order by
            descending: If True, order descending

        Returns:
            List of dicts representing rows
        """
        # Validate table
        self._validate_identifier(table)
        if table not in self.list_tables():
            raise ValidationError(f"Table '{table}' does not exist")

        # Get table schema for validation
        schema = self.get_table_schema(table)
        valid_columns = {col["name"] for col in schema}

        # Validate and build column list
        if columns:
            for col in columns:
                self._validate_identifier(col)
                if col not in valid_columns:
                    raise ValidationError(f"Column '{col}' does not exist in table '{table}'")
            col_list = ", ".join(columns)
        else:
            col_list = "*"

        # Build query
        query = f"SELECT {col_list} FROM {table}"
        params = []

        # Build WHERE clause
        if filters:
            where_clauses = []
            for col, condition in filters.items():
                self._validate_identifier(col)
                if col not in valid_columns:
                    raise ValidationError(f"Column '{col}' does not exist in table '{table}'")

                # Support both simple value and operator dict
                if isinstance(condition, dict):
                    op = condition.get("op", "=")
                    value = condition.get("value")

                    # Validate operator
                    allowed_ops = ["=", "!=", "<", ">", "<=", ">=", "LIKE", "IN"]
                    if op.upper() not in allowed_ops:
                        raise ValidationError(f"Unsupported operator: {op}")

                    if op.upper() == "IN":
                        if not isinstance(value, list):
                            raise ValidationError("IN operator requires a list value")
                        placeholders = ",".join(["?" for _ in value])
                        where_clauses.append(f"{col} IN ({placeholders})")
                        params.extend(value)
                    else:
                        where_clauses.append(f"{col} {op} ?")
                        params.append(value)
                else:
                    where_clauses.append(f"{col} = ?")
                    params.append(condition)

            if where_clauses:
                query += " WHERE " + " AND ".join(where_clauses)

        # Add ORDER BY
        if order_by:
            self._validate_identifier(order_by)
            if order_by not in valid_columns:
                raise ValidationError(f"Column '{order_by}' does not exist in table '{table}'")
            query += f" ORDER BY {order_by}"
            if descending:
                query += " DESC"

        # Add LIMIT and OFFSET
        query += f" LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        # Execute query
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute(query, params)

        # Convert rows to dicts
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    def insert(self, table, values):
        """
        Execute an INSERT statement.

        Args:
            table: Table name
            values: Dict of {column: value}

        Returns:
            Dict with inserted values and generated ID
        """
        # Validate table
        self._validate_identifier(table)
        if table not in self.list_tables():
            raise ValidationError(f"Table '{table}' does not exist")

        # Validate values is not empty
        if not values:
            raise ValidationError("Insert values cannot be empty")

        # Get table schema for validation
        schema = self.get_table_schema(table)
        valid_columns = {col["name"] for col in schema}

        # Validate columns
        for col in values.keys():
            self._validate_identifier(col)
            if col not in valid_columns:
                raise ValidationError(f"Column '{col}' does not exist in table '{table}'")

        # Build INSERT statement
        columns = list(values.keys())
        placeholders = ",".join(["?" for _ in columns])
        col_list = ",".join(columns)

        query = f"INSERT INTO {table} ({col_list}) VALUES ({placeholders})"
        params = [values[col] for col in columns]

        # Execute insert
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()

        # Get inserted ID
        inserted_id = cursor.lastrowid

        # Return inserted payload with ID
        result = dict(values)
        result["id"] = inserted_id
        return result

    def aggregate(self, table, metric, column=None, filters=None, group_by=None):
        """
        Execute an aggregate query (COUNT, AVG, SUM, MIN, MAX).

        Args:
            table: Table name
            metric: Aggregate function (count, avg, sum, min, max)
            column: Column name to aggregate (required for avg, sum, min, max)
            filters: Dict of {column: value} for WHERE clause
            group_by: Column name to group by

        Returns:
            List of dicts with aggregate results
        """
        # Validate table
        self._validate_identifier(table)
        if table not in self.list_tables():
            raise ValidationError(f"Table '{table}' does not exist")

        # Validate metric
        allowed_metrics = ["count", "avg", "sum", "min", "max"]
        metric_lower = metric.lower()
        if metric_lower not in allowed_metrics:
            raise ValidationError(f"Unsupported metric: {metric}. Allowed: {allowed_metrics}")

        # Get table schema for validation
        schema = self.get_table_schema(table)
        valid_columns = {col["name"] for col in schema}

        # Build aggregate expression
        if metric_lower == "count":
            if column:
                self._validate_identifier(column)
                if column not in valid_columns:
                    raise ValidationError(f"Column '{column}' does not exist in table '{table}'")
                agg_expr = f"COUNT({column})"
            else:
                agg_expr = "COUNT(*)"
        else:
            # avg, sum, min, max require a column
            if not column:
                raise ValidationError(f"Metric '{metric}' requires a column")
            self._validate_identifier(column)
            if column not in valid_columns:
                raise ValidationError(f"Column '{column}' does not exist in table '{table}'")
            agg_expr = f"{metric_lower.upper()}({column})"

        # Build SELECT clause
        if group_by:
            self._validate_identifier(group_by)
            if group_by not in valid_columns:
                raise ValidationError(f"Column '{group_by}' does not exist in table '{table}'")
            query = f"SELECT {group_by}, {agg_expr} AS value FROM {table}"
        else:
            query = f"SELECT {agg_expr} AS value FROM {table}"

        params = []

        # Build WHERE clause
        if filters:
            where_clauses = []
            for col, value in filters.items():
                self._validate_identifier(col)
                if col not in valid_columns:
                    raise ValidationError(f"Column '{col}' does not exist in table '{table}'")
                where_clauses.append(f"{col} = ?")
                params.append(value)

            if where_clauses:
                query += " WHERE " + " AND ".join(where_clauses)

        # Add GROUP BY
        if group_by:
            query += f" GROUP BY {group_by}"

        # Execute query
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute(query, params)

        # Convert rows to dicts
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
