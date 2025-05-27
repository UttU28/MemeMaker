#!/usr/bin/env python3
"""
Basic Usage Example for F5-TTS Selenium Automation
Demonstrates how to use the F5-TTS automation with user profiles
"""

import time
from src.client import F5TtsSeleniumClient
from src.config import ConfigManager
from src.utils import AudioFileManager, LogManager


def basicUsageExample():
    """Basic usage example with default user"""
    print("🚀 F5-TTS Basic Usage Example")
    print("=" * 50)
    
    # Initialize managers
    configManager = ConfigManager()
    audioManager = AudioFileManager()
    logManager = LogManager()
    
    # Get default user
    defaultUserId = configManager.getDefaultUserId()
    print(f"📋 Using default user: {defaultUserId}")
    
    # Validate user profile
    if not configManager.validateUserProfile(defaultUserId):
        print(f"❌ Invalid user profile: {defaultUserId}")
        return
    
    # Get user configuration
    userConfig = configManager.getUserConfig(defaultUserId)
    audioFilePath = configManager.getAudioFilePath(defaultUserId)
    
    # Validate audio file
    if not audioManager.validateAudioFile(audioFilePath):
        print(f"❌ Invalid audio file: {audioFilePath}")
        return
    
    # Create client with user configuration
    client = F5TtsSeleniumClient(userConfig.get("f5ttsUrl", "http://localhost:7860"))
    
    try:
        # Setup and run automation
        if not client.setupDriver():
            return
        
        if not client.openF5tts():
            return
        
        # Run automation with user profile
        success = client.automateF5ttsWorkflowWithUser(defaultUserId)
        
        if success:
            print("✅ Basic automation completed successfully!")
            logManager.logUserAction(defaultUserId, "BasicAutomation", "Completed successfully")
        else:
            print("❌ Basic automation failed")
            logManager.logUserAction(defaultUserId, "BasicAutomation", "Failed")
        
        # Keep browser open for testing
        client.keepOpen()
        
    except Exception as e:
        print(f"❌ Error during automation: {e}")
        logManager.logError(e, "Basic automation")
    finally:
        client.close()


def multiUserExample():
    """Example showing how to use multiple user profiles"""
    print("\n🔄 Multi-User Example")
    print("=" * 30)
    
    configManager = ConfigManager()
    audioManager = AudioFileManager()
    logManager = LogManager()
    
    # Get all available users
    allUserIds = configManager.getAllUserIds()
    print(f"👥 Available users: {', '.join(allUserIds)}")
    
    # Let user choose
    print("\nSelect a user profile:")
    for i, userId in enumerate(allUserIds, 1):
        userProfile = configManager.getUserProfile(userId)
        displayName = userProfile.get("displayName", userId)
        description = userProfile.get("description", "No description")
        print(f"  {i}. {displayName} ({userId}) - {description}")
    
    try:
        choice = int(input("\nEnter your choice (1-5): ")) - 1
        if 0 <= choice < len(allUserIds):
            selectedUserId = allUserIds[choice]
            print(f"✅ Selected: {selectedUserId}")
            
            # Update last used
            configManager.updateLastUsed(selectedUserId)
            
            # Run automation with selected user
            runAutomationWithUser(selectedUserId)
        else:
            print("❌ Invalid choice")
    except ValueError:
        print("❌ Invalid input")
    except KeyboardInterrupt:
        print("\n🛑 Cancelled by user")


def runAutomationWithUser(userId: str):
    """Run automation with specific user profile"""
    configManager = ConfigManager()
    audioManager = AudioFileManager()
    logManager = LogManager()
    
    print(f"\n🎯 Running automation for user: {userId}")
    
    # Get user configuration
    userConfig = configManager.getUserConfig(userId)
    audioFilePath = configManager.getAudioFilePath(userId)
    userProfile = configManager.getUserProfile(userId)
    
    print(f"📁 Audio file: {audioFilePath}")
    print(f"⚙️ Speed: {userConfig.get('speed')}")
    print(f"⚙️ NFE Steps: {userConfig.get('nfeSteps')}")
    print(f"⚙️ Cross-fade: {userConfig.get('crossFadeDuration')}")
    print(f"⚙️ Remove silences: {userConfig.get('removeSilences')}")
    
    # Validate audio file
    if not audioManager.validateAudioFile(audioFilePath):
        return
    
    # Create client
    client = F5TtsSeleniumClient(userConfig.get("f5ttsUrl"))
    
    try:
        # Setup and run
        if client.setupDriver() and client.openF5tts():
            success = client.automateF5ttsWorkflowWithUser(userId)
            
            if success:
                print(f"✅ Automation completed for {userId}")
                logManager.logUserAction(userId, "UserAutomation", "Completed")
            else:
                print(f"❌ Automation failed for {userId}")
                logManager.logUserAction(userId, "UserAutomation", "Failed")
            
            # Show generated files for this user
            outputPrefix = configManager.getOutputPrefix(userId)
            generatedFiles = audioManager.listGeneratedFiles(outputPrefix)
            
            if generatedFiles:
                print(f"\n📁 Generated files for {userId}:")
                for fileName in generatedFiles[:5]:  # Show last 5
                    filePath = audioManager.getGeneratedFilePath(fileName)
                    fileSize = audioManager.getFileSize(filePath)
                    if fileSize:
                        sizeStr = audioManager.formatFileSize(fileSize)
                        print(f"  • {fileName} ({sizeStr})")
            
            client.keepOpen()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        logManager.logError(e, f"User automation for {userId}")
    finally:
        client.close()


def listUserProfiles():
    """List all available user profiles"""
    print("\n👥 Available User Profiles")
    print("=" * 30)
    
    configManager = ConfigManager()
    allUserIds = configManager.getAllUserIds()
    
    for userId in allUserIds:
        userProfile = configManager.getUserProfile(userId)
        if userProfile:
            print(f"\n🔹 {userId.upper()}")
            print(f"   Name: {userProfile.get('displayName', 'N/A')}")
            print(f"   Audio: {userProfile.get('audioFile', 'N/A')}")
            print(f"   Description: {userProfile.get('description', 'N/A')}")
            
            config = userProfile.get('config', {})
            print(f"   Settings: Speed={config.get('speed')}, NFE={config.get('nfeSteps')}")


def showGeneratedFiles():
    """Show all generated audio files"""
    print("\n📁 Generated Audio Files")
    print("=" * 30)
    
    audioManager = AudioFileManager()
    allFiles = audioManager.listGeneratedFiles()
    
    if not allFiles:
        print("No generated files found.")
        return
    
    print(f"Found {len(allFiles)} generated files:")
    
    for fileName in allFiles:
        filePath = audioManager.getGeneratedFilePath(fileName)
        fileSize = audioManager.getFileSize(filePath)
        
        if fileSize:
            sizeStr = audioManager.formatFileSize(fileSize)
            print(f"  • {fileName} ({sizeStr})")
        else:
            print(f"  • {fileName}")


def main():
    """Main function with menu"""
    while True:
        print("\n🎵 F5-TTS Automation Menu")
        print("=" * 30)
        print("1. Basic Usage (Default User)")
        print("2. Multi-User Selection")
        print("3. List User Profiles")
        print("4. Show Generated Files")
        print("5. Exit")
        
        try:
            choice = input("\nEnter your choice (1-5): ").strip()
            
            if choice == "1":
                basicUsageExample()
            elif choice == "2":
                multiUserExample()
            elif choice == "3":
                listUserProfiles()
            elif choice == "4":
                showGeneratedFiles()
            elif choice == "5":
                print("👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice. Please enter 1-5.")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")


if __name__ == "__main__":
    main() 