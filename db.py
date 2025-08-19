import click
import os
import sqlite3
import sys

def init_db(db_name: str, sql_file="schema.sql"):
    conn = sqlite3.connect(db_name)
    cur = conn.cursor()

    with open(sql_file, "r", encoding="utf-8") as f:
        cur.executescript(f.read())
    conn.commit()

    # Test if it was created ok
    try:
        cur.execute("SELECT * FROM input_files;")
        _ = cur.fetchone()
        success = True
    except sqlite3.OperationalError:
        success = False

    conn.close()

    return success


def insert_file(db_path: str, file_path: str):
    filename = os.path.basename(file_path)

    fmt_filename = click.format_filename(filename)
    fmt_database = click.format_filename(os.path.basename(db_path))

    # read file as bytes
    with open(file_path, "rb") as f:
        file_bytes = f.read()

    # use context manager for connection
    with sqlite3.connect(db_path) as con:
        cur = con.cursor()
        try:
            cur.execute("""
                INSERT INTO input_files (name, content)
                VALUES (?, ?)
            """, (filename, file_bytes))
            con.commit()
            click.secho(f"Added {fmt_filename} to {fmt_database}", fg="green")
        except sqlite3.IntegrityError as e:
            msg = str(e)
            if "UNIQUE constraint" in msg:
                click.secho(f"File {fmt_filename} already exists in the database.", fg="red", err=True)
            else:
                click.secho(f"Failed to import {fmt_filename}: {msg}", fg="red", err=True)
            sys.exit(1)
        except sqlite3.DatabaseError as e:
            click.secho(f"Database error: {e}", fg="red", err=True)
            sys.exit(1)

