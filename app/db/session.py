import contextlib
import logging
from typing import Any, AsyncIterator
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.future import select 
from app.db.models import Plan
from config import settings
from core.auth_utils import AuthException
from .base import Base


class SessionManager:
	def __init__(self, host:str, engine_kwargs:dict[str, Any] = {}):
		self._engine = create_async_engine(host, **engine_kwargs)
		self._sessionmaker = async_sessionmaker(bind=self._engine,autocommit=False)
		self.logger = logging.getLogger(self.__class__.__name__)

	async def close(self):
		if self._engine is None:
			raise Exception("SessionManager isn't initialized -_-")
		await self._engine.dispose()
		self._engine = None
		self._sessionmaker = None
	
	async def init_db(self):
		if self._engine:
			async with self._engine.begin() as conn:
				await conn.run_sync(Base.metadata.create_all)
		
		if not self._sessionmaker:
			self.logger.error("SessionManager is not initialized-_-")
			raise AuthException("SessionManager is not initialized-_-")
		
		async with self._sessionmaker() as session:
			for plan_name, price, interval, description in [
				("basic", 0.0, 30, "Default free plan"),
				("business", 9.99, 30, "Pro plan with more features"),
				("enterprise", 19.99, 30, "Premium plan with all features"),
				]:
				exists = await session.execute(select(Plan).where(Plan.name == plan_name))

				if not exists.scalar():
					plan = Plan(name=plan_name, price=price, interval=interval, description=description)
					session.add(plan)
				await session.commit()

	@contextlib.asynccontextmanager
	async def connect(self) -> AsyncIterator[AsyncConnection]:
		if self._engine is None:
			raise Exception("SessionManager isn't initialized -_-")
		async with self._engine.begin() as connection:
			try:
				yield connection
			except Exception:
				await connection.rollback()
				raise

	@contextlib.asynccontextmanager
	async def session(self) -> AsyncIterator[AsyncSession]:
		if self._sessionmaker is None:
			raise Exception("SessionManager isn't initialized -_-")
		session = self._sessionmaker()

		try:
			yield session
		except Exception:
			await session.rollback()
			raise
		finally:
			await session.close()
	async def get_db(self):
		async with self.session() as session:
			yield session


sessionmanager = SessionManager(settings.database_url, {"echo": settings.echo_sql})



