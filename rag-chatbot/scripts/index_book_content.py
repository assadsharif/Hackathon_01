#!/usr/bin/env python3
"""
Book Content Indexing Script

Parses the Physical AI & Humanoid Robotics Docusaurus book, chunks content,
generates embeddings, and indexes everything in Postgres and Qdrant.

This script performs the following:
1. Scans the book directory for markdown files
2. Extracts frontmatter and content from each file
3. Chunks paragraphs with configurable size and overlap
4. Generates embeddings using OpenAI API
5. Stores metadata in Postgres (book_content_chunks table)
6. Stores vectors in Qdrant (physical-ai-book-v1 collection)

Usage:
    python scripts/index_book_content.py \\
        --book-path ../physical-ai-book/docs \\
        --collection physical-ai-book-v1 \\
        --chunk-size 250 \\
        --overlap 50 \\
        [--dry-run]

Options:
    --book-path: Path to Docusaurus docs directory
    --collection: Qdrant collection name (default: from env)
    --chunk-size: Target tokens per chunk (default: 250)
    --overlap: Token overlap between chunks (default: 50)
    --dry-run: Parse and chunk without writing to databases
    --force: Overwrite existing chunks (delete and recreate)
"""

import argparse
import os
import re
import sys
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from uuid import uuid4

import psycopg
import tiktoken
from dotenv import load_dotenv
from openai import OpenAI
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct


# Load environment variables
load_dotenv()


# ============================================================================
# Configuration
# ============================================================================

def get_config(args: argparse.Namespace) -> Dict:
    """Get configuration from environment and arguments."""
    return {
        "openai_api_key": os.getenv("OPENAI_API_KEY"),
        "qdrant_url": os.getenv("QDRANT_URL"),
        "qdrant_api_key": os.getenv("QDRANT_API_KEY"),
        "qdrant_collection": args.collection or os.getenv("QDRANT_COLLECTION", "physical-ai-book-v1"),
        "postgres_url": os.getenv("POSTGRES_URL"),
        "embedding_model": os.getenv("EMBEDDING_MODEL", "text-embedding-3-small"),
        "book_path": Path(args.book_path),
        "chunk_size": args.chunk_size,
        "overlap": args.overlap,
        "dry_run": args.dry_run,
        "force": args.force,
    }


# ============================================================================
# Markdown Parsing
# ============================================================================

def extract_frontmatter(content: str) -> Tuple[Dict, str]:
    """
    Extract YAML frontmatter from markdown content.

    Args:
        content: Full markdown file content

    Returns:
        Tuple of (frontmatter dict, content without frontmatter)
    """
    frontmatter = {}
    body = content

    # Match YAML frontmatter block
    match = re.match(r'^---\s*\n(.*?)\n---\s*\n(.*)$', content, re.DOTALL)
    if match:
        yaml_content = match.group(1)
        body = match.group(2)

        # Parse simple YAML (id, title, sidebar_position)
        for line in yaml_content.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                frontmatter[key.strip()] = value.strip().strip('"\'')

    return frontmatter, body


def parse_markdown_file(file_path: Path) -> Dict:
    """
    Parse a single markdown file into structured data.

    Args:
        file_path: Path to markdown file

    Returns:
        Dictionary with metadata and content
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    frontmatter, body = extract_frontmatter(content)

    # Extract module and chapter from path
    # Expected structure: docs/module-N/chapter-name.md or docs/Part-N/module-N/chapter.md
    parts = file_path.parts
    module_number = None
    module_name = None

    # Find module directory
    for i, part in enumerate(parts):
        if part.startswith('module-'):
            module_number = int(part.split('-')[1])
            module_name = frontmatter.get('title', part)
            break
        elif 'module' in part.lower():
            # Try to extract number from various formats
            numbers = re.findall(r'\d+', part)
            if numbers:
                module_number = int(numbers[0])

    if module_number is None:
        # Fallback: try to infer from file path
        module_number = 0  # Unknown module

    chapter_title = frontmatter.get('title', file_path.stem)
    section_id = frontmatter.get('id', file_path.stem)

    return {
        "file_path": str(file_path),
        "module_number": module_number,
        "module_name": module_name or f"Module {module_number}",
        "chapter_title": chapter_title,
        "section_id": section_id,
        "content": body,
        "frontmatter": frontmatter,
    }


def extract_paragraphs(content: str) -> List[str]:
    """
    Extract paragraphs from markdown content.

    Args:
        content: Markdown content (without frontmatter)

    Returns:
        List of paragraph strings
    """
    # Remove code blocks
    content = re.sub(r'```.*?```', '', content, flags=re.DOTALL)

    # Remove inline code
    content = re.sub(r'`[^`]+`', '', content)

    # Remove headers (keep content but remove markdown syntax)
    content = re.sub(r'^#+\s+', '', content, flags=re.MULTILINE)

    # Split by double newlines (paragraph boundaries)
    paragraphs = content.split('\n\n')

    # Clean and filter
    cleaned = []
    for para in paragraphs:
        para = para.strip()
        # Remove very short paragraphs (likely formatting artifacts)
        if len(para) > 50:
            cleaned.append(para)

    return cleaned


# ============================================================================
# Chunking
# ============================================================================

def count_tokens(text: str, model: str = "gpt-3.5-turbo") -> int:
    """Count tokens in text using tiktoken."""
    encoder = tiktoken.encoding_for_model(model)
    return len(encoder.encode(text))


def chunk_text(text: str, chunk_size: int = 250, overlap: int = 50) -> List[str]:
    """
    Chunk text into overlapping segments.

    Args:
        text: Text to chunk
        chunk_size: Target tokens per chunk
        overlap: Overlap tokens between chunks

    Returns:
        List of text chunks
    """
    encoder = tiktoken.encoding_for_model("gpt-3.5-turbo")
    tokens = encoder.encode(text)

    chunks = []
    start = 0

    while start < len(tokens):
        end = start + chunk_size
        chunk_tokens = tokens[start:end]
        chunk_text = encoder.decode(chunk_tokens)
        chunks.append(chunk_text)

        # Move start forward by (chunk_size - overlap)
        start += chunk_size - overlap

        # If remaining tokens are less than overlap, we're done
        if len(tokens) - start < overlap:
            break

    return chunks


# ============================================================================
# Embedding Generation
# ============================================================================

def generate_embeddings(texts: List[str], client: OpenAI, model: str) -> List[List[float]]:
    """
    Generate embeddings for a batch of texts.

    Args:
        texts: List of text strings
        client: OpenAI client
        model: Embedding model name

    Returns:
        List of embedding vectors
    """
    print(f"  Generating embeddings for {len(texts)} chunks...")

    try:
        response = client.embeddings.create(
            input=texts,
            model=model
        )
        embeddings = [item.embedding for item in response.data]
        return embeddings
    except Exception as e:
        print(f"  ❌ Embedding generation failed: {e}")
        raise


# ============================================================================
# Database Operations
# ============================================================================

def store_chunks_postgres(chunks: List[Dict], conn: psycopg.Connection, force: bool) -> None:
    """
    Store chunk metadata in Postgres.

    Args:
        chunks: List of chunk dictionaries
        conn: Postgres connection
        force: If True, delete existing chunks before inserting
    """
    print(f"  Storing {len(chunks)} chunks in Postgres...")

    with conn.cursor() as cur:
        if force:
            # Delete existing chunks for this module
            module_numbers = set(chunk['module_number'] for chunk in chunks)
            for module_num in module_numbers:
                cur.execute(
                    "DELETE FROM book_content_chunks WHERE module_number = %s",
                    (module_num,)
                )

        # Insert chunks
        for chunk in chunks:
            cur.execute("""
                INSERT INTO book_content_chunks (
                    chunk_id, module_number, module_name, chapter_title,
                    section_id, paragraph_index, char_offset_start, char_offset_end,
                    text_content, token_count
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (module_number, chapter_title, section_id, paragraph_index)
                DO UPDATE SET
                    text_content = EXCLUDED.text_content,
                    token_count = EXCLUDED.token_count,
                    updated_at = NOW()
            """, (
                chunk['chunk_id'],
                chunk['module_number'],
                chunk['module_name'],
                chunk['chapter_title'],
                chunk['section_id'],
                chunk['paragraph_index'],
                chunk['char_offset_start'],
                chunk['char_offset_end'],
                chunk['text_content'],
                chunk['token_count'],
            ))

    conn.commit()
    print(f"  ✅ Stored {len(chunks)} chunks in Postgres")


def store_vectors_qdrant(chunks: List[Dict], embeddings: List[List[float]],
                        client: QdrantClient, collection: str) -> None:
    """
    Store chunk vectors in Qdrant.

    Args:
        chunks: List of chunk dictionaries
        embeddings: List of embedding vectors
        client: Qdrant client
        collection: Collection name
    """
    print(f"  Storing {len(chunks)} vectors in Qdrant...")

    points = []
    for chunk, embedding in zip(chunks, embeddings):
        point = PointStruct(
            id=str(chunk['chunk_id']),
            vector=embedding,
            payload={
                "chunk_id": str(chunk['chunk_id']),
                "module_number": chunk['module_number'],
                "module_name": chunk['module_name'],
                "chapter_title": chunk['chapter_title'],
                "section_id": chunk['section_id'],
                "paragraph_index": chunk['paragraph_index'],
                "text_content": chunk['text_content'],
                "token_count": chunk['token_count'],
            }
        )
        points.append(point)

    # Batch insert
    client.upsert(collection_name=collection, points=points)
    print(f"  ✅ Stored {len(points)} vectors in Qdrant")


# ============================================================================
# Main Indexing Logic
# ============================================================================

def index_file(file_path: Path, config: Dict, openai_client: OpenAI,
               qdrant_client: QdrantClient, postgres_conn: psycopg.Connection) -> int:
    """
    Index a single markdown file.

    Args:
        file_path: Path to markdown file
        config: Configuration dictionary
        openai_client: OpenAI client
        qdrant_client: Qdrant client
        postgres_conn: Postgres connection

    Returns:
        Number of chunks created
    """
    print(f"\nProcessing: {file_path.name}")

    # Parse file
    doc = parse_markdown_file(file_path)
    paragraphs = extract_paragraphs(doc['content'])
    print(f"  Found {len(paragraphs)} paragraphs")

    if not paragraphs:
        print(f"  ⚠️  No content to index, skipping")
        return 0

    # Chunk paragraphs
    all_chunks = []
    for para_index, paragraph in enumerate(paragraphs):
        chunks = chunk_text(paragraph, config['chunk_size'], config['overlap'])

        for chunk_index, chunk_text in enumerate(chunks):
            chunk_id = uuid4()
            token_count = count_tokens(chunk_text)

            chunk_dict = {
                "chunk_id": chunk_id,
                "module_number": doc['module_number'],
                "module_name": doc['module_name'],
                "chapter_title": doc['chapter_title'],
                "section_id": doc['section_id'],
                "paragraph_index": para_index,
                "char_offset_start": 0,  # Simplified for MVP
                "char_offset_end": len(chunk_text),
                "text_content": chunk_text,
                "token_count": token_count,
            }
            all_chunks.append(chunk_dict)

    print(f"  Created {len(all_chunks)} chunks")

    if config['dry_run']:
        print(f"  [DRY RUN] Would index {len(all_chunks)} chunks")
        return len(all_chunks)

    # Generate embeddings
    chunk_texts = [c['text_content'] for c in all_chunks]
    embeddings = generate_embeddings(chunk_texts, openai_client, config['embedding_model'])

    # Store in databases
    store_chunks_postgres(all_chunks, postgres_conn, config['force'])
    store_vectors_qdrant(all_chunks, embeddings, qdrant_client, config['qdrant_collection'])

    return len(all_chunks)


def main() -> None:
    """Main indexing workflow."""
    parser = argparse.ArgumentParser(description="Index Physical AI book content")
    parser.add_argument("--book-path", required=True, help="Path to Docusaurus docs directory")
    parser.add_argument("--collection", help="Qdrant collection name")
    parser.add_argument("--chunk-size", type=int, default=250, help="Target tokens per chunk")
    parser.add_argument("--overlap", type=int, default=50, help="Token overlap between chunks")
    parser.add_argument("--dry-run", action="store_true", help="Parse only, don't write to databases")
    parser.add_argument("--force", action="store_true", help="Overwrite existing chunks")
    args = parser.parse_args()

    print("=" * 60)
    print("Physical AI Book Indexing Script")
    print("=" * 60)

    # Get configuration
    config = get_config(args)

    # Validate book path
    if not config['book_path'].exists():
        print(f"❌ Book path does not exist: {config['book_path']}")
        sys.exit(1)

    # Initialize clients
    print("\nInitializing clients...")
    openai_client = OpenAI(api_key=config['openai_api_key'])

    if not config['dry_run']:
        qdrant_client = QdrantClient(url=config['qdrant_url'], api_key=config['qdrant_api_key'])
        postgres_conn = psycopg.connect(config['postgres_url'])
        print("✅ Clients initialized")
    else:
        print("✅ [DRY RUN MODE] Skipping database initialization")
        qdrant_client = None
        postgres_conn = None

    # Find all markdown files
    print(f"\nScanning {config['book_path']} for markdown files...")
    md_files = list(config['book_path'].rglob("*.md"))
    # Filter out index files and README
    md_files = [f for f in md_files if f.name not in ['index.md', 'README.md', '_category_.json']]
    print(f"Found {len(md_files)} files to index")

    # Index all files
    total_chunks = 0
    for file_path in md_files:
        try:
            chunks_created = index_file(
                file_path, config, openai_client, qdrant_client, postgres_conn
            )
            total_chunks += chunks_created
        except Exception as e:
            print(f"  ❌ Error indexing {file_path.name}: {e}")
            continue

    # Cleanup
    if postgres_conn:
        postgres_conn.close()

    # Summary
    print("\n" + "=" * 60)
    print(f"✅ Indexing complete!")
    print(f"   Files processed: {len(md_files)}")
    print(f"   Total chunks created: {total_chunks}")
    if config['dry_run']:
        print(f"   [DRY RUN] No data was written to databases")
    print("=" * 60)


if __name__ == "__main__":
    main()
