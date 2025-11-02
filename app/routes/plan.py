import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.session import sessionmanager
from app.db.models import Plan as PlanModel, PlansEnum
from app.schemas.subscription import PlanModel as PlanSchema
from core.auth_utils import auth_manager, AuthException

plan = APIRouter(tags=["Plans"])
logger = logging.getLogger("plan_router")


@plan.get("/", response_model=List[PlanSchema])
async def get_all_plans(db: AsyncSession = Depends(sessionmanager.get_db)):
	try:
		query = select(PlanModel)
		result = await db.execute(query)
		plans = result.scalars().all()
		return plans
	except Exception as e:
		logger.error(f"Error fetching plans: {e}", exc_info=True)
		raise HTTPException(status_code=500, detail="Failed to fetch plans")


@plan.get("/{plan_name}", response_model=PlanSchema)
async def get_plan(plan_name: PlansEnum, db: AsyncSession = Depends(sessionmanager.get_db)):
	try:
		query = select(PlanModel).where(PlanModel.name == plan_name)
		result = await db.execute(query)
		plan = result.scalar_one_or_none()
		
		if not plan:
			raise HTTPException(status_code=404, detail=f"Plan {plan_name} not found")
		return plan
	except HTTPException:
		raise
	except Exception as e:
		logger.error(f"Error fetching plan: {e}", exc_info=True)
		raise HTTPException(status_code=500, detail="Failed to fetch plan")


@plan.post("/", response_model=PlanSchema, status_code=201)
async def create_plan(
	plan_data: PlanSchema,
	payload = Depends(auth_manager.require_role("admin")),
	db: AsyncSession = Depends(sessionmanager.get_db)
):
	try:
		existing_query = select(PlanModel).where(PlanModel.name == plan_data.name)
		existing = await db.execute(existing_query)
		if existing.scalar_one_or_none():
			raise HTTPException(status_code=400, detail=f"Plan {plan_data.name} already exists")
		
		new_plan = PlanModel(**plan_data.model_dump())
		db.add(new_plan)
		await db.commit()
		await db.refresh(new_plan)
		return new_plan
		
	except HTTPException:
		raise
	except Exception as e:
		await db.rollback()
		logger.error(f"Error creating plan: {e}", exc_info=True)
		raise HTTPException(status_code=500, detail="Failed to create plan")


@plan.put("/{plan_name}", response_model=PlanSchema)
async def update_plan(
	plan_name: PlansEnum,
	plan_data: PlanSchema,
	payload = Depends(auth_manager.require_role("admin")),
	db: AsyncSession = Depends(sessionmanager.get_db)
):
	try:
		query = select(PlanModel).where(PlanModel.name == plan_name)
		result = await db.execute(query)
		plan = result.scalar_one_or_none()
		
		if not plan:
			raise HTTPException(status_code=404, detail=f"Plan {plan_name} not found")
		
		for key, value in plan_data.model_dump().items():
			setattr(plan, key, value)
		
		await db.commit()
		await db.refresh(plan)
		return plan
	except HTTPException:
		raise
	except Exception as e:
		await db.rollback()
		logger.error(f"Error updating plan: {e}", exc_info=True)
		raise HTTPException(status_code=500, detail="Failed to update plan")


@plan.delete("/{plan_name}", status_code=204)
async def delete_plan(
	plan_name: PlansEnum,
	payload = Depends(auth_manager.require_role("admin")),
	db: AsyncSession = Depends(sessionmanager.get_db)
):
	try:
		query = select(PlanModel).where(PlanModel.name == plan_name)
		result = await db.execute(query)
		plan = result.scalar_one_or_none()
		
		if not plan:
			raise HTTPException(status_code=404, detail=f"Plan {plan_name} not found")
		
		await db.delete(plan)
		await db.commit()
		return None
	except HTTPException:
		raise
	except Exception as e:
		await db.rollback()
		logger.error(f"Error deleting plan: {e}", exc_info=True)
		raise HTTPException(status_code=500, detail="Failed to delete plan")

