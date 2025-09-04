from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from typing import AsyncGenerator
import logging
from app.core.config import get_settings
from app.db.models import Base

logger = logging.getLogger(__name__)
settings = get_settings()

# Create async engine with connection pooling and optimizations
engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    future=True,
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True,
    pool_recycle=300,
)

# Configure session factory
SessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to get database session"""
    async with SessionLocal() as session:
        try:
            yield session
        except Exception as e:
            logger.error(f"Database session error: {e}")
            await session.rollback()
            raise
        finally:
            await session.close()

async def init_db():
    """Initialize database tables"""
    try:
        async with engine.begin() as conn:
            logger.info("Creating database tables...")
            await conn.run_sync(Base.metadata.create_all)
            logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise

async def close_db():
    """Close database engine"""
    try:
        await engine.dispose()
        logger.info("Database engine closed")
    except Exception as e:
        logger.error(f"Error closing database: {e}")

class DatabaseService:
    """Service for database operations with dependency injection"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def commit(self):
        """Commit current transaction"""
        await self.session.commit()
    
    async def rollback(self):
        """Rollback current transaction"""
        await self.session.rollback()
    
    async def refresh(self, instance):
        """Refresh instance from database"""
        await self.session.refresh(instance)
