#!/usr/bin/env python3

import jwt
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import logging
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

class JWTService:
    """JWT Token Service for user authentication"""
    
    def __init__(self):
        self.jwt_secret = os.getenv('JWT_TOKEN', 'thisisjwttoken')
        self.algorithm = 'HS256'
        self.expiration_hours = 24  # Token expires in 24 hours
    
    def create_token(self, user_id: str, email: str) -> tuple[str, int]:
        """Create a JWT token for user authentication"""
        try:
            expiration_time = datetime.utcnow() + timedelta(hours=self.expiration_hours)
            
            payload = {
                'user_id': user_id,
                'email': email,
                'exp': expiration_time,
                'iat': datetime.utcnow(),
                'type': 'access'
            }
            
            token = jwt.encode(payload, self.jwt_secret, algorithm=self.algorithm)
            expires_in = int(self.expiration_hours * 3600)  # Convert to seconds
            
            logger.info(f"✅ Created JWT token for user: {email}")
            return token, expires_in
            
        except Exception as e:
            logger.error(f"💥 Error creating JWT token: {str(e)}")
            raise
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode a JWT token"""
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=[self.algorithm])
            
            # Check if token is expired
            if datetime.utcnow() > datetime.fromtimestamp(payload['exp']):
                logger.warning("⚠️ JWT token has expired")
                return None
            
            logger.info(f"✅ JWT token verified for user: {payload.get('email')}")
            return payload
            
        except jwt.ExpiredSignatureError:
            logger.warning("⚠️ JWT token has expired")
            return None
        except jwt.InvalidTokenError:
            logger.warning("⚠️ Invalid JWT token")
            return None
        except Exception as e:
            logger.error(f"💥 Error verifying JWT token: {str(e)}")
            return None
    
    def decode_token_without_verification(self, token: str) -> Optional[Dict[str, Any]]:
        """Decode token without verification (for debugging)"""
        try:
            payload = jwt.decode(token, options={"verify_signature": False})
            return payload
        except Exception as e:
            logger.error(f"💥 Error decoding JWT token: {str(e)}")
            return None
    
    def refresh_token(self, token: str) -> Optional[tuple[str, int]]:
        """Refresh an existing JWT token"""
        try:
            payload = self.verify_token(token)
            if not payload:
                return None
            
            # Create new token with same user data
            new_token, expires_in = self.create_token(
                payload['user_id'], 
                payload['email']
            )
            
            logger.info(f"✅ Refreshed JWT token for user: {payload['email']}")
            return new_token, expires_in
            
        except Exception as e:
            logger.error(f"💥 Error refreshing JWT token: {str(e)}")
            return None

# Global JWT service instance
jwt_service = JWTService()

def get_jwt_service() -> JWTService:
    """Get the global JWT service instance"""
    return jwt_service 