import logging
from datetime import date
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.db.session import sessionmanager
from app.db.models import Subscription, Plan, PlansEnum, SubscriptionStatus as SubscriptionStatusEnum
from app.schemas.subscription import SubscriptionCreate, SubscriptionResponse, SubscriptionStatus
from core.auth_utils import auth_manager, AuthException

subscription = APIRouter(tags=["Subscriptions"])
logger = logging.getLogger("subscription_router")


@subscription.get("/me", response_model=List[SubscriptionResponse])
async def get_my_subscriptions(
	payload = Depends(auth_manager.decode),
	db: AsyncSession = Depends(sessionmanager.get_db)
):
	try:
		user_id = payload.get("sub")
		query = select(Subscription).options(selectinload(Subscription.plan)).where(Subscription.user_id == user_id)
		result = await db.execute(query)
		subscriptions = result.scalars().all()
		return subscriptions
	except Exception as e:
		logger.error(f"Error fetching subscriptions: {e}", exc_info=True)
		raise HTTPException(status_code=500, detail="Failed to fetch subscriptions")


@subscription.post("/", response_model=SubscriptionResponse, status_code=201)
async def create_subscription(
	sub_data: SubscriptionCreate,
	payload = Depends(auth_manager.decode),
	db: AsyncSession = Depends(sessionmanager.get_db)
):
	try:
		user_id = payload.get("sub")
		
		plan_query = select(Plan).where(Plan.name == sub_data.name)
		plan_result = await db.execute(plan_query)
		plan = plan_result.scalar_one_or_none()
		
		if not plan:
			raise HTTPException(status_code=404, detail=f"Plan {sub_data.name} not found")
		
		new_subscription = Subscription(
			user_id=user_id,
			name=sub_data.name,
			status=SubscriptionStatusEnum.active
		)
		db.add(new_subscription)
		await db.commit()
		await db.refresh(new_subscription)
		return new_subscription
	except HTTPException:
		raise
	except Exception as e:
		await db.rollback()
		logger.error(f"Error creating subscription: {e}", exc_info=True)
		raise HTTPException(status_code=500, detail="Failed to create subscription")


@subscription.patch("/{subscription_id}/cancel", response_model=SubscriptionResponse)
async def cancel_subscription(
	subscription_id: str,
	payload = Depends(auth_manager.decode),
	db: AsyncSession = Depends(sessionmanager.get_db)
):
	try:
		user_id = payload.get("sub")
		query = select(Subscription).where(
			Subscription.subscription_id == subscription_id,
			Subscription.user_id == user_id
		)
		result = await db.execute(query)
		subscription = result.scalar_one_or_none()
		
		if not subscription:
			raise HTTPException(status_code=404, detail="Subscription not found")
		
		subscription.status = SubscriptionStatusEnum.canceled
		await db.commit()
		await db.refresh(subscription)
		return subscription
	except HTTPException:
		raise
	except Exception as e:
		await db.rollback()
		logger.error(f"Error canceling subscription: {e}", exc_info=True)
		raise HTTPException(status_code=500, detail="Failed to cancel subscription")


@subscription.get("/{subscription_id}", response_model=SubscriptionResponse)
async def get_subscription(
	subscription_id: str,
	payload = Depends(auth_manager.decode),
	db: AsyncSession = Depends(sessionmanager.get_db)
):
	try:
		user_id = payload.get("sub")
		query = select(Subscription).where(
			Subscription.subscription_id == subscription_id,
			Subscription.user_id == user_id
		)
		result = await db.execute(query)
		subscription = result.scalar_one_or_none()
		
		if not subscription:
			raise HTTPException(status_code=404, detail="Subscription not found")
		
		return subscription
	except HTTPException:
		raise
	except Exception as e:
		logger.error(f"Error fetching subscription: {e}", exc_info=True)
		raise HTTPException(status_code=500, detail="Failed to fetch subscription")


@subscription.get("/", response_model=List[SubscriptionResponse])
async def get_all_subscriptions(
	payload = Depends(auth_manager.require_role("admin")),
	db: AsyncSession = Depends(sessionmanager.get_db)
):
	try:
		query = select(Subscription)
		result = await db.execute(query)
		subscriptions = result.scalars().all()
		return subscriptions
	except Exception as e:
		logger.error(f"Error fetching subscriptions: {e}", exc_info=True)
		raise HTTPException(status_code=500, detail="Failed to fetch subscriptions")

