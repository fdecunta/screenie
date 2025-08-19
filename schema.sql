CREATE TABLE IF NOT EXISTS input_files (
    file_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    content BLOB NOT NULL UNIQUE,  
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS papers (
    paper_id INTEGER PRIMARY KEY,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    title TEXT NOT NULL,
    authors TEXT NOT NULL, 
    year INTEGER NOT NULL,
    abstract TEXT NOT NULL,
    url TEXT NOT NULL UNIQUE,
    doi TEXT UNIQUE,
    file_id INTEGER NOT NULL,  
    FOREIGN KEY (file_id) REFERENCES input_files (file_id)
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
    verdict INTEGER NOT NULL CHECK (verdict IN (-1, 0, 1)),  
    reason TEXT NOT NULL,
    human_validated INTEGER NOT NULL DEFAULT 0 CHECK (human_validated IN (0, 1)),
    input_tokens INTEGER NOT NULL DEFAULT 0,
    output_tokens INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (paper_id) REFERENCES papers (paper_id),
    FOREIGN KEY (criteria_id) REFERENCES criteria (criteria_id)
);
