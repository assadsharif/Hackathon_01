#!/usr/bin/env python3
"""
Qdrant Vector Database Setup Script

Creates and configures the Qdrant collection for storing book content embeddings.

Collection Configuration:
- Name: physical-ai-book-v1
- Vector size: 1536 (text-embedding-3-small)
- Distance metric: Cosine
- Index: HNSW (Hierarchical Navigable Small World)

Usage:
    python scripts/setup_vector_db.py [--recreate]

Options:
    --recreate: Delete existing collection and create fresh (WARNING: destroys data)
"""

import os
import sys
from typing import Optional

from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, HnswConfigDiff


# Load environment variables
load_dotenv()


def get_qdrant_config() -> tuple[str, str, str]:
    """Get Qdrant configuration from environment."""
    url = os.getenv("QDRANT_URL")
    api_key = os.getenv("QDRANT_API_KEY")
    collection_name = os.getenv("QDRANT_COLLECTION", "physical-ai-book-v1")

    if not url:
        raise ValueError(
            "QDRANT_URL not found in environment. "
            "Please set it in .env file or environment variables."
        )
    if not api_key:
        raise ValueError(
            "QDRANT_API_KEY not found in environment. "
            "Please set it in .env file or environment variables."
        )

    return url, api_key, collection_name


def create_qdrant_client(url: str, api_key: str) -> QdrantClient:
    """Create and verify Qdrant client connection."""
    try:
        client = QdrantClient(url=url, api_key=api_key)
        # Verify connection by fetching cluster info
        client.get_collections()
        return client
    except Exception as e:
        raise ConnectionError(f"Failed to connect to Qdrant: {e}")


def collection_exists(client: QdrantClient, collection_name: str) -> bool:
    """Check if collection already exists."""
    try:
        client.get_collection(collection_name)
        return True
    except Exception:
        return False


def delete_collection(client: QdrantClient, collection_name: str) -> None:
    """Delete existing collection."""
    print(f"⚠️  Deleting existing collection '{collection_name}'...")
    client.delete_collection(collection_name)
    print("✅ Collection deleted successfully")


def create_collection(client: QdrantClient, collection_name: str) -> None:
    """
    Create Qdrant collection with optimized configuration.

    Vector Configuration:
    - Size: 1536 (OpenAI text-embedding-3-small)
    - Distance: Cosine (optimal for semantic similarity)

    HNSW Index Configuration:
    - m: 16 (connections per layer, balance between speed and accuracy)
    - ef_construct: 100 (construction-time accuracy)
    - ef: 128 (search-time accuracy, overridden at query time if needed)
    """
    print(f"Creating collection '{collection_name}'...")

    # Vector configuration
    vector_config = VectorParams(
        size=1536,  # text-embedding-3-small dimensionality
        distance=Distance.COSINE,  # Cosine similarity for semantic search
    )

    # HNSW index configuration (optimized for accuracy and speed)
    hnsw_config = HnswConfigDiff(
        m=16,  # Number of edges per node (default: 16)
        ef_construct=100,  # Construction-time accuracy (higher = slower indexing, better quality)
    )

    # Create collection
    client.create_collection(
        collection_name=collection_name,
        vectors_config=vector_config,
        hnsw_config=hnsw_config,
    )

    print("✅ Collection created successfully")


def verify_collection(client: QdrantClient, collection_name: str) -> None:
    """Verify collection configuration."""
    print("\nVerifying collection configuration...")

    collection_info = client.get_collection(collection_name)

    # Extract configuration details
    vector_config = collection_info.config.params.vectors
    hnsw_config = collection_info.config.hnsw_config

    print(f"✅ Collection verification passed")
    print(f"   - Name: {collection_name}")
    print(f"   - Vector size: {vector_config.size}")
    print(f"   - Distance metric: {vector_config.distance}")
    print(f"   - HNSW m: {hnsw_config.m}")
    print(f"   - HNSW ef_construct: {hnsw_config.ef_construct}")
    print(f"   - Points count: {collection_info.points_count}")
    print(f"   - Status: {collection_info.status}")


def display_collection_info(client: QdrantClient, collection_name: str) -> None:
    """Display helpful information about next steps."""
    print("\n" + "=" * 60)
    print("Next Steps:")
    print("=" * 60)
    print(f"1. Index book content:")
    print(f"   python scripts/index_book_content.py \\")
    print(f"     --book-path ../physical-ai-book/docs \\")
    print(f"     --collection {collection_name} \\")
    print(f"     --chunk-size 250 \\")
    print(f"     --overlap 50")
    print()
    print(f"2. Verify indexed content:")
    print(f"   python -c \"from qdrant_client import QdrantClient; \\")
    print(f"     client = QdrantClient(url='{client._client._host}', api_key='***'); \\")
    print(f"     info = client.get_collection('{collection_name}'); \\")
    print(f"     print(f'Points: {{info.points_count}}')\"")
    print()
    print(f"3. Test retrieval:")
    print(f"   # After indexing, test with a sample query")
    print(f"   # Use the API endpoint: POST /v1/query")


def main() -> None:
    """Run Qdrant collection setup."""
    print("=" * 60)
    print("RAG Chatbot Vector Database Setup")
    print("=" * 60)
    print()

    # Check for --recreate flag
    recreate = "--recreate" in sys.argv

    # Get configuration
    try:
        url, api_key, collection_name = get_qdrant_config()
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        sys.exit(1)

    # Create client
    print(f"Connecting to Qdrant Cloud...")
    try:
        client = create_qdrant_client(url, api_key)
        print("✅ Connected successfully\n")
    except ConnectionError as e:
        print(f"❌ {e}")
        print("\nPlease verify:")
        print("  1. QDRANT_URL is correctly set in .env")
        print("  2. QDRANT_API_KEY is correct")
        print("  3. Qdrant Cloud cluster is running")
        sys.exit(1)

    # Check if collection exists
    exists = collection_exists(client, collection_name)

    if exists and not recreate:
        print(f"⚠️  Collection '{collection_name}' already exists.")
        print(f"   Use --recreate flag to delete and recreate (WARNING: destroys data)")
        verify_collection(client, collection_name)
        sys.exit(0)

    if exists and recreate:
        response = input("⚠️  This will DELETE all indexed book content. Continue? (yes/no): ")
        if response.lower() != "yes":
            print("Setup cancelled.")
            sys.exit(0)
        delete_collection(client, collection_name)
        print()

    # Create collection
    try:
        create_collection(client, collection_name)
        verify_collection(client, collection_name)
        display_collection_info(client, collection_name)

        print("\n" + "=" * 60)
        print("✅ Vector database setup completed successfully!")
        print("=" * 60)

    except Exception as e:
        print(f"❌ Collection creation failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
