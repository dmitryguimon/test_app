import sqlite3
from datetime import datetime

DB_PATH = "comments.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            author TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TEXT NOT NULL,
            parent_id INTEGER,
            FOREIGN KEY(parent_id) REFERENCES comments(id)
        )
    """
    )
    conn.commit()
    conn.close()

def get_all_comments():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, author, content, created_at, parent_id FROM comments")
    rows = c.fetchall()
    conn.close()
    # Build a tree structure
    comments = []
    lookup = {}
    for row in rows:
        comment = {
            "id": row[0],
            "author": row[1],
            "content": row[2],
            "created_at": row[3],
            "parent_id": row[4],
            "children": []
        }
        lookup[comment["id"]] = comment
        if comment["parent_id"]:
            parent = lookup.get(comment["parent_id"])
            if parent:
                parent["children"].append(comment)
        else:
            comments.append(comment)
    return comments

def add_comment(author, content, parent_id=None):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "INSERT INTO comments (author, content, created_at, parent_id) VALUES (?, ?, ?, ?)",
        (author, content, datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"), parent_id)
    )
    conn.commit()
    conn.close()