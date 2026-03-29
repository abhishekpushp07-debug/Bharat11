"""
Base Repository Pattern Implementation
Provides common CRUD operations with MongoDB best practices.
"""
from typing import TypeVar, Generic, Optional, List, Dict, Any, Type
from datetime import datetime, timezone
from abc import ABC, abstractmethod

from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorCollection
from pydantic import BaseModel
from bson import ObjectId

T = TypeVar('T', bound=BaseModel)


class BaseRepository(Generic[T], ABC):
    """
    Abstract base repository implementing common CRUD operations.
    Uses MongoDB best practices: projections, indexes, atomic operations.
    """
    
    def __init__(self, db: AsyncIOMotorDatabase, collection_name: str, model_class: Type[T]):
        self._db = db
        self._collection: AsyncIOMotorCollection = db[collection_name]
        self._model_class = model_class
    
    @property
    def collection(self) -> AsyncIOMotorCollection:
        """Get the MongoDB collection."""
        return self._collection
    
    def _to_document(self, model: T, exclude_none: bool = True) -> Dict[str, Any]:
        """
        Convert Pydantic model to MongoDB document.
        Handles datetime serialization.
        """
        doc = model.model_dump(exclude_none=exclude_none)
        
        # Convert datetime to ISO string for consistent storage
        for key, value in doc.items():
            if isinstance(value, datetime):
                doc[key] = value.isoformat()
        
        return doc
    
    def _from_document(self, doc: Dict[str, Any]) -> Optional[T]:
        """
        Convert MongoDB document to Pydantic model.
        Handles _id exclusion and datetime parsing.
        """
        if doc is None:
            return None
        
        # Remove MongoDB _id if present (we use our own id field)
        doc.pop('_id', None)
        
        # Parse ISO strings back to datetime
        for key, value in doc.items():
            if isinstance(value, str):
                try:
                    # Try to parse as datetime
                    if 'T' in value and ('+' in value or 'Z' in value or value.count(':') >= 2):
                        doc[key] = datetime.fromisoformat(value.replace('Z', '+00:00'))
                except (ValueError, TypeError):
                    pass
        
        return self._model_class(**doc)
    
    async def create(self, model: T) -> T:
        """
        Create a new document.
        Returns the created model.
        """
        doc = self._to_document(model)
        await self._collection.insert_one(doc)
        return model
    
    async def create_many(self, models: List[T]) -> List[T]:
        """
        Create multiple documents in a single operation.
        Uses bulk insert for efficiency.
        """
        if not models:
            return []
        
        docs = [self._to_document(m) for m in models]
        await self._collection.insert_many(docs)
        return models
    
    async def find_by_id(
        self, 
        id: str, 
        projection: Optional[Dict[str, int]] = None
    ) -> Optional[T]:
        """
        Find document by id field.
        Uses projection to limit returned fields.
        """
        query = {"id": id}
        proj = projection or {}
        proj["_id"] = 0  # Always exclude MongoDB _id
        
        doc = await self._collection.find_one(query, proj)
        return self._from_document(doc)
    
    async def find_one(
        self, 
        query: Dict[str, Any], 
        projection: Optional[Dict[str, int]] = None
    ) -> Optional[T]:
        """
        Find single document matching query.
        """
        proj = projection or {}
        proj["_id"] = 0
        
        doc = await self._collection.find_one(query, proj)
        return self._from_document(doc)
    
    async def find_many(
        self,
        query: Dict[str, Any],
        projection: Optional[Dict[str, int]] = None,
        sort: Optional[List[tuple]] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[T]:
        """
        Find multiple documents with pagination.
        Returns list of models.
        """
        proj = projection or {}
        proj["_id"] = 0
        
        cursor = self._collection.find(query, proj)
        
        if sort:
            cursor = cursor.sort(sort)
        
        cursor = cursor.skip(skip).limit(limit)
        
        docs = await cursor.to_list(length=limit)
        return [self._from_document(doc) for doc in docs if doc]
    
    async def update_by_id(
        self, 
        id: str, 
        update: Dict[str, Any],
        upsert: bool = False
    ) -> bool:
        """
        Update document by id.
        Returns True if document was modified.
        """
        # Add updated_at timestamp
        if "$set" in update:
            update["$set"]["updated_at"] = datetime.now(timezone.utc).isoformat()
        else:
            update["$set"] = {"updated_at": datetime.now(timezone.utc).isoformat()}
        
        result = await self._collection.update_one(
            {"id": id}, 
            update, 
            upsert=upsert
        )
        return result.modified_count > 0 or result.upserted_id is not None
    
    async def update_one(
        self, 
        query: Dict[str, Any], 
        update: Dict[str, Any],
        upsert: bool = False
    ) -> bool:
        """
        Update single document matching query.
        """
        if "$set" in update:
            update["$set"]["updated_at"] = datetime.now(timezone.utc).isoformat()
        
        result = await self._collection.update_one(query, update, upsert=upsert)
        return result.modified_count > 0 or result.upserted_id is not None
    
    async def update_many(
        self, 
        query: Dict[str, Any], 
        update: Dict[str, Any]
    ) -> int:
        """
        Update multiple documents.
        Returns count of modified documents.
        """
        if "$set" in update:
            update["$set"]["updated_at"] = datetime.now(timezone.utc).isoformat()
        
        result = await self._collection.update_many(query, update)
        return result.modified_count
    
    async def delete_by_id(self, id: str) -> bool:
        """
        Delete document by id.
        Returns True if document was deleted.
        """
        result = await self._collection.delete_one({"id": id})
        return result.deleted_count > 0
    
    async def delete_many(self, query: Dict[str, Any]) -> int:
        """
        Delete multiple documents.
        Returns count of deleted documents.
        """
        result = await self._collection.delete_many(query)
        return result.deleted_count
    
    async def count(self, query: Optional[Dict[str, Any]] = None) -> int:
        """
        Count documents matching query.
        """
        return await self._collection.count_documents(query or {})
    
    async def exists(self, query: Dict[str, Any]) -> bool:
        """
        Check if document exists.
        More efficient than find_one for existence checks.
        """
        doc = await self._collection.find_one(query, {"_id": 1})
        return doc is not None
    
    async def aggregate(
        self, 
        pipeline: List[Dict[str, Any]],
        limit: int = 1000
    ) -> List[Dict[str, Any]]:
        """
        Execute aggregation pipeline.
        """
        cursor = self._collection.aggregate(pipeline)
        return await cursor.to_list(length=limit)
    
    async def bulk_write(self, operations: List[Any]) -> Any:
        """
        Execute bulk write operations.
        For maximum efficiency on large updates.
        """
        if not operations:
            return None
        return await self._collection.bulk_write(operations)
    
    async def create_indexes(self, indexes: List[tuple]) -> None:
        """
        Create indexes on the collection.
        Should be called during app startup.
        """
        from pymongo import IndexModel, ASCENDING, DESCENDING
        
        index_models = []
        for idx in indexes:
            if isinstance(idx, tuple) and len(idx) >= 1:
                keys = idx[0] if isinstance(idx[0], list) else [(idx[0], ASCENDING)]
                options = idx[1] if len(idx) > 1 else {}
                index_models.append(IndexModel(keys, **options))
        
        if index_models:
            await self._collection.create_indexes(index_models)
