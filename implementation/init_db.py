import sqlite3
import os

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    cohort TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS courses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    credits INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS enrollments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    course_id INTEGER NOT NULL,
    score REAL,
    FOREIGN KEY (student_id) REFERENCES students(id),
    FOREIGN KEY (course_id) REFERENCES courses(id),
    UNIQUE(student_id, course_id)
);
"""

SEED_SQL = """
INSERT OR IGNORE INTO students (name, cohort, email) VALUES
    ('Truong Minh Phuoc', 'A1', 'phuoc.truong@vinuni.edu.vn'),
    ('Nguyen Van A', 'A1', 'a.nguyen@vinuni.edu.vn'),
    ('Tran Thi B', 'A2', 'b.tran@vinuni.edu.vn'),
    ('Le Van C', 'A2', 'c.le@vinuni.edu.vn'),
    ('Pham Thi D', 'A1', 'd.pham@vinuni.edu.vn');

INSERT OR IGNORE INTO courses (code, name, credits) VALUES
    ('CS101', 'Introduction to Programming', 3),
    ('CS201', 'Data Structures', 4),
    ('CS301', 'Database Systems', 3),
    ('CS401', 'Machine Learning', 4);

INSERT OR IGNORE INTO enrollments (student_id, course_id, score) VALUES
    (1, 1, 95.5),
    (1, 2, 88.0),
    (2, 1, 92.0),
    (2, 3, 85.5),
    (3, 2, 78.0),
    (3, 3, 90.0),
    (4, 1, 88.5),
    (4, 4, 92.0),
    (5, 2, 95.0),
    (5, 3, 87.5);
"""


def create_database(db_path="lab.db"):
    """
    Create and initialize the SQLite database with schema and seed data.

    Args:
        db_path: Path to the database file

    Returns:
        str: Absolute path to the created database
    """
    # Remove existing database if it exists
    if os.path.exists(db_path):
        os.remove(db_path)

    # Create new database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Execute schema SQL
    cursor.executescript(SCHEMA_SQL)

    # Execute seed SQL
    cursor.executescript(SEED_SQL)

    # Commit changes
    conn.commit()
    conn.close()

    # Return absolute path
    abs_path = os.path.abspath(db_path)
    print(f"Database created successfully at: {abs_path}")
    return abs_path


if __name__ == "__main__":
    create_database()
