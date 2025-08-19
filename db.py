import sqlite3

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
