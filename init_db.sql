CREATE TABLE IF NOT EXISTS papers (
    paper_id INTEGER PRIMARY KEY,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    title TEXT NOT NULL,
    authors TEXT NOT NULL, 
    year INTEGER NOT NULL,
    abstract TEXT NOT NULL,
    url TEXT NOT NULL,
    doi TEXT,
    source TEXT
);

CREATE TABLE IF NOT EXISTS criteria (
    criteria_id INTEGER PRIMARY KEY,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    text TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS screener (
    suggestion_id INTEGER PRIMARY KEY,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    criteria_id INTEGER NOT NULL,
    paper_id INTEGER NOT NULL,
    veredict INTEGER NOT NULL CHECK (veredict IN (-1, 0, 1)),
    reason TEXT NOT NULL,
    human_validated INTEGER NOT NULL DEFAULT 0 CHECK (human_validated IN (0, 1)),
    FOREIGN KEY (paper_id) REFERENCES papers (paper_id),
    FOREIGN KEY (criteria_id) REFERENCES criteria (criteria_id)
);
