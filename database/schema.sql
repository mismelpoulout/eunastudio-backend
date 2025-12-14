-- =========================
-- USERS
-- =========================
CREATE TABLE users (
    id CHAR(36) PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    avatar_url VARCHAR(255),
    role ENUM('user', 'admin') DEFAULT 'user',

    is_verified BOOLEAN DEFAULT FALSE,
    verification_code VARCHAR(10),

    plan ENUM('free', 'premium') DEFAULT 'free',
    plan_start DATETIME,
    plan_end DATETIME,

    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- =========================
-- SESSIONS
-- =========================
CREATE TABLE sessions (
    id CHAR(36) PRIMARY KEY,
    user_id CHAR(36),
    jwt_token TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- =========================
-- EXAM RESULTS
-- =========================
CREATE TABLE exam_results (
    id CHAR(36) PRIMARY KEY,
    user_id CHAR(36),
    exam_type ENUM(
    'corto',
    'trivia',
    'simulacion',
    'especialidad'
)
    specialty VARCHAR(100),

    score INT,
    total_questions INT,
    duration_seconds INT,

    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);