CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS core;

CREATE TABLE staging.videos (
    video_id VARCHAR(20) PRIMARY KEY,
    title TEXT,
    published_at VARCHAR(50),
    duration VARCHAR(30),
    views VARCHAR(20),
    likes VARCHAR(20),
    comments VARCHAR(20),
    loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE core.videos (
    video_id VARCHAR(20) PRIMARY KEY,
    title TEXT,
    published_at TIMESTAMP,
    duration_seconds INTEGER,
    views INTEGER,
    likes INTEGER,
    comments INTEGER,
    likes_per_view FLOAT,
    comments_per_view FLOAT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);