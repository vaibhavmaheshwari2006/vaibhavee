import sqlite3
from collections import defaultdict, Counter

def get_connection(db_path="fingerprints.db"):
    return sqlite3.connect(db_path)

def init_db(db_path="fingerprints.db"):
    """
    Initialize SQLite database tables and indices.
    """
    conn = get_connection(db_path)
    cursor = conn.cursor()
    
    # Create songs table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS songs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT UNIQUE NOT NULL
    )
    """)
    
    # Create fingerprints table (WITHOUT ROWID with compound primary key for minimal size)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS fingerprints (
        hash INTEGER NOT NULL,
        song_id INTEGER NOT NULL,
        offset INTEGER NOT NULL,
        PRIMARY KEY (hash, song_id, offset)
    ) WITHOUT ROWID
    """)
    
    conn.commit()
    conn.close()

def clear_db(db_path="fingerprints.db"):
    """
    Drop database tables to re-index.
    """
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS fingerprints")
    cursor.execute("DROP TABLE IF EXISTS songs")
    conn.commit()
    conn.close()
    init_db(db_path)

def store_song_fingerprints(db_path, song_title, fingerprints):
    """
    Store fingerprints for a single song.
    fingerprints is a list of tuples: (hash_str, offset_t1)
    """
    conn = get_connection(db_path)
    cursor = conn.cursor()
    
    # Insert song and get its ID
    try:
        cursor.execute("INSERT INTO songs (title) VALUES (?)", (song_title,))
        song_id = cursor.lastrowid
    except sqlite3.IntegrityError:
        # Song already indexed, retrieve its ID
        cursor.execute("SELECT id FROM songs WHERE title = ?", (song_title,))
        song_id = cursor.fetchone()[0]
        
        # Remove old fingerprints for this song
        cursor.execute("DELETE FROM fingerprints WHERE song_id = ?", (song_id,))
        
    # Bulk insert fingerprints
    data_to_insert = [(int(h), song_id, int(offset)) for h, offset in fingerprints]
    cursor.executemany("INSERT OR IGNORE INTO fingerprints (hash, song_id, offset) VALUES (?, ?, ?)", data_to_insert)
    
    conn.commit()
    conn.close()
    return song_id

def match_fingerprints(db_path, query_fingerprints):
    """
    Match query fingerprints against the database.
    query_fingerprints is a list of tuples: (hash_str, offset_t1)
    
    Returns:
        matches: a dictionary mapping song_id to a list of offset differences
        song_names: a dictionary mapping song_id to song_title
    """
    conn = get_connection(db_path)
    cursor = conn.cursor()
    
    # Map song_id -> title
    cursor.execute("SELECT id, title FROM songs")
    song_names = {row[0]: row[1] for row in cursor.fetchall()}
    
    # Group query offsets by hash
    query_by_hash = defaultdict(list)
    for hash_val, t_query in query_fingerprints:
        query_by_hash[int(hash_val)].append(int(t_query))
        
    hashes = list(query_by_hash.keys())
    matches = defaultdict(list)
    
    # Query in chunks of 999 parameters (SQLite limit)
    chunk_size = 999
    for i in range(0, len(hashes), chunk_size):
        chunk = hashes[i:i+chunk_size]
        placeholders = ",".join(["?"] * len(chunk))
        query = f"SELECT hash, song_id, offset FROM fingerprints WHERE hash IN ({placeholders})"
        cursor.execute(query, chunk)
        
        for hash_val, song_id, t_db in cursor.fetchall():
            for t_query in query_by_hash[hash_val]:
                diff = int(t_db) - int(t_query)
                matches[song_id].append(diff)
                
    conn.close()
    return matches, song_names

def score_matches(matches):
    """
    Score matched song records using offset alignment histograms.
    Returns:
        sorted_scores: list of tuples (song_id, peak_score, total_matches, best_offset)
                       sorted by peak_score descending
    """
    scores = []
    for song_id, diffs in matches.items():
        if not diffs:
            continue
        counts = Counter(diffs)
        best_offset, peak_score = counts.most_common(1)[0]
        total_matches = len(diffs)
        scores.append((song_id, peak_score, total_matches, best_offset))
        
    # Sort by peak score descending
    scores.sort(key=lambda x: x[1], reverse=True)
    return scores

def get_db_stats(db_path="fingerprints.db"):
    """
    Get statistics on the database.
    """
    conn = get_connection(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT COUNT(*) FROM songs")
        song_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM fingerprints")
        fingerprint_count = cursor.fetchone()[0]
    except sqlite3.OperationalError:
        song_count = 0
        fingerprint_count = 0
        
    conn.close()
    return song_count, fingerprint_count
