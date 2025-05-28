#!/usr/bin/env python3
"""
F5-TTS Selenium Client with camelCase naming conventions
Enhanced version with user profile support and improved functionality
"""

import time
import os
import requests
from datetime import datetime
from typing import Optional, Dict, Any
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

from .config import ConfigManager
from .utils import AudioFileManager, LogManager


class F5TtsSeleniumClient:
    """F5-TTS Selenium automation client with camelCase naming conventions"""
    
    def __init__(self, url: str = "http://localhost:7860"):
        """
        Initialize the Selenium client for F5-TTS
        
        Args:
            url: URL of the F5-TTS web interface
        """
        self.url = url
        self.driver = None
        self.wait = None
        self.configManager = ConfigManager()
        self.audioManager = AudioFileManager()
        self.logManager = LogManager()
        
    def setupDriver(self) -> bool:
        """Setup Chrome WebDriver with options"""
        print("🔧 Setting up Chrome WebDriver...")
        
        # Chrome options
        chromeOptions = Options()
        # Keep browser open (head mode, not headless)
        # chromeOptions.add_argument("--headless")  # Commented out for head mode
        chromeOptions.add_argument("--no-sandbox")
        chromeOptions.add_argument("--disable-dev-shm-usage")
        chromeOptions.add_argument("--disable-gpu")
        chromeOptions.add_argument("--window-size=1920,1080")
        
        # Try to create the driver
        try:
            # Try using ChromeDriver from PATH
            self.driver = webdriver.Chrome(options=chromeOptions)
            print("✅ Chrome WebDriver initialized successfully!")
        except Exception as e:
            print(f"❌ Failed to initialize Chrome WebDriver: {e}")
            print("💡 Make sure you have Chrome and ChromeDriver installed")
            print("💡 You can download ChromeDriver from: https://chromedriver.chromium.org/")
            self.logManager.logError(e, "ChromeDriver initialization")
            return False
        
        # Setup WebDriverWait
        self.wait = WebDriverWait(self.driver, 10)
        self.logManager.logInfo("Chrome WebDriver setup completed successfully")
        return True
    
    def openF5tts(self) -> bool:
        """Open the F5-TTS web interface"""
        if not self.driver:
            print("❌ Driver not initialized")
            return False
        
        try:
            print(f"🌐 Opening F5-TTS at {self.url}...")
            self.driver.get(self.url)
            
            # Wait for the page to load
            print("⏳ Waiting for page to load...")
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            
            # Check if the page loaded successfully
            if "F5 TTS" in self.driver.title or "Gradio" in self.driver.title:
                print("✅ F5-TTS page loaded successfully!")
                print(f"📄 Page title: {self.driver.title}")
                self.logManager.logInfo(f"F5-TTS page loaded: {self.driver.title}")
                return True
            else:
                print(f"⚠️  Page loaded but title unexpected: {self.driver.title}")
                self.logManager.logWarning(f"Unexpected page title: {self.driver.title}")
                return True  # Still return True as page loaded
                
        except Exception as e:
            print(f"❌ Failed to open F5-TTS: {e}")
            self.logManager.logError(e, "Opening F5-TTS page")
            return False
    
    def findElements(self):
        """Find and display key elements on the page"""
        if not self.driver:
            return
        
        try:
            print("\n🔍 Looking for key elements on the page...")
            
            # Look for common Gradio elements
            elementsToFind = [
                ("Audio upload", "input[type='file']"),
                ("Text areas", "textarea"),
                ("Text inputs", "input[type='text']"),
                ("Buttons", "button"),
                ("Tabs", "[role='tab']"),
                ("File upload areas", ".file-upload"),
                ("Gradio components", ".gradio-container"),
            ]
            
            for name, selector in elementsToFind:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        print(f"  ✅ Found {len(elements)} {name}")
                    else:
                        print(f"  ❌ No {name} found")
                except:
                    print(f"  ❌ Error finding {name}")
            
            # Try to find specific F5-TTS elements
            print("\n🎯 Looking for F5-TTS specific elements...")
            
            # Look for text that might indicate F5-TTS interface
            pageText = self.driver.page_source.lower()
            f5Indicators = [
                "f5-tts", "f5 tts", "basic-tts", "multi-speech", 
                "voice-chat", "reference audio", "synthesize"
            ]
            
            for indicator in f5Indicators:
                if indicator in pageText:
                    print(f"  ✅ Found '{indicator}' in page")
                else:
                    print(f"  ❌ '{indicator}' not found")
                    
        except Exception as e:
            print(f"❌ Error finding elements: {e}")
            self.logManager.logError(e, "Finding page elements")
    
    def uploadAudioFile(self, filePath: str) -> bool:
        """Upload audio file to the reference audio section"""
        try:
            print(f"📁 Uploading audio file: {filePath}")
            
            # Validate file first
            if not self.audioManager.validateAudioFile(filePath):
                return False
            
            # Convert to absolute path
            absolutePath = self.audioManager.getAbsolutePath(filePath)
            
            # Wait for the file input to be present
            fileInput = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file'][accept*='audio']"))
            )
            
            # Upload the file
            fileInput.send_keys(absolutePath)
            print("✅ Audio file uploaded successfully!")
            self.logManager.logInfo(f"Audio file uploaded: {filePath}")
            
            # Wait a moment for the file to process
            time.sleep(2)
            return True
            
        except Exception as e:
            print(f"❌ Failed to upload audio file: {e}")
            self.logManager.logError(e, f"Uploading audio file: {filePath}")
            return False
    
    def enterTextToGenerate(self, text: str) -> bool:
        """Enter text in the 'Text to Generate' textarea"""
        try:
            print(f"✏️ Entering text: {text[:50]}{'...' if len(text) > 50 else ''}")
            
            # Find the textarea for "Text to Generate"
            textarea = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "textarea[data-testid='textbox'][rows='10']"))
            )
            
            # Clear and enter the text
            textarea.clear()
            textarea.send_keys(text)
            print("✅ Text entered successfully!")
            self.logManager.logInfo(f"Text entered for generation: {len(text)} characters")
            return True
            
        except Exception as e:
            print(f"❌ Failed to enter text: {e}")
            self.logManager.logError(e, "Entering text to generate")
            return False
    
    def openAdvancedSettings(self) -> bool:
        """Open the Advanced Settings dropdown"""
        try:
            print("🔧 Opening Advanced Settings...")
            
            # Find and click the Advanced Settings button
            advancedButton = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button.label-wrap"))
            )
            
            advancedButton.click()
            print("✅ Advanced Settings opened!")
            self.logManager.logInfo("Advanced Settings opened")
            
            # Wait a moment for the dropdown to expand
            time.sleep(1)
            return True
            
        except Exception as e:
            print(f"❌ Failed to open Advanced Settings: {e}")
            self.logManager.logError(e, "Opening Advanced Settings")
            return False
    
    def configureAdvancedSettings(self, userConfig: Optional[Dict[str, Any]] = None) -> bool:
        """Configure the advanced settings with specific values"""
        try:
            print("⚙️ Configuring Advanced Settings...")
            
            # Use provided config or default values
            if userConfig is None:
                userConfig = {
                    "speed": 0.8,
                    "nfeSteps": 34,
                    "crossFadeDuration": 0.16,
                    "removeSilences": True
                }
            
            # Enable/Disable Remove Silences checkbox
            try:
                removeSilenceCheckbox = self.driver.find_element(
                    By.XPATH, "//span[text()='Remove Silences']/preceding-sibling::input[@type='checkbox']"
                )
                isSelected = removeSilenceCheckbox.is_selected()
                shouldBeSelected = userConfig.get("removeSilences", True)
                
                if isSelected != shouldBeSelected:
                    removeSilenceCheckbox.click()
                    print(f"✅ Remove Silences {'enabled' if shouldBeSelected else 'disabled'}")
            except Exception as e:
                print(f"⚠️ Could not configure Remove Silences: {e}")
            
            # Set Speed
            try:
                speedInput = self.driver.find_element(
                    By.XPATH, "//span[text()='Speed']/ancestor::div[@class='head svelte-10lj3xl']//input[@type='number']"
                )
                speedValue = str(userConfig.get("speed", 0.8))
                speedInput.clear()
                speedInput.send_keys(speedValue)
                print(f"✅ Speed set to {speedValue}")
            except Exception as e:
                print(f"⚠️ Could not set Speed: {e}")
            
            # Set NFE Steps
            try:
                nfeInput = self.driver.find_element(
                    By.XPATH, "//span[text()='NFE Steps']/ancestor::div[@class='head svelte-10lj3xl']//input[@type='number']"
                )
                nfeValue = str(userConfig.get("nfeSteps", 34))
                nfeInput.clear()
                nfeInput.send_keys(nfeValue)
                print(f"✅ NFE Steps set to {nfeValue}")
            except Exception as e:
                print(f"⚠️ Could not set NFE Steps: {e}")
            
            # Set Cross-Fade Duration
            try:
                crossfadeInput = self.driver.find_element(
                    By.XPATH, "//span[text()='Cross-Fade Duration (s)']/ancestor::div[@class='head svelte-10lj3xl']//input[@type='number']"
                )
                crossfadeValue = str(userConfig.get("crossFadeDuration", 0.16))
                crossfadeInput.clear()
                crossfadeInput.send_keys(crossfadeValue)
                print(f"✅ Cross-Fade Duration set to {crossfadeValue}")
            except Exception as e:
                print(f"⚠️ Could not set Cross-Fade Duration: {e}")
            
            print("✅ Advanced Settings configured!")
            self.logManager.logInfo(f"Advanced Settings configured: {userConfig}")
            time.sleep(1)
            return True
            
        except Exception as e:
            print(f"❌ Failed to configure Advanced Settings: {e}")
            self.logManager.logError(e, "Configuring Advanced Settings")
            return False
    
    def closeAdvancedSettings(self) -> bool:
        """Close the Advanced Settings dropdown"""
        try:
            print("📁 Closing Advanced Settings...")
            
            # Find and click the Advanced Settings button to close it
            advancedButton = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button.label-wrap"))
            )
            
            advancedButton.click()
            print("✅ Advanced Settings closed!")
            self.logManager.logInfo("Advanced Settings closed")
            
            # Wait a moment for the dropdown to collapse
            time.sleep(1)
            return True
            
        except Exception as e:
            print(f"❌ Failed to close Advanced Settings: {e}")
            self.logManager.logError(e, "Closing Advanced Settings")
            return False
    
    def clickSynthesize(self) -> bool:
        """Click the Synthesize button to generate audio"""
        try:
            print("🎵 Clicking Synthesize button...")
            
            # Find and click the Synthesize button
            synthesizeButton = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[text()='Synthesize']"))
            )
            
            synthesizeButton.click()
            print("✅ Synthesize button clicked! Audio generation started...")
            self.logManager.logInfo("Audio synthesis started")
            
            # Wait a moment for the process to start
            time.sleep(2)
            return True
            
        except Exception as e:
            print(f"❌ Failed to click Synthesize button: {e}")
            self.logManager.logError(e, "Clicking Synthesize button")
            return False
    
    def waitForAudioAndDownload(self, outputPrefix: str = "f5ttsGenerated", timeout: int = 300) -> bool:
        """Wait for audio generation to complete and download the file"""
        try:
            print("⏳ Waiting for audio generation to complete...")
            startTime = time.time()
            
            # Wait for the download link to appear (indicating audio is ready)
            downloadLink = None
            
            while time.time() - startTime < timeout:
                try:
                    # Look for the download link
                    downloadElement = self.driver.find_element(
                        By.CSS_SELECTOR, "a.download-link[download='audio.wav']"
                    )
                    downloadLink = downloadElement.get_attribute("href")
                    
                    if downloadLink and "gradio_api/file" in downloadLink:
                        print("✅ Audio generation completed!")
                        break
                        
                except:
                    pass
                
                print("⏳ Still generating... (waiting 5 seconds)")
                time.sleep(5)
            
            if not downloadLink:
                print("❌ Audio generation timed out or failed")
                self.logManager.logError("Audio generation timeout", "Download wait")
                return False
            
            # Download the audio file
            print(f"📥 Downloading audio from: {downloadLink}")
            
            # Generate filename with user prefix and timestamp
            fileName = self.audioManager.generateOutputFileName(outputPrefix)
            filePath = self.audioManager.getGeneratedFilePath(fileName)
            
            # Download the file
            response = requests.get(downloadLink)
            response.raise_for_status()
            
            with open(filePath, 'wb') as f:
                f.write(response.content)
            
            print(f"✅ Audio downloaded successfully!")
            print(f"📁 Saved as: {fileName}")
            print(f"📍 Location: {filePath}")
            
            # Get file size for confirmation
            fileSize = self.audioManager.getFileSize(filePath)
            if fileSize:
                sizeStr = self.audioManager.formatFileSize(fileSize)
                print(f"📊 File size: {sizeStr}")
            
            self.logManager.logInfo(f"Audio downloaded: {fileName} ({sizeStr if fileSize else 'unknown size'})")
            return True
            
        except Exception as e:
            print(f"❌ Failed to download audio: {e}")
            self.logManager.logError(e, "Downloading generated audio")
            return False
    
    def automateF5ttsWorkflowWithUser(self, userId: str, customText: Optional[str] = None) -> bool:
        """Complete automation workflow for F5-TTS with user profile"""
        print(f"\n🤖 Starting F5-TTS automation workflow for user: {userId}")
        
        # Get user profile and configuration
        userProfile = self.configManager.getUserProfile(userId)
        if not userProfile:
            print(f"❌ User profile not found: {userId}")
            return False
        
        userConfig = self.configManager.getUserConfig(userId)
        audioFilePath = self.configManager.getAudioFilePathWithFallback(userId)
        outputPrefix = self.configManager.getOutputPrefixWithFallback(userId)
        
        # Log user action
        self.logManager.logUserAction(userId, "AutomationStarted", f"Audio: {audioFilePath}")
        
        startTime = time.time()
        
        try:
            # Step 1: Upload audio file
            if not self.uploadAudioFile(audioFilePath):
                print("❌ Failed to upload audio file. Continuing anyway...")
            
            # Step 2: Enter text to generate
            if customText:
                textToGenerate = customText
            else:
                # Use default test text
                textToGenerate = "Hello, this is a test of the F5-TTS voice cloning system. The quick brown fox jumps over the lazy dog."
            
            if not self.enterTextToGenerate(textToGenerate):
                print("❌ Failed to enter text. Continuing anyway...")
            
            # Step 3: Open Advanced Settings
            if not self.openAdvancedSettings():
                print("❌ Failed to open Advanced Settings. Continuing anyway...")
            
            # Step 4: Configure Advanced Settings with user config
            if not self.configureAdvancedSettings(userConfig):
                print("❌ Failed to configure Advanced Settings. Continuing anyway...")
            
            # Step 5: Close Advanced Settings
            if not self.closeAdvancedSettings():
                print("❌ Failed to close Advanced Settings. Continuing anyway...")
            
            # Step 6: Click Synthesize button
            if not self.clickSynthesize():
                print("❌ Failed to click Synthesize button.")
                return False
            
            # Step 7: Wait for audio generation and download
            if not self.waitForAudioAndDownload(outputPrefix, userConfig.get("timeoutSeconds", 300)):
                print("❌ Failed to download generated audio. You can download manually from the browser.")
                return False
            
            # Calculate duration and log success
            duration = time.time() - startTime
            self.logManager.logAudioGeneration(
                userId, len(textToGenerate), audioFilePath, 
                f"{outputPrefix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav", duration
            )
            
            print("✅ Complete automation workflow finished!")
            self.logManager.logUserAction(userId, "AutomationCompleted", f"Duration: {duration:.2f}s")
            
            # Update last used user
            self.configManager.updateLastUsed(userId)
            
            return True
            
        except Exception as e:
            print(f"❌ Error during automation workflow: {e}")
            self.logManager.logError(e, f"Automation workflow for user {userId}")
            return False
    
    def automateF5ttsWorkflow(self) -> bool:
        """Legacy method - Complete automation workflow for F5-TTS with hardcoded values"""
        print("\n🤖 Starting F5-TTS automation workflow (legacy mode)...")
        
        # Step 1: Upload audio file
        audioFilePath = r"C:\Users\utsav\OneDrive\Desktop\F5-TTS\Palki.wav"
        if not self.uploadAudioFile(audioFilePath):
            print("❌ Failed to upload audio file. Continuing anyway...")
        
        # Step 2: Enter text to generate
        testText = "Rahul if memory management were that simple you would be Prime Minister by now \n\nSQL helps retrieve update and organize information efficiently it's like a librarian who actually knows where every book is"
        if not self.enterTextToGenerate(testText):
            print("❌ Failed to enter text. Continuing anyway...")
        
        # Step 3: Open Advanced Settings
        if not self.openAdvancedSettings():
            print("❌ Failed to open Advanced Settings. Continuing anyway...")
        
        # Step 4: Configure Advanced Settings
        if not self.configureAdvancedSettings():
            print("❌ Failed to configure Advanced Settings. Continuing anyway...")
        
        # Step 5: Close Advanced Settings
        if not self.closeAdvancedSettings():
            print("❌ Failed to close Advanced Settings. Continuing anyway...")
        
        # Step 6: Click Synthesize button
        if not self.clickSynthesize():
            print("❌ Failed to click Synthesize button. Continuing anyway...")
            return False
        
        # Step 7: Wait for audio generation and download
        if not self.waitForAudioAndDownload():
            print("❌ Failed to download generated audio. You can download manually from the browser.")
            return False
        
        print("✅ Complete automation workflow finished!")
        return True
    
    def keepOpen(self):
        """Keep the browser open for testing"""
        if not self.driver:
            return
        
        print("\n🔄 Browser is now open for testing!")
        print("📋 Complete automation finished! You can now:")
        print("  - Review the uploaded audio file")
        print("  - Check the entered text")
        print("  - Review configured Advanced Settings")
        print("  - Play the generated audio in browser")
        print("  - Check the downloaded audio file in generated directory")
        print("  - Run additional tests or generate more audio")
        print("  - Inspect elements for further automation")
        print("\n⌨️  Press Ctrl+C to close the browser and exit")
        
        try:
            # Keep the script running
            while True:
                time.sleep(1)
                
                # Check if browser is still open
                try:
                    self.driver.current_url
                except:
                    print("🔴 Browser was closed by user")
                    break
                    
        except KeyboardInterrupt:
            print("\n🛑 Received interrupt signal")
        except Exception as e:
            print(f"\n❌ Error: {e}")
            self.logManager.logError(e, "Browser keep-open session")
        finally:
            self.close()
    
    def close(self):
        """Close the browser"""
        if self.driver:
            print("🔴 Closing browser...")
            self.driver.quit()
            self.driver = None
            self.logManager.logInfo("Browser session closed")
            print("✅ Browser closed") 