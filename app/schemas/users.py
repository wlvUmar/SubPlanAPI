import enum
from datetime import date, datetime, timezone
from typing import Annotated
from uuid import UUID
from pydantic import BaseModel, EmailStr, field_serializer, field_validator
class UserRole(enum.Enum):
	user = "user"
	admin = "admin"

class UserModel(BaseModel):
	name:Annotated[str, "Full name (first_name second_name or vv)"]
	email:EmailStr 
	password: str
	address: Annotated[str, "Full address"]
	is_active: bool = False
	is_verified: bool = False
	role: UserRole = UserRole.user
	created_at: datetime = datetime.now(timezone.utc)
	updated_at: datetime = datetime.now(timezone.utc)

	@field_validator('password')
	@classmethod
	def strong_password(cls, v):
		if len(v) < 8:
			raise ValueError("Password too short")
		if not any(c.islower() for c in v):
			raise ValueError("Password must contain a lowercase letter")
		if not any(c.isupper() for c in v):
			raise ValueError("Password must contain an uppercase letter")
		if not any(c.isdigit() for c in v):
			raise ValueError("Password must contain a digit")
		if not any(c in "#@$!%*?&" for c in v):
			raise ValueError("Password must contain a special char")
		return v

class UserLogin(BaseModel):
	email: EmailStr 
	password: str 

class UserSchema(BaseModel):
    user_id: UUID
    name: str
    email: str
    address:str
    is_active:bool
    is_verified: bool 
    role: str
    created_at: datetime 
    updated_at:datetime
    model_config = {
        "from_attributes": True 
    }
    @field_serializer("user_id")
    def serialize_user_id(self, v:UUID, _info):
    	return str(v)
    	
class PasswordModel(BaseModel):
    password: str

    @field_validator('password')
    @classmethod
    def strong_password(cls, v):
        if len(v) < 8:
            raise ValueError("Password too short")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain a lowercase letter")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain an uppercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain a digit")
        if not any(c in "#@$!%*?&" for c in v):
            raise ValueError("Password must contain a special char")
        return v
