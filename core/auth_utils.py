import traceback
import uuid
from fastapi import BackgroundTasks, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import jwt, logging
from datetime import timedelta, datetime , timezone
from passlib.hash import bcrypt
from sqlalchemy.exc import DataError, IntegrityError, OperationalError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.db.models import RefreshToken, User, Subscription
from app.schemas.users import UserLogin, UserModel
from config import settings
from core.utils import UtilException, send_email

bearer_schema = HTTPBearer()


class AuthException(Exception):

    def __init__(self, message: str = "Authentication failed", status_code: int = 401, details: dict | None = None):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(message)

    def as_dict(self) -> dict:
        return {
            "message": self.message,
            "status_code": self.status_code,
            "details": self.details
        }
    def __str__(self):
        return f"{self.status_code} {self.message}"

class AuthManager:
	def __init__(self) -> None:
		from logger_setup import setup_logging
		setup_logging()
		self.logger = logging.getLogger(self.__class__.__name__)
		self._secret = settings.SECRET
		self._algorithm = settings.ALGORITHM
	def _hash(self, password:str)->str:
		try:
			self.logger.debug("Hashing the password")
			return 	bcrypt.hash(password)
		except Exception as e:
			raise AuthException("Internal error hashing password", 500, details={"origin":e, "traceback": traceback.format_exc()})

	def _verify(self, password:str, hash:str)->bool:
		try:
			self.logger.debug("verifying the password")
			return bcrypt.verify(password, hash)
		except Exception as e:
			raise AuthException("Internal error verifying password", 500, details={"origin":e,"traceback": traceback.format_exc()})

	def _create_access_token(self, subject, role, exp=None):
		try:	
			self.logger.debug("_create_access_token called")
			now = datetime.now(timezone.utc)
			exp = now + timedelta(minutes=exp or 30)
			payload = {"sub": str(subject), 
				"role": str(role), 
				"exp":exp, 
				}
			
			encoded = jwt.encode(payload, self._secret, self._algorithm)
			return encoded
		except jwt.PyJWTError as e:
			raise AuthException("Failed to create access token", 500, details={"origin":e,"traceback": traceback.format_exc()})

	def _create_refresh_token(self, subject):
		self.logger.debug("_create_refresh_token called")
		try:
			now = datetime.now(timezone.utc)

			payload = {
			"subject": str(subject),
			"jti": str(uuid.uuid4()),
			"exp": now + timedelta(weeks=1)
			}
			new_record = RefreshToken(jti=payload['jti'], user_id=subject, expires_at=payload["exp"])
			token = jwt.encode(payload, self._secret, self._algorithm)
			return new_record ,token
		except jwt.PyJWTError as e:
			raise AuthException("Failed to create refresh token", 500, details={"origin":e,"traceback": traceback.format_exc()})

	async def login(self, db: AsyncSession, credentials:UserLogin, exp = None)->dict:
		self.logger.debug("AuthManager.login called")
		query = select(User.user_id, User.password, User.role).where(User.email == credentials.email)
		try:
			user = (await db.execute(query)).first()
		except (OperationalError, DataError) as e:
			raise AuthException("Database query failed", 500, {"db_error": e,"traceback": traceback.format_exc()})

		if not user:
			raise AuthException("User not found", 400)

		user_id ,user_password, role = user
		if not self._verify(credentials.password, user_password):
			raise AuthException("Invalid password or user_id", 400)
		
		access_token = self._create_access_token(user_id, role.value, exp)
		new_token, refresh_token =  self._create_refresh_token(user_id)
		
		try:
			db.add(new_token)

			self.logger.debug("Issuing an INSERT query")
			await db.flush()
			await db.commit()

		except (DataError, OperationalError) as e:
			raise AuthException("Failed to store refresh_token", 500, {'db_error': str(e)})
		except Exception as e:
			raise AuthException("Unexpected Error during db Operation", 500) from e

		return {"access":access_token, "refresh": refresh_token} 

	async def create_user(self, db:AsyncSession, user:UserModel, background_tasks:BackgroundTasks):
		self.logger.debug("AuthManager.create_user called")
		try:
			async with db.begin():
				self.logger.debug("AuthManager.create_user Transaction started")
				user = user.model_copy(update={"password": self._hash(user.password)})
				new_user = User(**user.model_dump())
				db.add(new_user)
				await db.flush()
				subscription = Subscription(user_id=new_user.user_id, name="basic")
				db.add(subscription)

				new_user.verification_expires_at = datetime.now(timezone.utc) + timedelta(minutes=15)
				background_tasks.add_task(send_email, str(new_user.verification_token), new_user.email)

				token = self._create_access_token(new_user.user_id, new_user.role.value)
				new_token, refresh_token =  self._create_refresh_token(new_user.user_id)
				db.add(new_token)
			return {"access": token, "refresh": refresh_token} 
		except UtilException as e:
			raise AuthException(f"Error in utils.send_email: {e.message}", e.status_code, details=e.details)
		except IntegrityError as e:
			if "unique" in str(e.orig).lower():  
				raise AuthException("User is already registered", 400)
			raise AuthException("Database integrity error", 400, {"db_error": str(e)})
		except (DataError, OperationalError) as e:
			raise AuthException("User creation failed", 400, {"db_error": str(e)})
		except jwt.PyJWTError as e:
			raise AuthException("Failed to create JWT tokens", 500)
		except Exception as e:
			raise AuthException("Failed to add user to db") from e
	
	async def decode(self, creds:HTTPAuthorizationCredentials=Depends(bearer_schema)):
		self.logger.debug("AuthManager.decode called")
		token = creds.credentials

		try:
			payload = jwt.decode(token, self._secret, algorithms=[self._algorithm])
			self.logger.debug(f"159: {payload}")
			return payload 
		except jwt.ExpiredSignatureError:
			raise HTTPException(status_code=401, detail="Token expired")
		except jwt.InvalidTokenError:
			self.logger.debug(token)
			raise HTTPException(status_code=401, detail="Invalid token")
		except Exception as e:
			self.logger.error("Unexpected error decoding token", exc_info=True)
			raise HTTPException(status_code=500, detail={"msg":"Failed to decode token","origin":e})
	
	async def refresh(self, jti, db:AsyncSession):
		self.logger.debug("AuthManager.refresh called")
		try:
			async with db.begin():
				query = select(RefreshToken).options(selectinload(RefreshToken.user)).where(RefreshToken.jti == jti)
				result = (await db.execute(query)).scalar()
				if result is None:
					raise AuthException("Invalid jti")
				if result.revoked:
					raise AuthException("Refresh Token has already been used")
				if result.expires_at < datetime.now(timezone.utc):
					raise AuthException("Refresh Token is Expired, Login again", details={"expires_at": result.expires_at})
		
				result.revoked = True
		
				new_token, refresh_token = self._create_refresh_token(result.user.user_id)
				db.add(new_token)
		
			access_token = self._create_access_token(result.user.user_id, result.user.role.value)
			return {"access": access_token, "refresh":refresh_token}

		except OperationalError as e:
			raise AuthException("Database error in AuthManager.refresh", 500, {"db_error": str(e)})
		except Exception as e:
			raise AuthException("Unexpected error during refresh query", 500)

	async def logout(self, jti:str, db:AsyncSession):
		try:
			async with db.begin():
				query = select(RefreshToken).where(RefreshToken.jti == jti)
				result = (await db.execute(query)).scalar_one_or_none()
				if result is None:
					raise AuthException("Invalid jti")
				if result.revoked:
					raise AuthException("Refresh Token has already been revoked")
				result.revoked = True
			return True
		except OperationalError as e:
			raise AuthException("Database error in AuthManager.logout", 500, {"db_error": str(e)})
		except Exception as e:
			raise AuthException("Unexpected error during logout", 500)

	async def logout_all(self, user_id:str, db:AsyncSession):
		try:
			async with db.begin():
				query = select(RefreshToken).where(RefreshToken.user_id == user_id)
				tokens = (await db.execute(query)).scalars().all()
				for token in tokens:
					token.revoked = True
			return True
		except OperationalError as e:
			raise AuthException("Database error in AuthManager.logout_all", 500, {"db_error": str(e)})
		except Exception as e:
			raise AuthException("Unexpected error during logout_all", 500)

	async def get_user(self, user_id, db:AsyncSession):
		try:
			query = select(User).where(User.user_id == user_id)
			user = (await db.execute(query)).scalar_one_or_none()
			if not user:
				raise AuthException(f"User with id {user_id} dont exist", 404)
			return user
		except OperationalError as e:
			raise AuthException("Database error in AuthManager.get_user", 500, {"db_error": str(e)})
		except Exception as e:
			raise AuthException("Unexpected error in get user", 500)

	def require_role(self, role: str):
		def wrapper(user=Depends(self.decode)):
			if user.get("role") != role :
				self.logger.debug(f"{user.get("role")}, {role}")
				raise AuthException(status_code=403, message="Forbidden")
			return user
		return wrapper

	async def forgot_password(self, db:AsyncSession, email, background_tasks:BackgroundTasks):
		try:
			query = select(User).where(User.email == email)
			user = (await db.execute(query)).scalars().first()
			new_token = uuid.uuid4()
			if not user:
				raise AuthException("User with this email don't exist")
			if not user.is_verified:
				background_tasks.add_task(send_email, user.verification_token, email)
				raise AuthException("Verify your email first")

			user.verification_token = new_token
			user.verification_expires_at = datetime.now(timezone.utc) + timedelta(minutes=15) 
			background_tasks.add_task(send_email, new_token, 
				email, 
				body="Please follow the link to reset your password", 
				subject="Reset Password Request",
				button_text="Reset Password",
				url="http://localhost:8000/user/reset-password?token=")
			await db.commit()
			return {"message": "We've sent you an email with link to reset password"}
		except UtilException as e:
			raise AuthException(f"Error in utils.send_email: {e.message}", e.status_code, details=e.details)
		except (OperationalError, DataError) as e:
			await db.rollback()
			raise AuthException("Database error in forgot_password", 500, details={"origin": e})

		except Exception as e:
			await db.rollback()
			raise AuthException("Unexpected error in forgot_password", 500, details={"origin": e})

	async def reset_password(self, token, db:AsyncSession, new_password):
		try:
			query = select(User).where(User.verification_token == token)
			user = (await db.execute(query)).scalars().first()

			if not user:
				raise AuthException("Invalid or expired token", 400)

			if user.verification_expires_at < datetime.now(timezone.utc):
				raise AuthException("Token expired, try again", details={"expires_at": user.verification_expires_at})			

			user.password = self._hash(new_password)
			user.verification_token = None
			await db.commit()
			return {"message": "Password Changed"}
		except OperationalError as e:
			raise AuthException("Database Error in reset_password", 500, details={"origin":e})
		except Exception as e:
			raise AuthException("Unexpected Error in reset_password", 500, details={"origin":e})

	async def change_password(self, user_id: str, db:AsyncSession, old_password: str, new_password: str):
		try:
			query = select(User).where(User.user_id == user_id)
			user = (await db.execute(query)).scalars().first()
			
			if not user:
				raise AuthException("User not found", 404)
			
			if not self._verify(old_password, user.password):
				raise AuthException("Invalid old password", 400)
			
			user.password = self._hash(new_password)
			await db.commit()
			return {"message": "Password changed successfully"}
		except OperationalError as e:
			raise AuthException("Database Error in change_password", 500, details={"origin":e})
		except Exception as e:
			raise AuthException("Unexpected Error in change_password", 500, details={"origin":e})




auth_manager = AuthManager()