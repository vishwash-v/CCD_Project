"""
IBM Cloudant / CouchDB / In-Memory database service.
Uses IBM Cloudant SDK in production, CouchDB for Docker dev,
and falls back to in-memory storage when neither is available.
"""

import httpx
import uuid
import json
import logging
from typing import Optional, List, Dict, Any
from app.config import settings

logger = logging.getLogger(__name__)

# Database names
DB_USERS = "campus_users"
DB_RESOURCES = "campus_resources"
DB_BOOKINGS = "campus_bookings"

ALL_DBS = [DB_USERS, DB_RESOURCES, DB_BOOKINGS]


class InMemoryDB:
    """
    Simple in-memory database that mimics CouchDB behavior.
    Used for local development when CouchDB/Docker is not available.
    """

    def __init__(self):
        self._stores: Dict[str, Dict[str, dict]] = {}

    def ensure_db(self, db_name: str):
        if db_name not in self._stores:
            self._stores[db_name] = {}

    def create(self, db_name: str, doc: dict) -> dict:
        self.ensure_db(db_name)
        if "_id" not in doc:
            doc["_id"] = str(uuid.uuid4())
        doc["_rev"] = f"1-{uuid.uuid4().hex[:8]}"
        self._stores[db_name][doc["_id"]] = json.loads(json.dumps(doc))
        return doc

    def get(self, db_name: str, doc_id: str) -> Optional[dict]:
        self.ensure_db(db_name)
        doc = self._stores[db_name].get(doc_id)
        return json.loads(json.dumps(doc)) if doc else None

    def update(self, db_name: str, doc_id: str, updates: dict) -> dict:
        self.ensure_db(db_name)
        doc = self._stores[db_name].get(doc_id)
        if not doc:
            raise ValueError(f"Document {doc_id} not found")
        doc.update(updates)
        doc["_rev"] = f"2-{uuid.uuid4().hex[:8]}"
        self._stores[db_name][doc_id] = doc
        return json.loads(json.dumps(doc))

    def delete(self, db_name: str, doc_id: str) -> bool:
        self.ensure_db(db_name)
        if doc_id in self._stores[db_name]:
            del self._stores[db_name][doc_id]
            return True
        return False

    def get_all(self, db_name: str, doc_type: str = None) -> List[dict]:
        self.ensure_db(db_name)
        docs = list(self._stores[db_name].values())
        if doc_type:
            docs = [d for d in docs if d.get("type") == doc_type]
        return json.loads(json.dumps(docs))

    def find(self, db_name: str, selector: dict) -> List[dict]:
        self.ensure_db(db_name)
        results = []
        for doc in self._stores[db_name].values():
            if self._matches(doc, selector):
                results.append(json.loads(json.dumps(doc)))
        return results

    def _matches(self, doc: dict, selector: dict) -> bool:
        """Simple Mango query selector matching."""
        for key, value in selector.items():
            if key.startswith("$"):
                continue
            doc_val = doc.get(key)
            if isinstance(value, dict):
                for op, op_val in value.items():
                    if op == "$in" and doc_val not in op_val:
                        return False
                    elif op == "$gte" and (doc_val is None or doc_val < op_val):
                        return False
                    elif op == "$lte" and (doc_val is None or doc_val > op_val):
                        return False
                    elif op == "$gt" and (doc_val is None or doc_val <= op_val):
                        return False
                    elif op == "$lt" and (doc_val is None or doc_val >= op_val):
                        return False
            elif doc_val != value:
                return False
        return True


class CloudantService:
    """
    Database service that works with:
    1. IBM Cloudant (production)
    2. CouchDB (Docker local dev)
    3. In-memory (no Docker fallback)
    """

    def __init__(self):
        self.client: Optional[httpx.AsyncClient] = None
        self.base_url: str = ""
        self._initialized = False
        self._in_memory: Optional[InMemoryDB] = None
        self._use_memory = False

    async def initialize(self):
        """Initialize database connection and ensure databases exist."""
        if self._initialized:
            return

        if settings.use_cloudant:
            # Production: IBM Cloudant
            logger.info("Connecting to IBM Cloudant...")
            self.base_url = settings.CLOUDANT_URL
            self.client = httpx.AsyncClient(
                base_url=self.base_url,
                headers={"Content-Type": "application/json"},
                timeout=30.0,
            )
            token_response = await httpx.AsyncClient().post(
                "https://iam.cloud.ibm.com/identity/token",
                data={
                    "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
                    "apikey": settings.CLOUDANT_APIKEY,
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            token = token_response.json()["access_token"]
            self.client.headers["Authorization"] = f"Bearer {token}"
        else:
            # Try CouchDB first, fallback to in-memory
            try:
                logger.info("Trying to connect to local CouchDB...")
                test_client = httpx.AsyncClient(
                    base_url=settings.COUCHDB_URL,
                    auth=(settings.COUCHDB_USER, settings.COUCHDB_PASSWORD),
                    timeout=3.0,
                )
                response = await test_client.get("/")
                response.raise_for_status()
                self.client = test_client
                self.client.headers["Content-Type"] = "application/json"
                self.base_url = settings.COUCHDB_URL
                logger.info("Connected to CouchDB successfully.")
            except Exception as e:
                logger.warning(f"CouchDB not available ({e}). Using in-memory database.")
                self._use_memory = True
                self._in_memory = InMemoryDB()

        if not self._use_memory:
            # Ensure all databases exist (CouchDB/Cloudant)
            for db_name in ALL_DBS:
                await self._ensure_database(db_name)
            await self._create_views()
        else:
            for db_name in ALL_DBS:
                self._in_memory.ensure_db(db_name)

        self._initialized = True
        mode = "In-Memory" if self._use_memory else ("Cloudant" if settings.use_cloudant else "CouchDB")
        logger.info(f"Database service initialized successfully (mode: {mode}).")

    async def _ensure_database(self, db_name: str):
        """Create database if it doesn't exist."""
        try:
            response = await self.client.put(f"/{db_name}")
            if response.status_code in (201, 202):
                logger.info(f"Created database: {db_name}")
            elif response.status_code == 412:
                logger.info(f"Database already exists: {db_name}")
        except Exception as e:
            logger.error(f"Error creating database {db_name}: {e}")

    async def _create_views(self):
        """Create CouchDB/Cloudant design documents for querying."""
        booking_views = {
            "_id": "_design/bookings",
            "views": {
                "by_resource": {"map": "function(doc) { if (doc.type === 'booking') { emit(doc.resource_id, doc); } }"},
                "by_user": {"map": "function(doc) { if (doc.type === 'booking') { emit(doc.user_id, doc); } }"},
                "by_resource_date": {"map": "function(doc) { if (doc.type === 'booking') { emit([doc.resource_id, doc.date], doc); } }"},
                "by_status": {"map": "function(doc) { if (doc.type === 'booking') { emit(doc.status, doc); } }"},
                "by_date": {"map": "function(doc) { if (doc.type === 'booking') { emit(doc.date, doc); } }"},
            },
        }
        resource_views = {
            "_id": "_design/resources",
            "views": {
                "by_category": {"map": "function(doc) { if (doc.type === 'resource') { emit(doc.category, doc); } }"},
                "all": {"map": "function(doc) { if (doc.type === 'resource') { emit(doc._id, doc); } }"},
            },
        }
        user_views = {
            "_id": "_design/users",
            "views": {
                "by_email": {"map": "function(doc) { if (doc.type === 'user') { emit(doc.email, doc); } }"},
                "by_role": {"map": "function(doc) { if (doc.type === 'user') { emit(doc.role, doc); } }"},
            },
        }
        await self._upsert_design_doc(DB_BOOKINGS, booking_views)
        await self._upsert_design_doc(DB_RESOURCES, resource_views)
        await self._upsert_design_doc(DB_USERS, user_views)

    async def _upsert_design_doc(self, db_name: str, design_doc: dict):
        """Create or update a design document."""
        doc_id = design_doc["_id"]
        try:
            response = await self.client.get(f"/{db_name}/{doc_id}")
            if response.status_code == 200:
                existing = response.json()
                design_doc["_rev"] = existing["_rev"]
            await self.client.put(f"/{db_name}/{doc_id}", json=design_doc)
        except Exception as e:
            logger.error(f"Error upserting design doc {doc_id}: {e}")

    # ── CRUD Operations ──────────────────────────────────────────

    async def create_document(self, db_name: str, document: dict) -> dict:
        """Create a new document in the specified database."""
        if "_id" not in document:
            document["_id"] = str(uuid.uuid4())

        if self._use_memory:
            return self._in_memory.create(db_name, document)

        response = await self.client.post(f"/{db_name}", json=document)
        response.raise_for_status()
        result = response.json()
        document["_id"] = result["id"]
        document["_rev"] = result["rev"]
        return document

    async def get_document(self, db_name: str, doc_id: str) -> Optional[dict]:
        """Get a document by ID."""
        if self._use_memory:
            return self._in_memory.get(db_name, doc_id)

        response = await self.client.get(f"/{db_name}/{doc_id}")
        if response.status_code == 404:
            return None
        response.raise_for_status()
        return response.json()

    async def update_document(self, db_name: str, doc_id: str, updates: dict) -> dict:
        """Update an existing document."""
        if self._use_memory:
            return self._in_memory.update(db_name, doc_id, updates)

        current = await self.get_document(db_name, doc_id)
        if not current:
            raise ValueError(f"Document {doc_id} not found")
        current.update(updates)
        response = await self.client.put(f"/{db_name}/{doc_id}", json=current)
        response.raise_for_status()
        result = response.json()
        current["_rev"] = result["rev"]
        return current

    async def delete_document(self, db_name: str, doc_id: str) -> bool:
        """Delete a document by ID."""
        if self._use_memory:
            return self._in_memory.delete(db_name, doc_id)

        current = await self.get_document(db_name, doc_id)
        if not current:
            return False
        response = await self.client.delete(
            f"/{db_name}/{doc_id}", params={"rev": current["_rev"]}
        )
        return response.status_code == 200

    async def query_view(self, db_name: str, design_doc: str, view_name: str,
                         key: Any = None, start_key: Any = None, end_key: Any = None,
                         limit: int = 100, descending: bool = False) -> List[dict]:
        """Query a CouchDB/Cloudant view."""
        if self._use_memory:
            return self._in_memory.get_all(db_name)

        params: Dict[str, Any] = {"limit": limit, "descending": descending}
        if key is not None:
            params["key"] = json.dumps(key)
        if start_key is not None:
            params["startkey"] = json.dumps(start_key)
        if end_key is not None:
            params["endkey"] = json.dumps(end_key)

        response = await self.client.get(
            f"/{db_name}/_design/{design_doc}/_view/{view_name}", params=params
        )
        response.raise_for_status()
        result = response.json()
        return [row["value"] for row in result.get("rows", [])]

    async def get_all_documents(self, db_name: str, doc_type: str = None) -> List[dict]:
        """Get all documents from a database, optionally filtered by type."""
        if self._use_memory:
            return self._in_memory.get_all(db_name, doc_type)

        response = await self.client.get(
            f"/{db_name}/_all_docs", params={"include_docs": True}
        )
        response.raise_for_status()
        result = response.json()
        docs = [
            row["doc"] for row in result.get("rows", [])
            if not row["id"].startswith("_design")
        ]
        if doc_type:
            docs = [d for d in docs if d.get("type") == doc_type]
        return docs

    async def find_documents(self, db_name: str, selector: dict) -> List[dict]:
        """Query using Cloudant/CouchDB _find (Mango query) or in-memory filter."""
        if self._use_memory:
            return self._in_memory.find(db_name, selector)

        response = await self.client.post(
            f"/{db_name}/_find", json={"selector": selector, "limit": 200}
        )
        response.raise_for_status()
        return response.json().get("docs", [])

    async def close(self):
        """Close the HTTP client."""
        if self.client:
            await self.client.aclose()


# Singleton instance
db = CloudantService()
