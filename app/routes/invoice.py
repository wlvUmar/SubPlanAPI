import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.session import sessionmanager
from app.db.models import Invoice, Discount
from app.schemas.subscription import InvoiceResponse, DiscountCreate, DiscountResponse
from core.auth_utils import auth_manager

invoice = APIRouter(tags=["Invoices & Discounts"])
logger = logging.getLogger("invoice_router")


@invoice.get("/me", response_model=List[InvoiceResponse])
async def get_my_invoices(
	payload = Depends(auth_manager.decode),
	db: AsyncSession = Depends(sessionmanager.get_db)
):
	try:
		user_id = payload.get("sub")
		query = select(Invoice).where(Invoice.user_id == user_id)
		result = await db.execute(query)
		invoices = result.scalars().all()
		return invoices
	except Exception as e:
		logger.error(f"Error fetching invoices: {e}", exc_info=True)
		raise HTTPException(status_code=500, detail="Failed to fetch invoices")


@invoice.get("/{invoice_id}", response_model=InvoiceResponse)
async def get_invoice(
	invoice_id: str,
	payload = Depends(auth_manager.decode),
	db: AsyncSession = Depends(sessionmanager.get_db)
):
	try:
		user_id = payload.get("sub")
		query = select(Invoice).where(
			Invoice.invoice_id == invoice_id,
			Invoice.user_id == user_id
		)
		result = await db.execute(query)
		invoice = result.scalar_one_or_none()
		
		if not invoice:
			raise HTTPException(status_code=404, detail="Invoice not found")
		
		return invoice
	except HTTPException:
		raise
	except Exception as e:
		logger.error(f"Error fetching invoice: {e}", exc_info=True)
		raise HTTPException(status_code=500, detail="Failed to fetch invoice")


@invoice.get("/", response_model=List[InvoiceResponse])
async def get_all_invoices(
	payload = Depends(auth_manager.require_role("admin")),
	db: AsyncSession = Depends(sessionmanager.get_db)
):
	try:
		query = select(Invoice)
		result = await db.execute(query)
		invoices = result.scalars().all()
		return invoices
	except Exception as e:
		logger.error(f"Error fetching invoices: {e}", exc_info=True)
		raise HTTPException(status_code=500, detail="Failed to fetch invoices")


@invoice.post("/discounts", response_model=DiscountResponse, status_code=201)
async def create_discount(
	discount_data: DiscountCreate,
	payload = Depends(auth_manager.require_role("admin")),
	db: AsyncSession = Depends(sessionmanager.get_db)
):
	try:
		query = select(Discount).where(Discount.code == discount_data.code)
		result = await db.execute(query)
		existing = result.scalar_one_or_none()
		
		if existing:
			raise HTTPException(status_code=400, detail="Discount code already exists")
		
		new_discount = Discount(**discount_data.model_dump())
		db.add(new_discount)
		await db.commit()
		await db.refresh(new_discount)
		return new_discount
	except HTTPException:
		raise
	except Exception as e:
		await db.rollback()
		logger.error(f"Error creating discount: {e}", exc_info=True)
		raise HTTPException(status_code=500, detail="Failed to create discount")


@invoice.get("/discounts", response_model=List[DiscountResponse])
async def get_all_discounts(
	db: AsyncSession = Depends(sessionmanager.get_db)
):
	try:
		query = select(Discount)
		result = await db.execute(query)
		discounts = result.scalars().all()
		return discounts
	except Exception as e:
		logger.error(f"Error fetching discounts: {e}", exc_info=True)
		raise HTTPException(status_code=500, detail="Failed to fetch discounts")


@invoice.delete("/discounts/{discount_id}", status_code=204)
async def delete_discount(
	discount_id: str,
	payload = Depends(auth_manager.require_role("admin")),
	db: AsyncSession = Depends(sessionmanager.get_db)
):
	try:
		query = select(Discount).where(Discount.discount_id == discount_id)
		result = await db.execute(query)
		discount = result.scalar_one_or_none()
		
		if not discount:
			raise HTTPException(status_code=404, detail="Discount not found")
		
		await db.delete(discount)
		await db.commit()
		return None
	except HTTPException:
		raise
	except Exception as e:
		await db.rollback()
		logger.error(f"Error deleting discount: {e}", exc_info=True)
		raise HTTPException(status_code=500, detail="Failed to delete discount")

