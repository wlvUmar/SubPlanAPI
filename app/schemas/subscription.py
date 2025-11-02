import enum
from datetime import date, datetime, timezone
from typing import Optional
import uuid
from pydantic import BaseModel, field_serializer, ConfigDict

class SubscriptionStatus(enum.Enum):
	active = "active"
	canceled = "canceled"
	expired = "expired"
	inactive = "inactive"


class PlansEnum(enum.Enum):
	basic = 'basic'
	business = 'business'
	enterprise = 'enterprise'


class PaymentStatus(enum.Enum):
	paid = "paid"
	pending = "pending"
	failed = "failed"


class Currencies(enum.Enum):
	usd = "usd"
	uzs = "uzs"
	rub = "rub"
	jpy = "jpy"


class PlanModel(BaseModel):
	name: str
	price: float
	interval: int = 30
	description: Optional[str] = None
	model_config = ConfigDict(from_attributes=True, ser_json_timedelta="iso8601")

class SubscriptionCreate(BaseModel):
	name: PlansEnum


class SubscriptionResponse(BaseModel):
	subscription_id: uuid.UUID
	status: SubscriptionStatus
	start_date: date
	end_date: Optional[date] = None
	user_id: uuid.UUID
	name: str
	model_config = ConfigDict(from_attributes=True, ser_json_timedelta="iso8601")
		
	@field_serializer("subscription_id")
	def serialize_id(self, v: uuid.UUID, _info):
		return str(v)
	
	@field_serializer("user_id")
	def serialize_user_id(self, v: uuid.UUID, _info):
		return str(v)


class PaymentCreate(BaseModel):
	subscription_id: uuid.UUID
	amount: float
	currency: Currencies = Currencies.usd


class PaymentUpdate(BaseModel):
	status: PaymentStatus
	provider_txn_id: Optional[str] = None


class PaymentResponse(BaseModel):
	payment_id: uuid.UUID
	user_id: uuid.UUID
	subscription_id: uuid.UUID
	amount: float
	currency: str
	status: str
	provider_txn_id: Optional[str] = None
	created_at: datetime
	updated_at: datetime
	
	class Config:
		from_attributes = True
	
	@field_serializer("payment_id")
	def serialize_id(self, v: uuid.UUID, _info):
		return str(v)
	
	@field_serializer("user_id")
	def serialize_user_id(self, v: uuid.UUID, _info):
		return str(v)
	
	@field_serializer("subscription_id")
	def serialize_sub_id(self, v: uuid.UUID, _info):
		return str(v)


class InvoiceResponse(BaseModel):
	invoice_id: uuid.UUID
	user_id: uuid.UUID
	subscription_id: uuid.UUID
	amount: int
	pdf_url: str
	created_at: datetime
	
	class Config:
		from_attributes = True
	
	@field_serializer("invoice_id")
	def serialize_id(self, v: uuid.UUID, _info):
		return str(v)
	
	@field_serializer("user_id")
	def serialize_user_id(self, v: uuid.UUID, _info):
		return str(v)
	
	@field_serializer("subscription_id")
	def serialize_sub_id(self, v: uuid.UUID, _info):
		return str(v)


class DiscountCreate(BaseModel):
	code: str
	discount_amount: int
	expires_at: datetime


class DiscountResponse(BaseModel):
	discount_id: uuid.UUID
	code: str
	discount_amount: int
	expires_at: datetime
	subscription_id: Optional[uuid.UUID] = None
	
	class Config:
		from_attributes = True
	
	@field_serializer("discount_id")
	def serialize_id(self, v: uuid.UUID, _info):
		return str(v)
	
	@field_serializer("subscription_id")
	def serialize_sub_id(self, v: uuid.UUID, _info):
		return str(v) if v else None
