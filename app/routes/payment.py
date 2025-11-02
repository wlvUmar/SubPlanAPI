import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.session import sessionmanager
from app.db.models import Payment, Subscription, PaymentStatus as PaymentStatusEnum, Currencies
from app.schemas.subscription import PaymentCreate, PaymentUpdate, PaymentResponse, PaymentStatus
from core.auth_utils import auth_manager

payment = APIRouter(tags=["Payments"])
logger = logging.getLogger("payment_router")


@payment.get("/me", response_model=List[PaymentResponse])
async def get_my_payments(
	payload = Depends(auth_manager.decode),
	db: AsyncSession = Depends(sessionmanager.get_db)
):
	try:
		user_id = payload.get("sub")
		query = select(Payment).where(Payment.user_id == user_id)
		result = await db.execute(query)
		payments = result.scalars().all()
		return payments
	except Exception as e:
		logger.error(f"Error fetching payments: {e}", exc_info=True)
		raise HTTPException(status_code=500, detail="Failed to fetch payments")


@payment.post("/", response_model=PaymentResponse, status_code=201)
async def create_payment(
	payment_data: PaymentCreate,
	payload = Depends(auth_manager.decode),
	db: AsyncSession = Depends(sessionmanager.get_db)
):
	try:
		user_id = payload.get("sub")
		
		sub_query = select(Subscription).where(
			Subscription.subscription_id == payment_data.subscription_id,
			Subscription.user_id == user_id
		)
		sub_result = await db.execute(sub_query)
		subscription = sub_result.scalar_one_or_none()
		
		if not subscription:
			raise HTTPException(status_code=404, detail="Subscription not found")
		
		new_payment = Payment(
			user_id=user_id,
			subscription_id=payment_data.subscription_id,
			amount=payment_data.amount,
			currency=payment_data.currency,
			status=PaymentStatusEnum.pending
		)
		db.add(new_payment)
		await db.commit()
		await db.refresh(new_payment)
		return new_payment
	except HTTPException:
		raise
	except Exception as e:
		await db.rollback()
		logger.error(f"Error creating payment: {e}", exc_info=True)
		raise HTTPException(status_code=500, detail="Failed to create payment")


@payment.patch("/{payment_id}", response_model=PaymentResponse)
async def update_payment(
	payment_id: str,
	payment_update: PaymentUpdate,
	payload = Depends(auth_manager.decode),
	db: AsyncSession = Depends(sessionmanager.get_db)
):
	try:
		user_id = payload.get("sub")
		query = select(Payment).where(
			Payment.payment_id == payment_id,
			Payment.user_id == user_id
		)
		result = await db.execute(query)
		payment = result.scalar_one_or_none()
		
		if not payment:
			raise HTTPException(status_code=404, detail="Payment not found")
		
		payment.status = payment_update.status
		if payment_update.provider_txn_id:
			payment.provider_txn_id = payment_update.provider_txn_id
		
		await db.commit()
		await db.refresh(payment)
		return payment
	except HTTPException:
		raise
	except Exception as e:
		await db.rollback()
		logger.error(f"Error updating payment: {e}", exc_info=True)
		raise HTTPException(status_code=500, detail="Failed to update payment")


@payment.get("/{payment_id}", response_model=PaymentResponse)
async def get_payment(
	payment_id: str,
	payload = Depends(auth_manager.decode),
	db: AsyncSession = Depends(sessionmanager.get_db)
):
	try:
		user_id = payload.get("sub")
		query = select(Payment).where(
			Payment.payment_id == payment_id,
			Payment.user_id == user_id
		)
		result = await db.execute(query)
		payment = result.scalar_one_or_none()
		
		if not payment:
			raise HTTPException(status_code=404, detail="Payment not found")
		
		return payment
	except HTTPException:
		raise
	except Exception as e:
		logger.error(f"Error fetching payment: {e}", exc_info=True)
		raise HTTPException(status_code=500, detail="Failed to fetch payment")


@payment.get("/", response_model=List[PaymentResponse])
async def get_all_payments(
	payload = Depends(auth_manager.require_role("admin")),
	db: AsyncSession = Depends(sessionmanager.get_db)
):
	try:
		query = select(Payment)
		result = await db.execute(query)
		payments = result.scalars().all()
		return payments
	except Exception as e:
		logger.error(f"Error fetching payments: {e}", exc_info=True)
		raise HTTPException(status_code=500, detail="Failed to fetch payments")

