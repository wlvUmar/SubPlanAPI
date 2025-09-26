import enum
from datetime import date, datetime, timezone
from typing import Annotated, List
import uuid
from pydantic import BaseModel, EmailStr, StringConstraints
from pydantic_core.core_schema import DateSchema

from app.schemas.users import UserModel

class SubscriptionStatus(enum.Enum):
	active = "active"
	canceled = "canceled"
	expired = "expired"
	inactive = "inactive"


class SubscriptionModel(BaseModel):
	status: SubscriptionStatus = SubscriptionStatus.inactive
	start_date: date | None = None
	end_date: date | None = None 
	user_id: uuid.UUID
	user: UserModel
