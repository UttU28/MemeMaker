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
    
    def __init__(self):
        self.jwtSecret = os.getenv('JWT_TOKEN', 'thisisjwttoken')
        self.algorithm = 'HS256'
        self.expirationHours = 24
    
    def createToken(self, userId: str, email: str) -> tuple[str, int]:
        try:
            expirationTime = datetime.utcnow() + timedelta(hours=self.expirationHours)
            
            payload = {
                'user_id': userId,
                'email': email,
                'exp': expirationTime,
                'iat': datetime.utcnow(),
                'type': 'access'
            }
            
            token = jwt.encode(payload, self.jwtSecret, algorithm=self.algorithm)
            expiresIn = int(self.expirationHours * 3600)
            
            logger.info(f"🔐 Created JWT token for: {email}")
            return token, expiresIn
            
        except Exception as e:
            logger.error(f"�� JWT token creation failed: {str(e)}")
            raise
    
    def verifyToken(self, token: str) -> Optional[Dict[str, Any]]:
        try:
            payload = jwt.decode(token, self.jwtSecret, algorithms=[self.algorithm])
            
            if datetime.utcnow() > datetime.fromtimestamp(payload['exp']):
                logger.warning("⚠️ JWT token expired")
                return None
            
            logger.info(f"✅ JWT verified: {payload.get('email')}")
            return payload
            
        except jwt.ExpiredSignatureError:
            logger.warning("⚠️ JWT token expired")
            return None
        except jwt.InvalidTokenError:
            logger.warning("⚠️ Invalid JWT token")
            return None
        except Exception as e:
            logger.error(f"💥 JWT verification failed: {str(e)}")
            return None
    
    def decodeTokenWithoutVerification(self, token: str) -> Optional[Dict[str, Any]]:
        try:
            payload = jwt.decode(token, options={"verify_signature": False})
            return payload
        except Exception as e:
            logger.error(f"💥 JWT decode failed: {str(e)}")
            return None
    
    def refreshToken(self, token: str) -> Optional[tuple[str, int]]:
        try:
            payload = self.verifyToken(token)
            if not payload:
                return None
            
            newToken, expiresIn = self.createToken(
                payload['user_id'], 
                payload['email']
            )
            
            logger.info(f"🔄 JWT refreshed for: {payload['email']}")
            return newToken, expiresIn
            
        except Exception as e:
            logger.error(f"💥 JWT refresh failed: {str(e)}")
            return None

jwtService = JWTService()

def getJwtService() -> JWTService:
    return jwtService 