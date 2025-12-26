#!/usr/bin/env python3
"""
Postgres Database Migration Script

Creates the required tables and indexes for the RAG Chatbot backend.

Tables:
- book_content_chunks: Stores metadata for indexed book content
- query_analytics: Stores query metrics and performance data

Usage:
    python scripts/migrate_db.py [--drop]

Options:
    --drop: Drop existing tables before creating (WARNING: destroys data)
"""

import os
import sys
from pathlib import Path

import psycopg
from dotenv import load_dotenv


# Load environment variables
load_dotenv()


def get_database_url() -> str:
    """Get Postgres connection URL from environment."""
    url = os.getenv("POSTGRES_URL")
    if not url:
        raise ValueError(
            "POSTGRES_URL not found in environment. "
            "Please set it in .env file or environment variables."
        )
    return url


def drop_tables(conn: psycopg.Connection) -> None:
    """Drop existing tables (WARNING: destroys data)."""
    print("⚠️  Dropping existing tables...")

    with conn.cursor() as cur:
        cur.execute("DROP TABLE IF EXISTS query_analytics CASCADE;")
        cur.execute("DROP TABLE IF EXISTS book_content_chunks CASCADE;")

    conn.commit()
    print("✅ Tables dropped successfully")


def create_book_content_chunks_table(conn: psycopg.Connection) -> None:
    """Create book_content_chunks table with indexes."""
    print("Creating book_content_chunks table...")

    create_table_sql = """
    CREATE TABLE IF NOT EXISTS book_content_chunks (
        chunk_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        module_number INT NOT NULL,
        module_name VARCHAR(255) NOT NULL,
        chapter_title VARCHAR(255) NOT NULL,
        section_id VARCHAR(255) NOT NULL,
        paragraph_index INT NOT NULL,
        char_offset_start INT NOT NULL,
        char_offset_end INT NOT NULL,
        text_content TEXT NOT NULL,
        token_count INT NOT NULL,
        created_at TIMESTAMPTZ DEFAULT NOW(),
        updated_at TIMESTAMPTZ DEFAULT NOW(),

        CONSTRAINT unique_chunk UNIQUE(module_number, chapter_title, section_id, paragraph_index),
        CONSTRAINT valid_module_number CHECK (module_number BETWEEN 1 AND 10),
        CONSTRAINT valid_paragraph_index CHECK (paragraph_index >= 0),
        CONSTRAINT valid_token_count CHECK (token_count BETWEEN 50 AND 400),
        CONSTRAINT valid_char_offsets CHECK (char_offset_end > char_offset_start),
        CONSTRAINT non_empty_text CHECK (LENGTH(TRIM(text_content)) > 0),
        CONSTRAINT valid_section_id CHECK (section_id ~ '^[a-z0-9-]+$')
    );
    """

    create_indexes_sql = """
    CREATE INDEX IF NOT EXISTS idx_chunks_module ON book_content_chunks(module_number);
    CREATE INDEX IF NOT EXISTS idx_chunks_section ON book_content_chunks(section_id);
    CREATE INDEX IF NOT EXISTS idx_chunks_created ON book_content_chunks(created_at);
    """

    with conn.cursor() as cur:
        cur.execute(create_table_sql)
        cur.execute(create_indexes_sql)

    conn.commit()
    print("✅ book_content_chunks table created with indexes")


def create_query_analytics_table(conn: psycopg.Connection) -> None:
    """Create query_analytics table with indexes and constraints."""
    print("Creating query_analytics table...")

    create_table_sql = """
    CREATE TABLE IF NOT EXISTS query_analytics (
        query_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        session_id UUID NOT NULL,
        query_text TEXT NOT NULL,
        query_mode VARCHAR(50) NOT NULL,
        selected_text TEXT,
        current_page_url TEXT,
        response_latency_ms INT NOT NULL,
        retrieval_latency_ms INT,
        synthesis_latency_ms INT,
        chunks_retrieved INT,
        chunks_used INT,
        error_code VARCHAR(50),
        created_at TIMESTAMPTZ DEFAULT NOW(),

        CONSTRAINT valid_query_mode CHECK (query_mode IN ('full-book', 'selected-text')),
        CONSTRAINT valid_response_latency CHECK (response_latency_ms >= 0),
        CONSTRAINT valid_chunks_retrieved CHECK (chunks_retrieved >= 0),
        CONSTRAINT valid_chunks_used CHECK (chunks_used >= 0 AND chunks_used <= chunks_retrieved),
        CONSTRAINT non_empty_query CHECK (LENGTH(TRIM(query_text)) > 0)
    );
    """

    create_indexes_sql = """
    CREATE INDEX IF NOT EXISTS idx_analytics_session ON query_analytics(session_id);
    CREATE INDEX IF NOT EXISTS idx_analytics_created ON query_analytics(created_at);
    CREATE INDEX IF NOT EXISTS idx_analytics_mode ON query_analytics(query_mode);
    CREATE INDEX IF NOT EXISTS idx_analytics_error ON query_analytics(error_code) WHERE error_code IS NOT NULL;
    """

    with conn.cursor() as cur:
        cur.execute(create_table_sql)
        cur.execute(create_indexes_sql)

    conn.commit()
    print("✅ query_analytics table created with indexes")


def verify_schema(conn: psycopg.Connection) -> None:
    """Verify that tables were created successfully."""
    print("\nVerifying schema...")

    with conn.cursor() as cur:
        # Check book_content_chunks
        cur.execute("""
            SELECT COUNT(*)
            FROM information_schema.tables
            WHERE table_name = 'book_content_chunks'
        """)
        chunks_exists = cur.fetchone()[0] == 1

        # Check query_analytics
        cur.execute("""
            SELECT COUNT(*)
            FROM information_schema.tables
            WHERE table_name = 'query_analytics'
        """)
        analytics_exists = cur.fetchone()[0] == 1

        # Count indexes
        cur.execute("""
            SELECT COUNT(*)
            FROM pg_indexes
            WHERE tablename IN ('book_content_chunks', 'query_analytics')
        """)
        index_count = cur.fetchone()[0]

    if chunks_exists and analytics_exists:
        print(f"✅ Schema verification passed")
        print(f"   - book_content_chunks: {'exists' if chunks_exists else 'MISSING'}")
        print(f"   - query_analytics: {'exists' if analytics_exists else 'MISSING'}")
        print(f"   - Indexes created: {index_count}")
    else:
        print("❌ Schema verification FAILED")
        sys.exit(1)


def main() -> None:
    """Run database migrations."""
    print("=" * 60)
    print("RAG Chatbot Database Migration")
    print("=" * 60)
    print()

    # Check for --drop flag
    drop_existing = "--drop" in sys.argv
    if drop_existing:
        response = input("⚠️  This will DELETE all existing data. Continue? (yes/no): ")
        if response.lower() != "yes":
            print("Migration cancelled.")
            sys.exit(0)

    # Get database URL
    try:
        db_url = get_database_url()
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        sys.exit(1)

    # Connect to database
    print(f"Connecting to database...")
    try:
        with psycopg.connect(db_url) as conn:
            print("✅ Connected successfully\n")

            # Drop tables if requested
            if drop_existing:
                drop_tables(conn)
                print()

            # Create tables
            create_book_content_chunks_table(conn)
            create_query_analytics_table(conn)

            # Verify schema
            verify_schema(conn)

            print("\n" + "=" * 60)
            print("✅ Migration completed successfully!")
            print("=" * 60)

    except psycopg.OperationalError as e:
        print(f"❌ Database connection failed: {e}")
        print("\nPlease verify:")
        print("  1. POSTGRES_URL is correctly set in .env")
        print("  2. Database server is accessible")
        print("  3. Credentials are correct")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
