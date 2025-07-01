#!/usr/bin/env python3

import firebase_admin
from firebase_admin import credentials, firestore, auth
import os
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
import jwt
import requests
import json
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

class FirebaseService:
    def __init__(self, credentialsPath: str = "firebase.json"):
        self.credentialsPath = credentialsPath
        self.db = None
        self.app = None
        self.initializeFirebase()
    
    def initializeFirebase(self):
        try:
            if not os.path.exists(self.credentialsPath):
                raise FileNotFoundError(f"Firebase credentials file not found: {self.credentialsPath}")
            
            try:
                self.app = firebase_admin.get_app()
                logger.info("🔥 Firebase already initialized")
            except ValueError:
                cred = credentials.Certificate(self.credentialsPath)
                self.app = firebase_admin.initialize_app(cred)
                logger.info("🔥 Firebase initialized successfully")
            
            self.db = firestore.client()
            logger.info("📊 Firestore client initialized")
            
        except Exception as e:
            logger.error(f"💥 Firebase initialization failed: {str(e)}")
            raise
    
    def testConnection(self) -> bool:
        try:
            testRef = self.db.collection('test').document('connection_test')
            testData = {
                'timestamp': datetime.now(),
                'status': 'connected'
            }
            
            testRef.set(testData)
            doc = testRef.get()
            
            if doc.exists:
                testRef.delete()
                logger.info("✅ Firebase connection test successful")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"💥 Firebase connection test failed: {str(e)}")
            return False
    
    def getAllUserProfiles(self) -> Dict[str, Any]:
        try:
            profilesRef = self.db.collection('user_profiles')
            docs = profilesRef.stream()
            
            users = {}
            defaultUser = None
            
            for doc in docs:
                if doc.id == '_metadata':
                    metadata = doc.to_dict()
                    defaultUser = metadata.get('defaultUser')
                else:
                    users[doc.id] = doc.to_dict()
            
            result = {
                "users": users,
                "defaultUser": defaultUser
            }
            
            logger.info(f"📄 Retrieved {len(users)} user profiles")
            return result
            
        except Exception as e:
            logger.error(f"💥 Error getting user profiles: {str(e)}")
            return {"users": {}, "defaultUser": None}
    
    def saveUserProfiles(self, profilesData: Dict[str, Any]) -> bool:
        try:
            batch = self.db.batch()
            
            metadataRef = self.db.collection('user_profiles').document('_metadata')
            metadata = {
                'defaultUser': profilesData.get('defaultUser'),
                'updatedAt': datetime.now()
            }
            batch.set(metadataRef, metadata)
            
            users = profilesData.get('users', {})
            for userId, userData in users.items():
                userRef = self.db.collection('user_profiles').document(userId)
                if 'updatedAt' not in userData:
                    userData['updatedAt'] = datetime.now().isoformat()
                batch.set(userRef, userData)
            
            batch.commit()
            logger.info(f"✅ Saved {len(users)} user profiles")
            return True
            
        except Exception as e:
            logger.error(f"💥 Error saving user profiles: {str(e)}")
            return False
    
    def getUserProfile(self, userId: str) -> Optional[Dict[str, Any]]:
        try:
            userRef = self.db.collection('user_profiles').document(userId)
            doc = userRef.get()
            
            if doc.exists:
                return doc.to_dict()
            
            return None
            
        except Exception as e:
            logger.error(f"💥 Error getting user profile {userId}: {str(e)}")
            return None
    
    def saveUserProfile(self, userId: str, userData: Dict[str, Any]) -> bool:
        try:
            userRef = self.db.collection('user_profiles').document(userId)
            userData['updatedAt'] = datetime.now().isoformat()
            userRef.set(userData)
            
            logger.info(f"✅ Saved user profile: {userId}")
            return True
            
        except Exception as e:
            logger.error(f"💥 Error saving user profile {userId}: {str(e)}")
            return False
    
    def deleteUserProfile(self, userId: str) -> bool:
        try:
            userRef = self.db.collection('user_profiles').document(userId)
            userRef.delete()
            
            logger.info(f"🗑️ Deleted user profile: {userId}")
            return True
            
        except Exception as e:
            logger.error(f"💥 Error deleting user profile {userId}: {str(e)}")
            return False
    
    def getAllScripts(self) -> Dict[str, Any]:
        try:
            scriptsRef = self.db.collection('scripts')
            docs = scriptsRef.stream()
            
            scripts = {}
            
            for doc in docs:
                if doc.id != '_metadata':
                    scripts[doc.id] = doc.to_dict()
            
            result = {
                "scripts": scripts
            }
            
            logger.info(f"📝 Retrieved {len(scripts)} scripts")
            return result
            
        except Exception as e:
            logger.error(f"💥 Error getting scripts: {str(e)}")
            return {"scripts": {}}
    
    def saveScripts(self, scriptsData: Dict[str, Any]) -> bool:
        try:
            batch = self.db.batch()
            
            metadataRef = self.db.collection('scripts').document('_metadata')
            metadata = {
                'updatedAt': datetime.now()
            }
            batch.set(metadataRef, metadata)
            
            scripts = scriptsData.get('scripts', {})
            for scriptId, scriptData in scripts.items():
                scriptRef = self.db.collection('scripts').document(scriptId)
                if 'updatedAt' not in scriptData:
                    scriptData['updatedAt'] = datetime.now().isoformat()
                batch.set(scriptRef, scriptData)
            
            batch.commit()
            logger.info(f"✅ Saved {len(scripts)} scripts")
            return True
            
        except Exception as e:
            logger.error(f"💥 Error saving scripts: {str(e)}")
            return False
    
    def getScript(self, scriptId: str) -> Optional[Dict[str, Any]]:
        try:
            scriptRef = self.db.collection('scripts').document(scriptId)
            doc = scriptRef.get()
            
            if doc.exists:
                return doc.to_dict()
            
            return None
            
        except Exception as e:
            logger.error(f"💥 Error getting script {scriptId}: {str(e)}")
            return None
    
    def saveScript(self, scriptId: str, scriptData: Dict[str, Any]) -> bool:
        try:
            scriptRef = self.db.collection('scripts').document(scriptId)
            scriptData['updatedAt'] = datetime.now().isoformat()
            scriptRef.set(scriptData)
            
            logger.info(f"✅ Saved script: {scriptId}")
            return True
            
        except Exception as e:
            logger.error(f"💥 Error saving script {scriptId}: {str(e)}")
            return False
    
    def deleteScript(self, scriptId: str) -> bool:
        try:
            scriptRef = self.db.collection('scripts').document(scriptId)
            scriptRef.delete()
            
            logger.info(f"🗑️ Deleted script: {scriptId}")
            return True
            
        except Exception as e:
            logger.error(f"💥 Error deleting script {scriptId}: {str(e)}")
            return False
    
    def createUser(self, email: str, password: str, name: str) -> tuple[bool, str, Optional[str]]:
        try:
            apiKey = os.getenv('FIREBASE_API_KEY')
            if not apiKey:
                logger.error("🔑 Firebase API Key not found in environment")
                return False, "Authentication configuration error", None
            
            url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={apiKey}"
            
            payload = {
                "email": email,
                "password": password,
                "returnSecureToken": True
            }
            
            response = requests.post(url, json=payload)
            
            if response.status_code == 200:
                result = response.json()
                userId = result.get('localId')
                
                try:
                    auth.update_user(userId, display_name=name)
                except Exception as e:
                    logger.warning(f"⚠️ Could not update display name: {str(e)}")
                
                currentTime = datetime.now().isoformat()
                userData = {
                    'name': name,
                    'email': email,
                    'isVerified': False,
                                    'subscription': 'free',
                'generatedCharacters': [],
                'generatedScripts': [],
                'favCharacters': [],
                'createdAt': currentTime,
                    'updatedAt': currentTime
                }
                
                userRef = self.db.collection('users').document(userId)
                userRef.set(userData)
                
                logger.info(f"✅ Created user: {email}")
                return True, "User created successfully", userId
                
            else:
                errorData = response.json()
                errorMessage = errorData.get('error', {}).get('message', 'User creation failed')
                
                if 'EMAIL_EXISTS' in errorMessage:
                    logger.warning(f"⚠️ Email already exists: {email}")
                    return False, "Email already exists", None
                elif 'WEAK_PASSWORD' in errorMessage:
                    logger.warning(f"⚠️ Weak password: {email}")
                    return False, "Password should be at least 6 characters", None
                elif 'INVALID_EMAIL' in errorMessage:
                    logger.warning(f"⚠️ Invalid email: {email}")
                    return False, "Invalid email format", None
                else:
                    logger.warning(f"⚠️ User creation failed: {errorMessage}")
                    return False, f"User creation failed: {errorMessage}", None
            
        except requests.exceptions.RequestException as e:
            logger.error(f"💥 Network error: {str(e)}")
            return False, "User creation service unavailable", None
        except Exception as e:
            logger.error(f"💥 Error creating user {email}: {str(e)}")
            return False, f"User creation failed: {str(e)}", None
    
    def verifyUserPassword(self, email: str, password: str) -> tuple[bool, str, Optional[str]]:
        try:
            apiKey = os.getenv('FIREBASE_API_KEY')
            if not apiKey:
                logger.error("🔑 Firebase API Key not found in environment")
                return False, "Authentication configuration error", None
            
            url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={apiKey}"
            
            payload = {
                "email": email,
                "password": password,
                "returnSecureToken": True
            }
            
            response = requests.post(url, json=payload)
            
            if response.status_code == 200:
                result = response.json()
                userId = result.get('localId')
                logger.info(f"✅ User authenticated: {email}")
                return True, "User authenticated", userId
            else:
                errorData = response.json()
                errorMessage = errorData.get('error', {}).get('message', 'Authentication failed')
                
                if 'EMAIL_NOT_FOUND' in errorMessage or 'INVALID_PASSWORD' in errorMessage:
                    logger.warning(f"⚠️ Invalid credentials: {email}")
                    return False, "Invalid email or password", None
                else:
                    logger.warning(f"⚠️ Authentication failed: {errorMessage}")
                    return False, "Invalid email or password", None
            
        except requests.exceptions.RequestException as e:
            logger.error(f"💥 Network error: {str(e)}")
            return False, "Authentication service unavailable", None
        except Exception as e:
            logger.error(f"💥 Error verifying user {email}: {str(e)}")
            return False, f"Authentication failed: {str(e)}", None
    
    def getUserById(self, userId: str) -> Optional[Dict[str, Any]]:
        try:
            userRef = self.db.collection('users').document(userId)
            doc = userRef.get()
            
            if doc.exists:
                userData = doc.to_dict()
                userData['id'] = userId
                return userData
            
            return None
            
        except Exception as e:
            logger.error(f"💥 Error getting user {userId}: {str(e)}")
            return None
    
    def getUserByEmail(self, email: str) -> Optional[Dict[str, Any]]:
        try:
            userRecord = auth.get_user_by_email(email)
            userId = userRecord.uid
            
            return self.getUserById(userId)
            
        except auth.UserNotFoundError:
            logger.warning(f"⚠️ User not found: {email}")
            return None
        except Exception as e:
            logger.error(f"💥 Error getting user by email {email}: {str(e)}")
            return None

    def getUserNameById(self, userId: str) -> Optional[str]:
        try:
            if not userId:
                return None
                
            userRef = self.db.collection('users').document(userId)
            doc = userRef.get()
            
            if doc.exists:
                userData = doc.to_dict()
                return userData.get('name', 'Unknown User')
            
            return None
            
        except Exception as e:
            logger.error(f"💥 Error getting user name for {userId}: {str(e)}")
            return None
    
    def updateUser(self, userId: str, userData: Dict[str, Any]) -> bool:
        try:
            userRef = self.db.collection('users').document(userId)
            userData['updatedAt'] = datetime.now().isoformat()
            userRef.update(userData)
            
            logger.info(f"✅ Updated user: {userId}")
            return True
            
        except Exception as e:
            logger.error(f"💥 Error updating user {userId}: {str(e)}")
            return False
    
    def deleteUser(self, userId: str) -> bool:
        try:
            auth.delete_user(userId)
            
            userRef = self.db.collection('users').document(userId)
            userRef.delete()
            
            logger.info(f"🗑️ Deleted user: {userId}")
            return True
            
        except Exception as e:
            logger.error(f"💥 Error deleting user {userId}: {str(e)}")
            return False
    
    def createCharacterWithOwner(self, characterId: str, characterData: Dict[str, Any], ownerUserId: str) -> bool:
        try:
            characterData['createdBy'] = ownerUserId
            characterData['createdAt'] = datetime.now().isoformat()
            characterData['updatedAt'] = datetime.now().isoformat()
            characterData['scripts'] = []  # Initialize empty scripts array
            
            batch = self.db.batch()
            
            characterRef = self.db.collection('user_profiles').document(characterId)
            batch.set(characterRef, characterData)
            
            userRef = self.db.collection('users').document(ownerUserId)
            characterInfo = {
                'id': characterId,
                'displayName': characterData.get('displayName', characterId),
                'createdAt': characterData['createdAt']
            }
            
            batch.update(userRef, {
                'generatedCharacters': firestore.ArrayUnion([characterInfo]),
                'updatedAt': datetime.now().isoformat()
            })
            
            batch.commit()
            
            logger.info(f"✅ Created character {characterId} for user {ownerUserId}")
            return True
            
        except Exception as e:
            logger.error(f"💥 Error creating character with owner: {str(e)}")
            return False
    
    def deleteCharacterWithOwnerCleanup(self, characterId: str) -> bool:
        try:
            characterData = self.getUserProfile(characterId)
            if not characterData:
                logger.warning(f"⚠️ Character {characterId} not found")
                return False
            
            ownerUserId = characterData.get('createdBy')
            
            batch = self.db.batch()
            
            characterRef = self.db.collection('user_profiles').document(characterId)
            batch.delete(characterRef)
            
            if ownerUserId:
                try:
                    userRef = self.db.collection('users').document(ownerUserId)
                    
                    characterInfo = {
                        'id': characterId,
                        'displayName': characterData.get('displayName', characterId),
                        'createdAt': characterData.get('createdAt', '')
                    }
                    
                    batch.update(userRef, {
                        'generatedCharacters': firestore.ArrayRemove([characterInfo]),
                        'updatedAt': datetime.now().isoformat()
                    })
                    
                except Exception as e:
                    logger.warning(f"⚠️ Could not clean up user's characters: {str(e)}")
            
            batch.commit()
            
            logger.info(f"✅ Deleted character {characterId}")
            return True
            
        except Exception as e:
            logger.error(f"💥 Error deleting character: {str(e)}")
            return False
    
    def getUserCharacters(self, userId: str) -> List[Dict[str, Any]]:
        try:
            charactersRef = self.db.collection('user_profiles')
            query = charactersRef.where('createdBy', '==', userId)
            docs = query.stream()
            
            characters = []
            for doc in docs:
                characterData = doc.to_dict()
                characterData['id'] = doc.id
                characters.append(characterData)
            
            logger.info(f"📄 Retrieved {len(characters)} characters for user {userId}")
            return characters
            
        except Exception as e:
            logger.error(f"💥 Error getting user characters: {str(e)}")
            return []
    
    def updateCharacterWithOwnerCheck(self, characterId: str, characterData: Dict[str, Any], requestingUserId: str) -> bool:
        try:
            existingCharacter = self.getUserProfile(characterId)
            if not existingCharacter:
                logger.warning(f"⚠️ Character {characterId} not found")
                return False
            
            characterOwner = existingCharacter.get('createdBy')
            if characterOwner != requestingUserId:
                logger.warning(f"⚠️ Unauthorized update attempt for character {characterId}")
                return False
            
            characterData['updatedAt'] = datetime.now().isoformat()
            characterRef = self.db.collection('user_profiles').document(characterId)
            characterRef.update(characterData)
            
            if 'displayName' in characterData and characterOwner:
                try:
                    userRef = self.db.collection('users').document(characterOwner)
                    userDoc = userRef.get()
                    
                    if userDoc.exists:
                        userData = userDoc.to_dict()
                        generatedCharacters = userData.get('generatedCharacters', [])
                        
                        for i, charInfo in enumerate(generatedCharacters):
                            if charInfo.get('id') == characterId:
                                generatedCharacters[i]['displayName'] = characterData['displayName']
                                break
                        
                        userRef.update({
                            'generatedCharacters': generatedCharacters,
                            'updatedAt': datetime.now().isoformat()
                        })
                    
                except Exception as e:
                    logger.warning(f"⚠️ Could not update user's characters: {str(e)}")
            
            logger.info(f"✅ Updated character {characterId}")
            return True
            
        except Exception as e:
            logger.error(f"💥 Error updating character: {str(e)}")
            return False

    def starCharacter(self, characterId: str, userId: str) -> tuple[bool, str, int]:
        try:
            batch = self.db.batch()
            
            characterRef = self.db.collection('user_profiles').document(characterId)
            characterDoc = characterRef.get()
            
            if not characterDoc.exists:
                return False, f"Character {characterId} not found", 0
            
            characterData = characterDoc.to_dict()
            characterName = characterData.get('displayName', characterId)
            
            userRef = self.db.collection('users').document(userId)
            userDoc = userRef.get()
            
            if not userDoc.exists:
                return False, f"User {userId} not found", 0
            
            userData = userDoc.to_dict()
            favCharacters = userData.get('favCharacters', [])
            
            alreadyStarred = any(fav['charId'] == characterId for fav in favCharacters)
            if alreadyStarred:
                return False, "Character already starred", characterData.get('starred', 0)
            
            newFavorite = {
                'charId': characterId,
                'charName': characterName
            }
            favCharacters.append(newFavorite)
            
            batch.update(userRef, {
                'favCharacters': favCharacters,
                'updatedAt': datetime.now().isoformat()
            })
            
            currentStarred = characterData.get('starred', 0)
            newStarredCount = currentStarred + 1
            
            batch.update(characterRef, {
                'starred': newStarredCount,
                'updatedAt': datetime.now().isoformat()
            })
            
            batch.commit()
            
            logger.info(f"⭐ User {userId} starred character {characterId}")
            return True, "Character starred successfully", newStarredCount
            
        except Exception as e:
            logger.error(f"💥 Error starring character: {str(e)}")
            return False, f"Failed to star character: {str(e)}", 0

    def unstarCharacter(self, characterId: str, userId: str) -> tuple[bool, str, int]:
        try:
            batch = self.db.batch()
            
            characterRef = self.db.collection('user_profiles').document(characterId)
            characterDoc = characterRef.get()
            
            if not characterDoc.exists:
                return False, f"Character {characterId} not found", 0
            
            characterData = characterDoc.to_dict()
            
            userRef = self.db.collection('users').document(userId)
            userDoc = userRef.get()
            
            if not userDoc.exists:
                return False, f"User {userId} not found", 0
            
            userData = userDoc.to_dict()
            favCharacters = userData.get('favCharacters', [])
            
            starredIndex = -1
            for i, fav in enumerate(favCharacters):
                if fav.get('charId') == characterId:
                    starredIndex = i
                    break
            
            if starredIndex == -1:
                return False, "Character not starred by this user", characterData.get('starred', 0)
            
            favCharacters.pop(starredIndex)
            
            batch.update(userRef, {
                'favCharacters': favCharacters,
                'updatedAt': datetime.now().isoformat()
            })
            
            currentStarred = characterData.get('starred', 0)
            newStarredCount = max(0, currentStarred - 1)
            
            batch.update(characterRef, {
                'starred': newStarredCount,
                'updatedAt': datetime.now().isoformat()
            })
            
            batch.commit()
            
            logger.info(f"⭐ User {userId} unstarred character {characterId}")
            return True, "Character unstarred successfully", newStarredCount
            
        except Exception as e:
            logger.error(f"💥 Error unstarring character: {str(e)}")
            return False, f"Failed to unstar character: {str(e)}", 0

    def isCharacterStarredByUser(self, characterId: str, userId: str) -> bool:
        try:
            userRef = self.db.collection('users').document(userId)
            userDoc = userRef.get()
            
            if not userDoc.exists:
                return False
            
            userData = userDoc.to_dict()
            favCharacters = userData.get('favCharacters', [])
            
            return any(fav.get('charId') == characterId for fav in favCharacters)
            
        except Exception as e:
            logger.error(f"💥 Error checking if character is starred: {str(e)}")
            return False

    def getUserFavoriteCharacters(self, userId: str) -> List[Dict[str, Any]]:
        try:
            userRef = self.db.collection('users').document(userId)
            userDoc = userRef.get()
            
            if not userDoc.exists:
                return []
            
            userData = userDoc.to_dict()
            favCharacters = userData.get('favCharacters', [])
            
            favoriteCharsData = []
            for fav in favCharacters:
                charId = fav.get('charId')
                if charId:
                    charData = self.getUserProfile(charId)
                    if charData:
                        charData['id'] = charId
                        favoriteCharsData.append(charData)
            
            logger.info(f"📄 Retrieved {len(favoriteCharsData)} favorite characters for user {userId}")
            return favoriteCharsData
            
        except Exception as e:
            logger.error(f"💥 Error getting user favorite characters: {str(e)}")
            return []

    def createScriptWithAssociations(self, scriptId: str, scriptData: Dict[str, Any], ownerUserId: str) -> bool:
        """Create a script and update user's generatedScripts array and characters' scripts arrays"""
        try:
            scriptData['createdBy'] = ownerUserId
            scriptData['createdAt'] = datetime.now().isoformat()
            scriptData['updatedAt'] = datetime.now().isoformat()
            
            batch = self.db.batch()
            
            # Save the script
            scriptRef = self.db.collection('scripts').document(scriptId)
            batch.set(scriptRef, scriptData)
            
            # Update user's generatedScripts array
            userRef = self.db.collection('users').document(ownerUserId)
            scriptInfo = {
                'id': scriptId,
                'originalPrompt': scriptData.get('originalPrompt', '')[:50] + ('...' if len(scriptData.get('originalPrompt', '')) > 50 else ''),
                'selectedCharacters': scriptData.get('selectedCharacters', []),
                'createdAt': scriptData['createdAt']
            }
            
            batch.update(userRef, {
                'generatedScripts': firestore.ArrayUnion([scriptInfo]),
                'updatedAt': datetime.now().isoformat()
            })
            
            # Update each character's scripts array
            selectedCharacters = scriptData.get('selectedCharacters', [])
            for characterId in selectedCharacters:
                characterRef = self.db.collection('user_profiles').document(characterId)
                characterDoc = characterRef.get()
                
                if characterDoc.exists:
                    scriptReference = {
                        'scriptId': scriptId,
                        'scriptPrompt': scriptData.get('originalPrompt', '')[:30] + ('...' if len(scriptData.get('originalPrompt', '')) > 30 else ''),
                        'createdBy': ownerUserId,
                        'createdAt': scriptData['createdAt']
                    }
                    
                    batch.update(characterRef, {
                        'scripts': firestore.ArrayUnion([scriptReference]),
                        'updatedAt': datetime.now().isoformat()
                    })
            
            batch.commit()
            
            logger.info(f"✅ Created script {scriptId} for user {ownerUserId} with {len(selectedCharacters)} character associations")
            return True
            
        except Exception as e:
            logger.error(f"💥 Error creating script with associations: {str(e)}")
            return False

    def deleteScriptWithAssociations(self, scriptId: str) -> bool:
        """Delete a script and clean up all associations"""
        try:
            # Get script data first
            scriptData = self.getScript(scriptId)
            if not scriptData:
                logger.warning(f"⚠️ Script {scriptId} not found")
                return False
            
            ownerUserId = scriptData.get('createdBy')
            selectedCharacters = scriptData.get('selectedCharacters', [])
            
            batch = self.db.batch()
            
            # Delete the script
            scriptRef = self.db.collection('scripts').document(scriptId)
            batch.delete(scriptRef)
            
            # Remove from user's generatedScripts array
            if ownerUserId:
                try:
                    userRef = self.db.collection('users').document(ownerUserId)
                    
                    scriptInfo = {
                        'id': scriptId,
                        'originalPrompt': scriptData.get('originalPrompt', '')[:50] + ('...' if len(scriptData.get('originalPrompt', '')) > 50 else ''),
                        'selectedCharacters': scriptData.get('selectedCharacters', []),
                        'createdAt': scriptData.get('createdAt', '')
                    }
                    
                    batch.update(userRef, {
                        'generatedScripts': firestore.ArrayRemove([scriptInfo]),
                        'updatedAt': datetime.now().isoformat()
                    })
                    
                except Exception as e:
                    logger.warning(f"⚠️ Could not clean up user's scripts: {str(e)}")
            
            # Remove from each character's scripts array
            for characterId in selectedCharacters:
                try:
                    characterRef = self.db.collection('user_profiles').document(characterId)
                    characterDoc = characterRef.get()
                    
                    if characterDoc.exists:
                        scriptReference = {
                            'scriptId': scriptId,
                            'scriptPrompt': scriptData.get('originalPrompt', '')[:30] + ('...' if len(scriptData.get('originalPrompt', '')) > 30 else ''),
                            'createdBy': ownerUserId,
                            'createdAt': scriptData.get('createdAt', '')
                        }
                        
                        batch.update(characterRef, {
                            'scripts': firestore.ArrayRemove([scriptReference]),
                            'updatedAt': datetime.now().isoformat()
                        })
                        
                except Exception as e:
                    logger.warning(f"⚠️ Could not clean up character {characterId} scripts: {str(e)}")
            
            batch.commit()
            
            logger.info(f"✅ Deleted script {scriptId} with {len(selectedCharacters)} character associations")
            return True
            
        except Exception as e:
            logger.error(f"💥 Error deleting script with associations: {str(e)}")
            return False

    def getUserScripts(self, userId: str) -> List[Dict[str, Any]]:
        """Get all scripts created by a specific user"""
        try:
            scriptsRef = self.db.collection('scripts')
            query = scriptsRef.where('createdBy', '==', userId)
            docs = query.stream()
            
            scripts = []
            for doc in docs:
                scriptData = doc.to_dict()
                scriptData['id'] = doc.id
                scripts.append(scriptData)
            
            logger.info(f"📄 Retrieved {len(scripts)} scripts for user {userId}")
            return scripts
            
        except Exception as e:
            logger.error(f"💥 Error getting user scripts: {str(e)}")
            return []

    def getCharacterScripts(self, characterId: str) -> List[Dict[str, Any]]:
        """Get all scripts that use a specific character"""
        try:
            scriptsRef = self.db.collection('scripts')
            query = scriptsRef.where('selectedCharacters', 'array_contains', characterId)
            docs = query.stream()
            
            scripts = []
            for doc in docs:
                scriptData = doc.to_dict()
                scriptData['id'] = doc.id
                scripts.append(scriptData)
            
            logger.info(f"📄 Retrieved {len(scripts)} scripts using character {characterId}")
            return scripts
            
        except Exception as e:
            logger.error(f"💥 Error getting character scripts: {str(e)}")
            return []

    def updateScriptWithCharacterAssociations(self, scriptId: str, newScriptData: Dict[str, Any]) -> bool:
        """Update a script and handle character association changes"""
        try:
            # Get current script data
            oldScriptData = self.getScript(scriptId)
            if not oldScriptData:
                logger.warning(f"⚠️ Script {scriptId} not found for update")
                return False
            
            oldCharacters = set(oldScriptData.get('selectedCharacters', []))
            newCharacters = set(newScriptData.get('selectedCharacters', []))
            ownerUserId = oldScriptData.get('createdBy')
            
            # Characters to remove from
            charactersToRemove = oldCharacters - newCharacters
            # Characters to add to
            charactersToAdd = newCharacters - oldCharacters
            
            batch = self.db.batch()
            
            # Update the script
            newScriptData['updatedAt'] = datetime.now().isoformat()
            scriptRef = self.db.collection('scripts').document(scriptId)
            batch.update(scriptRef, newScriptData)
            
            # Update user's generatedScripts array with new info
            if ownerUserId:
                try:
                    userRef = self.db.collection('users').document(ownerUserId)
                    
                    # Remove old script info
                    oldScriptInfo = {
                        'id': scriptId,
                        'originalPrompt': oldScriptData.get('originalPrompt', '')[:50] + ('...' if len(oldScriptData.get('originalPrompt', '')) > 50 else ''),
                        'selectedCharacters': oldScriptData.get('selectedCharacters', []),
                        'createdAt': oldScriptData.get('createdAt', '')
                    }
                    
                    # Add new script info
                    newScriptInfo = {
                        'id': scriptId,
                        'originalPrompt': newScriptData.get('originalPrompt', '')[:50] + ('...' if len(newScriptData.get('originalPrompt', '')) > 50 else ''),
                        'selectedCharacters': newScriptData.get('selectedCharacters', []),
                        'createdAt': oldScriptData.get('createdAt', '')
                    }
                    
                    batch.update(userRef, {
                        'generatedScripts': firestore.ArrayRemove([oldScriptInfo]),
                        'updatedAt': datetime.now().isoformat()
                    })
                    
                    batch.update(userRef, {
                        'generatedScripts': firestore.ArrayUnion([newScriptInfo]),
                        'updatedAt': datetime.now().isoformat()
                    })
                    
                except Exception as e:
                    logger.warning(f"⚠️ Could not update user's scripts: {str(e)}")
            
            # Remove script from old characters
            for characterId in charactersToRemove:
                try:
                    characterRef = self.db.collection('user_profiles').document(characterId)
                    characterDoc = characterRef.get()
                    
                    if characterDoc.exists:
                        oldScriptReference = {
                            'scriptId': scriptId,
                            'scriptPrompt': oldScriptData.get('originalPrompt', '')[:30] + ('...' if len(oldScriptData.get('originalPrompt', '')) > 30 else ''),
                            'createdBy': ownerUserId,
                            'createdAt': oldScriptData.get('createdAt', '')
                        }
                        
                        batch.update(characterRef, {
                            'scripts': firestore.ArrayRemove([oldScriptReference]),
                            'updatedAt': datetime.now().isoformat()
                        })
                        
                except Exception as e:
                    logger.warning(f"⚠️ Could not remove script from character {characterId}: {str(e)}")
            
            # Add script to new characters
            for characterId in charactersToAdd:
                try:
                    characterRef = self.db.collection('user_profiles').document(characterId)
                    characterDoc = characterRef.get()
                    
                    if characterDoc.exists:
                        newScriptReference = {
                            'scriptId': scriptId,
                            'scriptPrompt': newScriptData.get('originalPrompt', '')[:30] + ('...' if len(newScriptData.get('originalPrompt', '')) > 30 else ''),
                            'createdBy': ownerUserId,
                            'createdAt': oldScriptData.get('createdAt', '')
                        }
                        
                        batch.update(characterRef, {
                            'scripts': firestore.ArrayUnion([newScriptReference]),
                            'updatedAt': datetime.now().isoformat()
                        })
                        
                except Exception as e:
                    logger.warning(f"⚠️ Could not add script to character {characterId}: {str(e)}")
            
            batch.commit()
            
            logger.info(f"✅ Updated script {scriptId} - removed from {len(charactersToRemove)} characters, added to {len(charactersToAdd)} characters")
            return True
            
        except Exception as e:
            logger.error(f"💥 Error updating script with character associations: {str(e)}")
            return False

firebaseService = None

def getFirebaseService() -> FirebaseService:
    global firebaseService
    if firebaseService is None:
        firebaseService = FirebaseService()
    return firebaseService

def initializeFirebaseService(credentialsPath: str = "firebase.json") -> FirebaseService:
    global firebaseService
    firebaseService = FirebaseService(credentialsPath)
    return firebaseService