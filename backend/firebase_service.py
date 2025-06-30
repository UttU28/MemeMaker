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
    """Firebase service for managing user profiles and scripts collections"""
    
    def __init__(self, credentials_path: str = "firebase.json"):
        self.credentials_path = credentials_path
        self.db = None
        self.app = None
        self.initialize_firebase()
    
    def initialize_firebase(self):
        """Initialize Firebase Admin SDK"""
        try:
            if not os.path.exists(self.credentials_path):
                raise FileNotFoundError(f"Firebase credentials file not found: {self.credentials_path}")
            
            # Check if Firebase is already initialized
            try:
                self.app = firebase_admin.get_app()
                logger.info("🔥 Firebase already initialized, using existing app")
            except ValueError:
                # Initialize Firebase if not already done
                cred = credentials.Certificate(self.credentials_path)
                self.app = firebase_admin.initialize_app(cred)
                logger.info("🔥 Firebase Admin SDK initialized successfully!")
            
            # Initialize Firestore client
            self.db = firestore.client()
            logger.info("📊 Firestore client initialized")
            
        except Exception as e:
            logger.error(f"💥 Firebase initialization failed: {str(e)}")
            raise
    
    def test_connection(self) -> bool:
        """Test Firebase connection"""
        try:
            # Try to write and read a test document
            test_ref = self.db.collection('test').document('connection_test')
            test_data = {
                'timestamp': datetime.now(),
                'status': 'connected'
            }
            
            test_ref.set(test_data)
            doc = test_ref.get()
            
            if doc.exists:
                test_ref.delete()  # Clean up
                logger.info("✅ Firebase connection test successful")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"💥 Firebase connection test failed: {str(e)}")
            return False
    
    # User Profiles (Characters) Operations
    
    def get_all_user_profiles(self) -> Dict[str, Any]:
        """Get all user profiles from Firebase"""
        try:
            profiles_ref = self.db.collection('user_profiles')
            docs = profiles_ref.stream()
            
            users = {}
            default_user = None
            
            for doc in docs:
                if doc.id == '_metadata':
                    # Handle metadata document
                    metadata = doc.to_dict()
                    default_user = metadata.get('defaultUser')
                else:
                    users[doc.id] = doc.to_dict()
            
            result = {
                "users": users,
                "defaultUser": default_user
            }
            
            logger.info(f"📄 Retrieved {len(users)} user profiles from Firebase")
            return result
            
        except Exception as e:
            logger.error(f"💥 Error getting user profiles: {str(e)}")
            # Return default structure on error
            return {"users": {}, "defaultUser": None}
    
    def save_user_profiles(self, profiles_data: Dict[str, Any]) -> bool:
        """Save user profiles to Firebase"""
        try:
            batch = self.db.batch()
            
            # Save metadata (defaultUser, etc.)
            metadata_ref = self.db.collection('user_profiles').document('_metadata')
            metadata = {
                'defaultUser': profiles_data.get('defaultUser'),
                'updatedAt': datetime.now()
            }
            batch.set(metadata_ref, metadata)
            
            # Save each user profile
            users = profiles_data.get('users', {})
            for user_id, user_data in users.items():
                user_ref = self.db.collection('user_profiles').document(user_id)
                # Ensure updatedAt is present
                if 'updatedAt' not in user_data:
                    user_data['updatedAt'] = datetime.now().isoformat()
                batch.set(user_ref, user_data)
            
            # Commit the batch
            batch.commit()
            logger.info(f"✅ Saved {len(users)} user profiles to Firebase")
            return True
            
        except Exception as e:
            logger.error(f"💥 Error saving user profiles: {str(e)}")
            return False
    
    def get_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific user profile"""
        try:
            user_ref = self.db.collection('user_profiles').document(user_id)
            doc = user_ref.get()
            
            if doc.exists:
                return doc.to_dict()
            
            return None
            
        except Exception as e:
            logger.error(f"💥 Error getting user profile {user_id}: {str(e)}")
            return None
    
    def save_user_profile(self, user_id: str, user_data: Dict[str, Any]) -> bool:
        """Save a specific user profile"""
        try:
            user_ref = self.db.collection('user_profiles').document(user_id)
            user_data['updatedAt'] = datetime.now().isoformat()
            user_ref.set(user_data)
            
            logger.info(f"✅ Saved user profile: {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"💥 Error saving user profile {user_id}: {str(e)}")
            return False
    
    def delete_user_profile(self, user_id: str) -> bool:
        """Delete a specific user profile"""
        try:
            user_ref = self.db.collection('user_profiles').document(user_id)
            user_ref.delete()
            
            logger.info(f"🗑️ Deleted user profile: {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"💥 Error deleting user profile {user_id}: {str(e)}")
            return False
    
    # Scripts Operations
    
    def get_all_scripts(self) -> Dict[str, Any]:
        """Get all scripts from Firebase"""
        try:
            scripts_ref = self.db.collection('scripts')
            docs = scripts_ref.stream()
            
            scripts = {}
            
            for doc in docs:
                if doc.id != '_metadata':  # Skip metadata document
                    scripts[doc.id] = doc.to_dict()
            
            result = {
                "scripts": scripts
            }
            
            logger.info(f"📝 Retrieved {len(scripts)} scripts from Firebase")
            return result
            
        except Exception as e:
            logger.error(f"💥 Error getting scripts: {str(e)}")
            # Return default structure on error
            return {"scripts": {}}
    
    def save_scripts(self, scripts_data: Dict[str, Any]) -> bool:
        """Save scripts to Firebase"""
        try:
            batch = self.db.batch()
            
            # Save metadata if needed
            metadata_ref = self.db.collection('scripts').document('_metadata')
            metadata = {
                'updatedAt': datetime.now()
            }
            batch.set(metadata_ref, metadata)
            
            # Save each script
            scripts = scripts_data.get('scripts', {})
            for script_id, script_data in scripts.items():
                script_ref = self.db.collection('scripts').document(script_id)
                # Ensure updatedAt is present
                if 'updatedAt' not in script_data:
                    script_data['updatedAt'] = datetime.now().isoformat()
                batch.set(script_ref, script_data)
            
            # Commit the batch
            batch.commit()
            logger.info(f"✅ Saved {len(scripts)} scripts to Firebase")
            return True
            
        except Exception as e:
            logger.error(f"💥 Error saving scripts: {str(e)}")
            return False
    
    def get_script(self, script_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific script"""
        try:
            script_ref = self.db.collection('scripts').document(script_id)
            doc = script_ref.get()
            
            if doc.exists:
                return doc.to_dict()
            
            return None
            
        except Exception as e:
            logger.error(f"💥 Error getting script {script_id}: {str(e)}")
            return None
    
    def save_script(self, script_id: str, script_data: Dict[str, Any]) -> bool:
        """Save a specific script"""
        try:
            script_ref = self.db.collection('scripts').document(script_id)
            script_data['updatedAt'] = datetime.now().isoformat()
            script_ref.set(script_data)
            
            logger.info(f"✅ Saved script: {script_id}")
            return True
            
        except Exception as e:
            logger.error(f"💥 Error saving script {script_id}: {str(e)}")
            return False
    
    def delete_script(self, script_id: str) -> bool:
        """Delete a specific script"""
        try:
            script_ref = self.db.collection('scripts').document(script_id)
            script_ref.delete()
            
            logger.info(f"🗑️ Deleted script: {script_id}")
            return True
            
        except Exception as e:
            logger.error(f"💥 Error deleting script {script_id}: {str(e)}")
            return False
    
    # Authentication & User Management Operations
    
    def create_user(self, email: str, password: str, name: str) -> tuple[bool, str, Optional[str]]:
        """Create a new user with Firebase Auth REST API and save to users collection"""
        try:
            # Get Firebase API Key from environment variables
            api_key = os.getenv('FIREBASE_API_KEY')
            if not api_key:
                logger.error("🔑 Firebase API Key not found in environment. Please set FIREBASE_API_KEY in .env file")
                return False, "Authentication configuration error", None
            
            # Use Firebase Auth REST API to create user
            url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={api_key}"
            
            payload = {
                "email": email,
                "password": password,
                "returnSecureToken": True
            }
            
            response = requests.post(url, json=payload)
            
            if response.status_code == 200:
                result = response.json()
                user_id = result.get('localId')
                
                # Update display name using Admin SDK
                try:
                    auth.update_user(user_id, display_name=name)
                except Exception as e:
                    logger.warning(f"⚠️ Could not update display name: {str(e)}")
                
                # Create user document in Firestore
                current_time = datetime.now().isoformat()
                user_data = {
                    'name': name,
                    'email': email,
                    'isVerified': False,
                    'subscription': 'free',
                    'generatedCharacters': [],  # Initialize empty array for character tracking
                    'createdAt': current_time,
                    'updatedAt': current_time
                }
                
                user_ref = self.db.collection('users').document(user_id)
                user_ref.set(user_data)
                
                logger.info(f"✅ Created user: {email} with ID: {user_id}")
                return True, "User created successfully", user_id
                
            else:
                error_data = response.json()
                error_message = error_data.get('error', {}).get('message', 'User creation failed')
                
                if 'EMAIL_EXISTS' in error_message:
                    logger.warning(f"⚠️ User creation failed: Email already exists - {email}")
                    return False, "Email already exists", None
                elif 'WEAK_PASSWORD' in error_message:
                    logger.warning(f"⚠️ User creation failed: Weak password - {email}")
                    return False, "Password should be at least 6 characters", None
                elif 'INVALID_EMAIL' in error_message:
                    logger.warning(f"⚠️ User creation failed: Invalid email - {email}")
                    return False, "Invalid email format", None
                else:
                    logger.warning(f"⚠️ User creation failed for {email}: {error_message}")
                    return False, f"User creation failed: {error_message}", None
            
        except requests.exceptions.RequestException as e:
            logger.error(f"💥 Network error during user creation: {str(e)}")
            return False, "User creation service unavailable", None
        except Exception as e:
            logger.error(f"💥 Error creating user {email}: {str(e)}")
            return False, f"User creation failed: {str(e)}", None
    
    def verify_user_password(self, email: str, password: str) -> tuple[bool, str, Optional[str]]:
        """Verify user credentials using Firebase Auth REST API"""
        try:
            # Get Firebase API Key from environment variables
            api_key = os.getenv('FIREBASE_API_KEY')
            if not api_key:
                logger.error("🔑 Firebase API Key not found in environment. Please set FIREBASE_API_KEY in .env file")
                return False, "Authentication configuration error", None
            
            # Use Firebase Auth REST API to verify credentials
            url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}"
            
            payload = {
                "email": email,
                "password": password,
                "returnSecureToken": True
            }
            
            response = requests.post(url, json=payload)
            
            if response.status_code == 200:
                result = response.json()
                user_id = result.get('localId')
                logger.info(f"✅ User authenticated: {email} with ID: {user_id}")
                return True, "User authenticated", user_id
            else:
                error_data = response.json()
                error_message = error_data.get('error', {}).get('message', 'Authentication failed')
                
                if 'EMAIL_NOT_FOUND' in error_message:
                    logger.warning(f"⚠️ User not found: {email}")
                    return False, "Invalid email or password", None
                elif 'INVALID_PASSWORD' in error_message:
                    logger.warning(f"⚠️ Invalid password for user: {email}")
                    return False, "Invalid email or password", None
                else:
                    logger.warning(f"⚠️ Authentication failed for {email}: {error_message}")
                    return False, "Invalid email or password", None
            
        except requests.exceptions.RequestException as e:
            logger.error(f"💥 Network error during authentication: {str(e)}")
            return False, "Authentication service unavailable", None
        except Exception as e:
            logger.error(f"💥 Error verifying user {email}: {str(e)}")
            return False, f"Authentication failed: {str(e)}", None
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user data from users collection"""
        try:
            user_ref = self.db.collection('users').document(user_id)
            doc = user_ref.get()
            
            if doc.exists:
                user_data = doc.to_dict()
                user_data['id'] = user_id  # Add ID to the data
                return user_data
            
            return None
            
        except Exception as e:
            logger.error(f"💥 Error getting user {user_id}: {str(e)}")
            return None
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user data by email"""
        try:
            # First get user from Firebase Auth
            user_record = auth.get_user_by_email(email)
            user_id = user_record.uid
            
            # Then get user data from Firestore
            return self.get_user_by_id(user_id)
            
        except auth.UserNotFoundError:
            logger.warning(f"⚠️ User not found: {email}")
            return None
        except Exception as e:
            logger.error(f"💥 Error getting user by email {email}: {str(e)}")
            return None
    
    def update_user(self, user_id: str, user_data: Dict[str, Any]) -> bool:
        """Update user data in users collection"""
        try:
            user_ref = self.db.collection('users').document(user_id)
            user_data['updatedAt'] = datetime.now().isoformat()
            user_ref.update(user_data)
            
            logger.info(f"✅ Updated user: {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"💥 Error updating user {user_id}: {str(e)}")
            return False
    
    def delete_user(self, user_id: str) -> bool:
        """Delete user from both Firebase Auth and users collection"""
        try:
            # Delete from Firebase Auth
            auth.delete_user(user_id)
            
            # Delete from Firestore
            user_ref = self.db.collection('users').document(user_id)
            user_ref.delete()
            
            logger.info(f"🗑️ Deleted user: {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"💥 Error deleting user {user_id}: {str(e)}")
            return False
    
    # Character-User Relationship Management
    
    def create_character_with_owner(self, character_id: str, character_data: Dict[str, Any], owner_user_id: str) -> bool:
        """Create a character with ownership tracking"""
        try:
            # Add createdBy field to character data
            character_data['createdBy'] = owner_user_id
            character_data['createdAt'] = datetime.now().isoformat()
            character_data['updatedAt'] = datetime.now().isoformat()
            
            # Start a batch operation
            batch = self.db.batch()
            
            # Save character with createdBy field
            character_ref = self.db.collection('user_profiles').document(character_id)
            batch.set(character_ref, character_data)
            
            # Update user's generatedCharacters array
            user_ref = self.db.collection('users').document(owner_user_id)
            character_info = {
                'id': character_id,
                'displayName': character_data.get('displayName', character_id),
                'createdAt': character_data['createdAt']
            }
            
            # Use array union to add the character info to the user's generatedCharacters
            batch.update(user_ref, {
                'generatedCharacters': firestore.ArrayUnion([character_info]),
                'updatedAt': datetime.now().isoformat()
            })
            
            # Commit the batch
            batch.commit()
            
            logger.info(f"✅ Created character {character_id} for user {owner_user_id}")
            return True
            
        except Exception as e:
            logger.error(f"💥 Error creating character with owner: {str(e)}")
            return False
    
    def delete_character_with_owner_cleanup(self, character_id: str) -> bool:
        """Delete a character and clean up user's generatedCharacters array"""
        try:
            # First get the character to find out who created it
            character_data = self.get_user_profile(character_id)
            if not character_data:
                logger.warning(f"⚠️ Character {character_id} not found for deletion")
                return False
            
            owner_user_id = character_data.get('createdBy')
            
            # Start a batch operation
            batch = self.db.batch()
            
            # Delete the character
            character_ref = self.db.collection('user_profiles').document(character_id)
            batch.delete(character_ref)
            
            # Clean up user's generatedCharacters array if owner exists
            if owner_user_id:
                try:
                    user_ref = self.db.collection('users').document(owner_user_id)
                    
                    # Find and remove the character from the array
                    character_info = {
                        'id': character_id,
                        'displayName': character_data.get('displayName', character_id),
                        'createdAt': character_data.get('createdAt', '')
                    }
                    
                    batch.update(user_ref, {
                        'generatedCharacters': firestore.ArrayRemove([character_info]),
                        'updatedAt': datetime.now().isoformat()
                    })
                    
                    logger.info(f"🧹 Will clean up character {character_id} from user {owner_user_id}'s generatedCharacters")
                    
                except Exception as e:
                    logger.warning(f"⚠️ Could not clean up user's generatedCharacters: {str(e)}")
            
            # Commit the batch
            batch.commit()
            
            logger.info(f"✅ Deleted character {character_id} with owner cleanup")
            return True
            
        except Exception as e:
            logger.error(f"💥 Error deleting character with owner cleanup: {str(e)}")
            return False
    
    def get_user_characters(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all characters created by a specific user"""
        try:
            characters_ref = self.db.collection('user_profiles')
            query = characters_ref.where('createdBy', '==', user_id)
            docs = query.stream()
            
            characters = []
            for doc in docs:
                character_data = doc.to_dict()
                character_data['id'] = doc.id
                characters.append(character_data)
            
            logger.info(f"📄 Retrieved {len(characters)} characters for user {user_id}")
            return characters
            
        except Exception as e:
            logger.error(f"💥 Error getting user characters: {str(e)}")
            return []
    
    def update_character_with_owner_check(self, character_id: str, character_data: Dict[str, Any], requesting_user_id: str) -> bool:
        """Update a character but only if the requesting user is the owner"""
        try:
            # First check if the user owns this character
            existing_character = self.get_user_profile(character_id)
            if not existing_character:
                logger.warning(f"⚠️ Character {character_id} not found")
                return False
            
            character_owner = existing_character.get('createdBy')
            if character_owner != requesting_user_id:
                logger.warning(f"⚠️ User {requesting_user_id} attempted to update character {character_id} owned by {character_owner}")
                return False
            
            # Update the character
            character_data['updatedAt'] = datetime.now().isoformat()
            character_ref = self.db.collection('user_profiles').document(character_id)
            character_ref.update(character_data)
            
            # If display name was updated, also update the user's generatedCharacters array
            if 'displayName' in character_data and character_owner:
                try:
                    user_ref = self.db.collection('users').document(character_owner)
                    user_doc = user_ref.get()
                    
                    if user_doc.exists:
                        user_data = user_doc.to_dict()
                        generated_characters = user_data.get('generatedCharacters', [])
                        
                        # Update the character info in the array
                        for i, char_info in enumerate(generated_characters):
                            if char_info.get('id') == character_id:
                                generated_characters[i]['displayName'] = character_data['displayName']
                                break
                        
                        user_ref.update({
                            'generatedCharacters': generated_characters,
                            'updatedAt': datetime.now().isoformat()
                        })
                        
                        logger.info(f"🔄 Updated character info in user's generatedCharacters array")
                    
                except Exception as e:
                    logger.warning(f"⚠️ Could not update user's generatedCharacters array: {str(e)}")
            
            logger.info(f"✅ Updated character {character_id} for user {requesting_user_id}")
            return True
            
        except Exception as e:
            logger.error(f"💥 Error updating character with owner check: {str(e)}")
            return False

# Global Firebase service instance
firebase_service = None

def get_firebase_service() -> FirebaseService:
    """Get the global Firebase service instance"""
    global firebase_service
    if firebase_service is None:
        firebase_service = FirebaseService()
    return firebase_service

def initialize_firebase_service(credentials_path: str = "firebase.json") -> FirebaseService:
    """Initialize and return Firebase service"""
    global firebase_service
    firebase_service = FirebaseService(credentials_path)
    return firebase_service 