from utils.db import get_connection

def init_comments_table():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS comments (
            id CHAR(36) PRIMARY KEY,
            user_id CHAR(36) NOT NULL,
            user_name VARCHAR(120) NOT NULL,
            avatar VARCHAR(512),
            text TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_comments_user (user_id),
            CONSTRAINT fk_comments_user
                FOREIGN KEY (user_id)
                REFERENCES users(id)
                ON DELETE CASCADE
        )
    """)

    conn.commit()
    cur.close()
    conn.close()