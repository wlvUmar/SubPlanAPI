import logging
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy import func, or_

from app.db.session import sessionmanager
from app.db.models import User, Subscription, Payment, Invoice, Plan, SubscriptionStatus
from app.schemas.users import UserSchema, UserRole
from app.schemas.subscription import SubscriptionResponse, PaymentResponse, InvoiceResponse
from core.auth_utils import auth_manager

admin = APIRouter(tags=["Admin"])
logger = logging.getLogger("admin_router")


@admin.get("/users", response_model=List[UserSchema])
async def get_all_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = None,
    role: Optional[UserRole] = None,
    payload=Depends(auth_manager.require_role("admin")),
    db: AsyncSession = Depends(sessionmanager.get_db)
):
    try:
        query = select(User)
        
        if search:
            query = query.where(
                or_(
                    User.email.ilike(f"%{search}%"),
                    User.name.ilike(f"%{search}%")
                )
            )
        
        if role:
            query = query.where(User.role == role)
        
        query = query.offset(skip).limit(limit).order_by(User.created_at.desc())
        result = await db.execute(query)
        users = result.scalars().all()
        return users
    except Exception as e:
        logger.error(f"Error fetching users: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to fetch users")


@admin.get("/users/{user_id}", response_model=UserSchema)
async def get_user(
    user_id: str,
    payload=Depends(auth_manager.require_role("admin")),
    db: AsyncSession = Depends(sessionmanager.get_db)
):
    try:
        query = select(User).where(User.user_id == user_id)
        result = await db.execute(query)
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching user: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to fetch user")


@admin.patch("/users/{user_id}/activate")
async def toggle_user_status(
    user_id: str,
    is_active: bool = Query(...),
    payload=Depends(auth_manager.require_role("admin")),
    db: AsyncSession = Depends(sessionmanager.get_db)
):
    try:
        query = select(User).where(User.user_id == user_id)
        result = await db.execute(query)
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        user.is_active = is_active
        await db.commit()
        await db.refresh(user)
        return {"message": f"User {'activated' if is_active else 'deactivated'}", "user": UserSchema.model_validate(user)}
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating user status: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to update user status")


@admin.patch("/users/{user_id}/verify")
async def verify_user_admin(
    user_id: str,
    payload=Depends(auth_manager.require_role("admin")),
    db: AsyncSession = Depends(sessionmanager.get_db)
):
    try:
        query = select(User).where(User.user_id == user_id)
        result = await db.execute(query)
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        user.is_verified = True
        await db.commit()
        await db.refresh(user)
        return {"message": "User verified", "user": UserSchema.model_validate(user)}
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error verifying user: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to verify user")


@admin.patch("/users/{user_id}/role")
async def update_user_role(
    user_id: str,
    role: UserRole = Query(...),
    payload=Depends(auth_manager.require_role("admin")),
    db: AsyncSession = Depends(sessionmanager.get_db)
):
    try:
        query = select(User).where(User.user_id == user_id)
        result = await db.execute(query)
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        user.role = role
        await db.commit()
        await db.refresh(user)
        return {"message": f"User role updated to {role.value}", "user": UserSchema.model_validate(user)}
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating user role: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to update user role")


@admin.get("/subscriptions", response_model=List[SubscriptionResponse])
async def get_all_subscriptions_admin(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[SubscriptionStatus] = None,
    payload=Depends(auth_manager.require_role("admin")),
    db: AsyncSession = Depends(sessionmanager.get_db)
):
    try:
        query = select(Subscription).options(selectinload(Subscription.plan))
        
        if status:
            query = query.where(Subscription.status == status)
        
        query = query.offset(skip).limit(limit).order_by(Subscription.start_date.desc())
        result = await db.execute(query)
        subscriptions = result.scalars().all()
        
        return subscriptions
    except Exception as e:
        logger.error(f"Error fetching subscriptions: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to fetch subscriptions")


@admin.patch("/subscriptions/{subscription_id}/status")
async def update_subscription_status(
    subscription_id: str,
    status: SubscriptionStatus = Query(...),
    payload=Depends(auth_manager.require_role("admin")),
    db: AsyncSession = Depends(sessionmanager.get_db)
):
    try:
        query = select(Subscription).where(Subscription.subscription_id == subscription_id)
        result = await db.execute(query)
        subscription = result.scalar_one_or_none()
        
        if not subscription:
            raise HTTPException(status_code=404, detail="Subscription not found")
        
        subscription.status = status
        await db.commit()
        await db.refresh(subscription)
        return subscription
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating subscription status: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to update subscription status")


@admin.get("/payments", response_model=List[PaymentResponse])
async def get_all_payments_admin(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = None,
    payload=Depends(auth_manager.require_role("admin")),
    db: AsyncSession = Depends(sessionmanager.get_db)
):
    try:
        query = select(Payment)
        
        if status:
            query = query.where(Payment.status == status)
        
        query = query.offset(skip).limit(limit).order_by(Payment.created_at.desc())
        result = await db.execute(query)
        payments = result.scalars().all()
        return payments
    except Exception as e:
        logger.error(f"Error fetching payments: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to fetch payments")


@admin.patch("/payments/{payment_id}/status")
async def update_payment_status_admin(
    payment_id: str,
    status: str = Query(...),
    provider_txn_id: Optional[str] = Query(None),
    payload=Depends(auth_manager.require_role("admin")),
    db: AsyncSession = Depends(sessionmanager.get_db)
):
    try:
        query = select(Payment).where(Payment.payment_id == payment_id)
        result = await db.execute(query)
        payment = result.scalar_one_or_none()
        
        if not payment:
            raise HTTPException(status_code=404, detail="Payment not found")
        
        payment.status = status
        if provider_txn_id:
            payment.provider_txn_id = provider_txn_id
        
        await db.commit()
        await db.refresh(payment)
        return payment
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating payment status: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to update payment status")


@admin.get("/invoices", response_model=List[InvoiceResponse])
async def get_all_invoices_admin(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    payload=Depends(auth_manager.require_role("admin")),
    db: AsyncSession = Depends(sessionmanager.get_db)
):
    try:
        query = select(Invoice).offset(skip).limit(limit).order_by(Invoice.created_at.desc())
        result = await db.execute(query)
        invoices = result.scalars().all()
        return invoices
    except Exception as e:
        logger.error(f"Error fetching invoices: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to fetch invoices")


@admin.get("/stats")
async def get_admin_stats(
    payload=Depends(auth_manager.require_role("admin")),
    db: AsyncSession = Depends(sessionmanager.get_db)
):
    try:
        users_count = await db.scalar(select(func.count(User.user_id)))
        active_subscriptions = await db.scalar(
            select(func.count(Subscription.subscription_id)).where(Subscription.status == SubscriptionStatus.active)
        )
        total_payments = await db.scalar(select(func.count(Payment.payment_id)))
        paid_payments = await db.scalar(
            select(func.count(Payment.payment_id)).where(Payment.status == "paid")
        )
        total_revenue = await db.scalar(
            select(func.sum(Payment.amount)).where(Payment.status == "paid")
        ) or 0
        
        return {
            "users": users_count or 0,
            "active_subscriptions": active_subscriptions or 0,
            "total_payments": total_payments or 0,
            "paid_payments": paid_payments or 0,
            "total_revenue": float(total_revenue) if total_revenue else 0
        }
    except Exception as e:
        logger.error(f"Error fetching stats: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to fetch stats")

