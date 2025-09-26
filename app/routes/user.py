import logging
from functools import wraps

from fastapi import APIRouter, Depends, Form, HTTPException, Query, Response, status
from fastapi.background import BackgroundTasks
from fastapi.responses import HTMLResponse
from pydantic import EmailStr, ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.users import PasswordModel, UserModel, UserLogin, UserSchema
from app.db.session import sessionmanager
from config import settings
from core.auth_utils import AuthException, auth_manager
from core.utils import UtilException,  verify_user


user = APIRouter(tags=["Users"])

logger = logging.getLogger("user_router")

def auth_exception_handler(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except AuthException as e:
            if e.status_code != 500:
                raise HTTPException(status_code=e.status_code, detail=e.message)
            logger.error("Error in auth_manager %s", e.details, exc_info=True)
            raise HTTPException(status_code=500, detail="Internal Server Error")
    return wrapper




@user.post("/register", status_code=201)
@auth_exception_handler
async def create_user(user_data: UserModel, backgroundtasks:BackgroundTasks,db : AsyncSession = Depends(sessionmanager.get_db)):
		tokens = await auth_manager.create_user(db, user_data, backgroundtasks)
		tokens["message"] = "Please check your email to activate your account"
		return tokens

@user.post("/login", status_code=200)
@auth_exception_handler
async def login_user(credentials: UserLogin, db: AsyncSession = Depends(sessionmanager.get_db)):
		tokens = await auth_manager.login(db, credentials)	
		return tokens


@user.get("/refresh", status_code=200)
@auth_exception_handler
async def refresh_tokens(user=Depends(auth_manager.decode), 
	db:AsyncSession = Depends(sessionmanager.get_db)):
	
	tokens = await auth_manager.refresh(user.get("jti"), db)
	return tokens



@user.post("/logout")
@auth_exception_handler
async def logout(user=Depends(auth_manager.decode), 
	db:AsyncSession = Depends(sessionmanager.get_db)):
	
	await auth_manager.logout(user.get("jti"), db)
	return Response(204)

@user.get("/me", status_code=200)
@auth_exception_handler
async def get_me(payload=Depends(auth_manager.decode), db:AsyncSession=Depends(sessionmanager.get_db)):
	user = await auth_manager.get_user(payload.get("sub"), db)
	return UserSchema.model_validate(user)


@user.get("/verify", status_code=200)
async def verify_users(db:AsyncSession = Depends(sessionmanager.get_db), token = None):
	try:
		# core.utils.verif_user
		await verify_user(db, token)
		return {"message": "verified"}
	except UtilException as e:
		logger.error("Error in /verify %s", e.details, exc_info=True)
		raise HTTPException(e.status_code, detail=e.message)

@user.post("/forgot-password")
@auth_exception_handler
async def forgot_password(
	backgroundtasks:BackgroundTasks,
	db:AsyncSession=Depends(sessionmanager.get_db), 
	email: EmailStr = Query(...), 
	):
	return await auth_manager.forgot_password(db, email, backgroundtasks)

"""POST /forgot-password – request reset link (email with token)

PUT /reset-password – set new password with token

PUT /change-password – change password (when logged in)

PUT /change-email – update email (requires verification)

DELETE /me – delete own account (GDPR-style)"""

@user.get("/reset-password", response_class=HTMLResponse)
async def reset_password_form(token: str):
    return settings.reset_password_html.format(token=token) 
  
@user.post("/reset-password")
@auth_exception_handler
async def reset_password_submit(
    token: str = Form(...),
    password: str = Form(...),
    confirm: str = Form(...),
    db: AsyncSession = Depends(sessionmanager.get_db),
):
	if password != confirm:
		raise AuthException("Passwords do not match", 400)
	try: 
		PasswordModel(password=password)
	except ValidationError:
		raise AuthException("Weak passowrd")
	return await auth_manager.reset_password(token, db, password)

