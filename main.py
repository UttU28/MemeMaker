#!/usr/bin/env python3
"""
F5-TTS Gradio API Automation - Main Script
Enhanced version with user profile support and menu system
"""

from src.client import F5TtsGradioClient
from src.config import ConfigManager
from src.utils import AudioFileManager, LogManager


def basicUsageExample(sampleText: str):
    """Basic usage example with default user"""
    print("🚀 F5-TTS Basic Usage")
    print("=" * 30)
    
    configManager = ConfigManager()
    audioManager = AudioFileManager()
    logManager = LogManager()
    
    defaultUserId = configManager.getDefaultUserId()
    print(f"Using user: {defaultUserId}")
    
    if not configManager.validateUserProfile(defaultUserId):
        print(f"❌ Invalid user profile: {defaultUserId}")
        return
    
    userConfig = configManager.getUserConfig(defaultUserId)
    audioFilePath = configManager.getAudioFilePathWithFallback(defaultUserId)
    
    if not audioManager.validateAudioFile(audioFilePath):
        print(f"❌ Invalid audio file: {audioFilePath}")
        return
    
    client = F5TtsGradioClient(userConfig.get("f5ttsUrl", "http://localhost:7860"))
    
    try:
        if not client.connectToGradio():
            return
        
        success = client.generateSpeechWithUser(defaultUserId, sampleText)
        
        if success:
            print("✅ Speech generation completed!")
            logManager.logUserAction(defaultUserId, "BasicGeneration", "Completed")
        else:
            print("❌ Speech generation failed")
            logManager.logUserAction(defaultUserId, "BasicGeneration", "Failed")
                    
    except Exception as e:
        print(f"❌ Error: {e}")
        logManager.logError(e, "Basic speech generation")
    finally:
        client.close()


def multiUserExample():
    """Multi-user selection example"""
    print("\n🔄 Multi-User Selection")
    print("=" * 25)
    
    configManager = ConfigManager()
    allUserIds = configManager.getAllUserIds()
    
    print("Available users:")
    for i, userId in enumerate(allUserIds, 1):
        userProfile = configManager.getUserProfile(userId)
        displayName = userProfile.get("displayName", userId)
        print(f"  {i}. {displayName} ({userId})")
    
    try:
        choice = int(input("\nEnter choice (1-5): ")) - 1
        if 0 <= choice < len(allUserIds):
            selectedUserId = allUserIds[choice]
            configManager.updateLastUsed(selectedUserId)
            runAutomationWithUser(selectedUserId)
        else:
            print("❌ Invalid choice")
    except (ValueError, KeyboardInterrupt):
        print("❌ Invalid input or cancelled")


def runAutomationWithUser(userId: str):
    """Run automation with specific user"""
    configManager = ConfigManager()
    audioManager = AudioFileManager()
    logManager = LogManager()
    
    print(f"\n🎯 Generating for: {userId}")
    
    userConfig = configManager.getUserConfig(userId)
    audioFilePath = configManager.getAudioFilePathWithFallback(userId)
    
    if not audioManager.validateAudioFile(audioFilePath):
        return
    
    client = F5TtsGradioClient(userConfig.get("f5ttsUrl"))
    
    try:
        if client.connectToGradio():
            success = client.generateSpeechWithUser(userId)
            
            if success:
                print(f"✅ Completed for {userId}")
                logManager.logUserAction(userId, "UserGeneration", "Completed")
                
                # Show recent files
                outputPrefix = configManager.getOutputPrefixWithFallback(userId)
                generatedFiles = audioManager.listGeneratedFiles(outputPrefix)
                
                if generatedFiles:
                    print(f"Recent files: {len(generatedFiles[:3])}")
                    for fileName in generatedFiles[:3]:
                        filePath = audioManager.getGeneratedFilePath(fileName)
                        fileSize = audioManager.getFileSize(filePath)
                        if fileSize:
                            sizeStr = audioManager.formatFileSize(fileSize)
                            print(f"  • {fileName} ({sizeStr})")
            else:
                print(f"❌ Failed for {userId}")
                logManager.logUserAction(userId, "UserGeneration", "Failed")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        logManager.logError(e, f"User generation for {userId}")
    finally:
        client.close()


def listUserProfiles():
    """List all user profiles"""
    print("\n👥 User Profiles")
    print("=" * 20)
    
    configManager = ConfigManager()
    
    for userId in configManager.getAllUserIds():
        userProfile = configManager.getUserProfile(userId)
        if userProfile:
            displayName = userProfile.get('displayName', 'N/A')
            config = userProfile.get('config', {})
            speed = config.get('speed', 'N/A')
            nfe = config.get('nfeSteps', 'N/A')
            print(f"🔹 {userId}: {displayName} (Speed: {speed}, NFE: {nfe})")


def showGeneratedFiles():
    """Show generated files"""
    print("\n📁 Generated Files")
    print("=" * 20)
    
    audioManager = AudioFileManager()
    allFiles = audioManager.listGeneratedFiles()
    
    if not allFiles:
        print("No files found.")
        return
        
    print(f"Total files: {len(allFiles)}")
    
    for fileName in allFiles[:10]:  # Show last 10
        filePath = audioManager.getGeneratedFilePath(fileName)
        fileSize = audioManager.getFileSize(filePath)
        
        if fileSize:
            sizeStr = audioManager.formatFileSize(fileSize)
            print(f"  • {fileName} ({sizeStr})")


def main():
    """Main menu"""
    sampleText = "Rahul if memory management were that simple you would be Prime Minister by now. SQL helps retrieve update and organize information efficiently it's like a librarian who actually knows where every book is"
    
    while True:
        print("\n🎵 F5-TTS Menu")
        print("=" * 15)
        print("1. Basic Usage")
        print("2. Multi-User")
        print("3. List Profiles")
        print("4. Show Files")
        print("5. Exit")
        
        try:
            choice = input("\nChoice (1-5): ").strip()
            
            if choice == "1":
                basicUsageExample(sampleText)
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
                print("❌ Invalid choice (1-5)")
                    
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")


if __name__ == "__main__":
    main() 