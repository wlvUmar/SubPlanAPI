from datetime import datetime, timedelta, timezone
import smtplib 
import logging
from email.mime.text import MIMEText
from uuid import UUID
import uuid

from sqlalchemy.exc import DataError, OperationalError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.models import User
from config import settings

logger = logging.getLogger(__name__)


class UtilException(Exception):

    def __init__(self, message: str = "Error In Utils", status_code: int = 500, details: dict | None = None):
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



def send_email(token:str|UUID|None, 
    to : str,
    subject:str = "MyApp Email Verification",
    header: str = "Welcome to MyApp",
    body: str = "Please verify your email to activate your account.",
    footer: str = "MyApp • 123 Street • If you didn’t register, ignore this email.",
    button_text: str = "Verify Email",
    url:str="http://localhost:8000/user/verify?token=", 
    ):

    button_url = f"{url}{token}"

    msg = MIMEText(settings.html_template.format(
        header=header, 
        body=body, 
        footer=footer, 
        button_text=button_text, 
        button_url=button_url), "html")
    msg["Subject"] = subject
    msg["From"] = "tolibovumar13@gmail.com"
    msg["To"] = to
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login("tolibovumar13@gmail.com", settings.email_password)
            server.send_message(msg)
    except smtplib.SMTPAuthenticationError as e:
        logger.error("Auth failed in SMTP", exc_info=True)
        raise UtilException("Auth failed in SMTP", details={"origin":e})
    except smtplib.SMTPRecipientsRefused:
        raise UtilException("User smtp server refused the email", 403)        
    except smtplib.SMTPConnectError:
        raise UtilException("Cannot connect to SMTP server.")
    except smtplib.SMTPException as e:
        raise UtilException(f"SMTP error", details={"origin":e})

async def verify_user(db:AsyncSession, token):
    try:
        query = select(User).where(User.verification_token == token)
        user = (await db.execute(query)).scalars().first()
    
        if not user:
            raise UtilException("Wrong verification_token", details={"token": token})
        if user.verification_expires_at < datetime.now(timezone.utc):
            user.verification_token = uuid.uuid4()
            user.verification_expires_at = datetime.now(timezone.utc) + timedelta(minutes=15) 
            raise UtilException("Token is expired, try again", details={"expires_at": user.verification_expires_at})
        user.is_verified = True
        user.verification_token=None
        await db.commit()

    except (OperationalError, DataError) as e:
        await db.rollback()
        raise UtilException("Error in utils:db", details={"origin":e})
    except Exception as e:
        await db.rollback()
        raise UtilException("Unexpected Error in utils", details={"origin":e}) 

