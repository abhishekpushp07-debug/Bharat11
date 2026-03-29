"""
Database Connection Manager - MongoDB & Redis
Implements connection pooling, health checks, and graceful shutdown.
World-class implementation following best practices.
"""
import asyncio
import logging
from typing import Optional, AsyncGenerator
from contextlib import asynccontextmanager

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
import redis.asyncio as aioredis
from redis.asyncio.connection import ConnectionPool

from config.settings import settings

logger = logging.getLogger(__name__)


class DatabaseManager:
    """
    Singleton Database Manager for MongoDB and Redis connections.
    Handles connection pooling, health checks, and graceful shutdown.
    """
    
    _instance: Optional['DatabaseManager'] = None
    _initialized: bool = False
    
    def __new__(cls) -> 'DatabaseManager':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._mongo_client: Optional[AsyncIOMotorClient] = None
        self._mongo_db: Optional[AsyncIOMotorDatabase] = None
        self._redis_pool: Optional[ConnectionPool] = None
        self._redis_client: Optional[aioredis.Redis] = None
        self._initialized = True
    
    async def connect(self) -> None:
        """Initialize all database connections with connection pooling."""
        await self._connect_mongodb()
        await self._connect_redis()
        logger.info("All database connections established successfully")
    
    async def _connect_mongodb(self) -> None:
        """
        Establish MongoDB connection with optimized settings.
        Uses connection pooling for high performance.
        """
        try:
            self._mongo_client = AsyncIOMotorClient(
                settings.MONGO_URL,
                minPoolSize=settings.MONGO_MIN_POOL_SIZE,
                maxPoolSize=settings.MONGO_MAX_POOL_SIZE,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=10000,
                socketTimeoutMS=20000,
                retryWrites=True,
                retryReads=True,
            )
            
            # Verify connection
            await self._mongo_client.admin.command('ping')
            self._mongo_db = self._mongo_client[settings.DB_NAME]
            
            logger.info(f"MongoDB connected: {settings.DB_NAME}")
            
        except Exception as e:
            logger.error(f"MongoDB connection failed: {e}")
            raise
    
    async def _connect_redis(self) -> None:
        """
        Establish Redis connection with connection pooling.
        Uses async Redis for non-blocking operations.
        """
        try:
            self._redis_pool = ConnectionPool.from_url(
                settings.REDIS_URL,
                max_connections=settings.REDIS_MAX_CONNECTIONS,
                decode_responses=settings.REDIS_DECODE_RESPONSES,
                socket_timeout=5.0,
                socket_connect_timeout=5.0,
                retry_on_timeout=True,
            )
            
            self._redis_client = aioredis.Redis(connection_pool=self._redis_pool)
            
            # Verify connection
            await self._redis_client.ping()
            
            logger.info("Redis connected successfully")
            
        except Exception as e:
            logger.warning(f"Redis connection failed (non-critical): {e}")
            # Redis is optional - app can work without it for basic functionality
            self._redis_client = None
    
    async def disconnect(self) -> None:
        """Gracefully close all database connections."""
        if self._redis_client:
            await self._redis_client.close()
            logger.info("Redis connection closed")
        
        if self._redis_pool:
            await self._redis_pool.disconnect()
        
        if self._mongo_client:
            self._mongo_client.close()
            logger.info("MongoDB connection closed")
    
    @property
    def db(self) -> AsyncIOMotorDatabase:
        """Get MongoDB database instance."""
        if self._mongo_db is None:
            raise RuntimeError("MongoDB not connected. Call connect() first.")
        return self._mongo_db
    
    @property
    def redis(self) -> Optional[aioredis.Redis]:
        """Get Redis client instance. May be None if Redis unavailable."""
        return self._redis_client
    
    async def health_check(self) -> dict:
        """
        Perform health check on all database connections.
        Returns status of each connection.
        """
        health = {
            "mongodb": {"status": "unhealthy", "latency_ms": None},
            "redis": {"status": "unhealthy", "latency_ms": None},
        }
        
        # Check MongoDB
        try:
            import time
            start = time.perf_counter()
            await self._mongo_client.admin.command('ping')
            latency = (time.perf_counter() - start) * 1000
            health["mongodb"] = {"status": "healthy", "latency_ms": round(latency, 2)}
        except Exception as e:
            health["mongodb"]["error"] = str(e)
        
        # Check Redis
        if self._redis_client:
            try:
                start = time.perf_counter()
                await self._redis_client.ping()
                latency = (time.perf_counter() - start) * 1000
                health["redis"] = {"status": "healthy", "latency_ms": round(latency, 2)}
            except Exception as e:
                health["redis"]["error"] = str(e)
        else:
            health["redis"]["status"] = "disabled"
        
        return health


# Singleton instance
db_manager = DatabaseManager()


# Dependency injection helpers
def get_db() -> AsyncIOMotorDatabase:
    """Dependency for getting MongoDB database."""
    return db_manager.db


def get_redis() -> Optional[aioredis.Redis]:
    """Dependency for getting Redis client."""
    return db_manager.redis


@asynccontextmanager
async def get_db_session() -> AsyncGenerator[AsyncIOMotorDatabase, None]:
    """Context manager for database session."""
    yield db_manager.db


@asynccontextmanager
async def get_transaction():
    """
    Context manager for MongoDB transactions.
    Ensures atomic operations across multiple collections.
    
    Usage:
        async with get_transaction() as session:
            await db.users.insert_one({...}, session=session)
            await db.wallet.insert_one({...}, session=session)
    """
    if db_manager._mongo_client is None:
        raise RuntimeError("MongoDB not connected")
    
    async with await db_manager._mongo_client.start_session() as session:
        async with session.start_transaction():
            try:
                yield session
                # Transaction commits automatically on successful exit
            except Exception as e:
                # Transaction aborts automatically on exception
                logger.error(f"Transaction failed: {e}")
                raise
