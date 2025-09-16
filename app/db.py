from __future__ import annotations
from typing import Any
from pathlib import Path
import chromadb
from chromadb.config import Settings

def get_client(db_path: Path) -> chromadb.ClientAPI:
    db_path.mkdir(parents=True, exist_ok=True)
    return chromadb.PersistentClient(path=str(db_path), settings=Settings(anonymized_telemetry=False))

def get_collection(client: chromadb.ClientAPI, name: str):
    return client.get_or_create_collection(name)