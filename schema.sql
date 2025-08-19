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

CREATE TABLE IF NOT EXISTS llm_calls (
    call_id INTEGER PRIMARY KEY,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    model TEXT NOT NULL,
    prompt TEXT NOT NULL,
    input_tokens INTEGER NOT NULL,
    output_tokens INTEGER NOT NULL,
    criteria_id INTEGER NOT NULL,
    paper_id INTEGER NOT NULL,
    full_response TEXT NOT NULL,
    FOREIGN KEY (criteria_id) REFERENCES criteria (criteria_id),
    FOREIGN KEY (paper_id) REFERENCES papers (paper_id)
);

CREATE TABLE IF NOT EXISTS screening_results (
    suggestion_id INTEGER PRIMARY KEY,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    criteria_id INTEGER NOT NULL,
    paper_id INTEGER NOT NULL,
    verdict INTEGER NOT NULL CHECK (verdict IN (0, 1)),  -- 0: Reject, 1: Accept
    reason TEXT NOT NULL,
    human_validated INTEGER NOT NULL DEFAULT 0 CHECK (human_validated IN (0, 1)), -- 0:Not validated, 1:Validated
    call_id INTEGER NOT NULL,
    FOREIGN KEY (paper_id) REFERENCES papers (paper_id),
    FOREIGN KEY (criteria_id) REFERENCES criteria (criteria_id),
    FOREIGN KEY (call_id) REFERENCES llm_calls (call_id)
);
