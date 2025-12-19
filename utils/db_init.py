from utils.db import get_connection

def init_comments_table():
    conn = None
    cur = None

    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
        CREATE TABLE IF NOT EXISTS comments (
            id CHAR(36) NOT NULL,
            user_id CHAR(36) NOT NULL,
            user_name VARCHAR(120) NOT NULL,
            avatar VARCHAR(512) DEFAULT NULL,
            text VARCHAR(2000) NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

            PRIMARY KEY (id),
            INDEX idx_comments_created_at (created_at),
            INDEX idx_comments_user_id (user_id),

            CONSTRAINT fk_comments_user
              FOREIGN KEY (user_id)
              REFERENCES users(id)
              ON DELETE CASCADE
        ) ENGINE=InnoDB
          DEFAULT CHARSET=utf8mb4
          COLLATE=utf8mb4_0900_ai_ci;
        """)

        conn.commit()
        print("✅ Tabla comments verificada / creada correctamente")

    except Exception as e:
        print("❌ ERROR creando tabla comments:", e)
        if conn:
            conn.rollback()

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()