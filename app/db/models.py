from typing import Optional
import uuid
import enum
from datetime import datetime, timedelta, timezone, date
from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.types import Date, Enum, DateTime

from .base import Base
from app.schemas import UserRole, SubscriptionStatus



class Currencies(enum.Enum):
	usd = "usd"
	uzs = "uzs"
	rub = "rub"
	jpy = "jpy"

class PaymentStatus(enum.Enum):
	paid = "paid"
	pending= "pending"
	failed= "failed"

class PlansEnum(enum.Enum):
	basic = 'basic'
	business = 'business'
	enterprise = 'enterprise'




class User(Base):
	__tablename__ = 'user'
	user_id : Mapped[uuid.UUID] = mapped_column(UUID(True), primary_key=True, default=uuid.uuid4)
	name : Mapped[str] = mapped_column(nullable=False)
	email: Mapped[str] = mapped_column(unique=True, nullable=False)
	password: Mapped[str] = mapped_column(nullable=False)
	address: Mapped[str] = mapped_column(nullable=False)
	is_active: Mapped[bool] = mapped_column(default=True)
	is_verified: Mapped[bool] = mapped_column(default=False)
	role: Mapped[UserRole] = mapped_column(Enum(UserRole), nullable=False, default=UserRole.user)	
	created_at: Mapped[datetime] = mapped_column(DateTime(True), server_default=func.now())
	updated_at: Mapped[datetime] = mapped_column(DateTime(True),server_default=func.now(), 
		onupdate=datetime.now(timezone.utc))
	verification_token: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(True),default=uuid.uuid4, nullable=True)
	verification_expires_at: Mapped[datetime] = mapped_column(DateTime(True),nullable=True)
	
	subscriptions: Mapped[list["Subscription"]] = relationship(back_populates="user", cascade="all, delete-orphan")
	invoices : Mapped[list["Invoice"]] = relationship(back_populates="user", cascade="all, delete-orphan")
	payments : Mapped[list["Payment"]] = relationship(back_populates="user", cascade="all, delete-orphan")
	refresh_tokens: Mapped[list["RefreshToken"]] = relationship(back_populates="user", cascade="all, delete-orphan")

	
class Subscription(Base):
	__tablename__ = "subscription"
	subscription_id : Mapped[uuid.UUID] = mapped_column(UUID(True), primary_key=True, default=uuid.uuid4)
	status: Mapped[SubscriptionStatus] = mapped_column(Enum(SubscriptionStatus), default=SubscriptionStatus.active)
	
	start_date:Mapped[date] = mapped_column(Date(), default=func.current_date())
	end_date:Mapped[date] = mapped_column(Date(), nullable=True)

	user_id : Mapped[uuid.UUID]=mapped_column(ForeignKey("user.user_id", ondelete="CASCADE"),nullable=False)
	user: Mapped["User"] = relationship(back_populates="subscriptions")
	
	name : Mapped[PlansEnum] = mapped_column(ForeignKey("plan.name",ondelete="CASCADE"))
	plan: Mapped["Plan"] = relationship(back_populates="subscriptions")

	payments: Mapped[list["Payment"]] = relationship(back_populates="subscription",cascade="all, delete-orphan")
	invoices: Mapped[list["Invoice"]] = relationship(back_populates="subscription",cascade="all, delete-orphan")
	discounts: Mapped[list["Discount"]] = relationship(back_populates="subscription",cascade="all, delete-orphan")


class Plan(Base):
	__tablename__ = "plan"
	name : Mapped[PlansEnum] = mapped_column(Enum(PlansEnum),primary_key=True)
	price : Mapped[float] = mapped_column(nullable=False)
	interval: Mapped[int] = mapped_column(default=30)
	description: Mapped[str] = mapped_column(nullable=True)
	subscriptions: Mapped[list["Subscription"]] = relationship(back_populates="plan",cascade="all, delete-orphan")


class Payment(Base):
	__tablename__ = "payment"
	payment_id : Mapped[uuid.UUID] = mapped_column(UUID(True), primary_key=True, default=uuid.uuid4)
	
	user_id : Mapped[uuid.UUID] = mapped_column(ForeignKey("user.user_id",ondelete="CASCADE"),nullable=False)
	user : Mapped["User"] = relationship(back_populates="payments")
	
	subscription_id : Mapped[uuid.UUID] = mapped_column(ForeignKey("subscription.subscription_id",ondelete="CASCADE"),nullable=False)
	subscription : Mapped["Subscription"] = relationship(back_populates="payments")
	
	amount: Mapped[float] = mapped_column(nullable=False)
	currency : Mapped[Currencies] = mapped_column(Enum(Currencies), default=Currencies.usd)
	status : Mapped[PaymentStatus] = mapped_column(Enum(PaymentStatus), default=PaymentStatus.pending)
	provider_txn_id: Mapped[str] = mapped_column(nullable=True, default="")
	created_at: Mapped[datetime] = mapped_column(DateTime(True), server_default=func.now())
	updated_at: Mapped[datetime] = mapped_column(DateTime(True),server_default=func.now(), 
		onupdate=func.now())


class Discount(Base):
	__tablename__ = "discount"
	discount_id: Mapped[uuid.UUID] = mapped_column(UUID(True), primary_key=True, default=uuid.uuid4)
	code: Mapped[str] = mapped_column(unique=True,nullable=False)
	discount_amount: Mapped[int] = mapped_column(nullable=False)
	expires_at: Mapped[datetime] = mapped_column(DateTime(True))

	subscription_id : Mapped[uuid.UUID] = mapped_column(ForeignKey("subscription.subscription_id",ondelete="CASCADE"))
	subscription: Mapped["Subscription"] = relationship(back_populates="discounts")

class Invoice(Base):
	__tablename__ = "invoice"
	invoice_id: Mapped[uuid.UUID] = mapped_column(UUID(True), primary_key=True, default=uuid.uuid4)
	
	user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("user.user_id",ondelete="CASCADE"),nullable=False)
	user : Mapped["User"] = relationship(back_populates="invoices")

	subscription_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("subscription.subscription_id",ondelete="CASCADE"),nullable=False)
	subscription: Mapped["Subscription"] = relationship(back_populates="invoices")
	
	amount: Mapped[int] = mapped_column()
	pdf_url: Mapped[str] = mapped_column(default="")
	created_at: Mapped[datetime] = mapped_column(DateTime(True), 
		server_default=func.now())


class RefreshToken(Base):
	__tablename__= "refresh_token"
	jti: Mapped[uuid.UUID] = mapped_column(UUID(True), primary_key=True, default=uuid.uuid4)
	user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("user.user_id",ondelete="CASCADE"))
	user : Mapped["User"] = relationship(back_populates="refresh_tokens")
	issued_at: Mapped[datetime] = mapped_column(DateTime(True), server_default=func.now())
	expires_at: Mapped[datetime] = mapped_column(DateTime(True))
	revoked: Mapped[bool] = mapped_column(default=False)
