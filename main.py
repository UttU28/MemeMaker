#!/usr/bin/env python3
"""
F5-TTS Selenium Automation Script
Opens the F5-TTS web interface and keeps it open for testing
"""

import time
import os
import requests
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

class F5TTSSeleniumClient:
    def __init__(self, url="http://localhost:7860"):
        """
        Initialize the Selenium client for F5-TTS
        
        Args:
            url: URL of the F5-TTS web interface
        """
        self.url = url
        self.driver = None
        self.wait = None
        
    def setup_driver(self):
        """Setup Chrome WebDriver with options"""
        print("🔧 Setting up Chrome WebDriver...")
        
        # Chrome options
        chrome_options = Options()
        # Keep browser open (head mode, not headless)
        # chrome_options.add_argument("--headless")  # Commented out for head mode
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        
        # Try to create the driver
        try:
            # Try using ChromeDriver from PATH
            self.driver = webdriver.Chrome(options=chrome_options)
            print("✅ Chrome WebDriver initialized successfully!")
        except Exception as e:
            print(f"❌ Failed to initialize Chrome WebDriver: {e}")
            print("💡 Make sure you have Chrome and ChromeDriver installed")
            print("💡 You can download ChromeDriver from: https://chromedriver.chromium.org/")
            return False
        
        # Setup WebDriverWait
        self.wait = WebDriverWait(self.driver, 10)
        return True
    
    def open_f5tts(self):
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
                return True
            else:
                print(f"⚠️  Page loaded but title unexpected: {self.driver.title}")
                return True  # Still return True as page loaded
                
        except Exception as e:
            print(f"❌ Failed to open F5-TTS: {e}")
            return False
    
    def find_elements(self):
        """Find and display key elements on the page"""
        if not self.driver:
            return
        
        try:
            print("\n🔍 Looking for key elements on the page...")
            
            # Look for common Gradio elements
            elements_to_find = [
                ("Audio upload", "input[type='file']"),
                ("Text areas", "textarea"),
                ("Text inputs", "input[type='text']"),
                ("Buttons", "button"),
                ("Tabs", "[role='tab']"),
                ("File upload areas", ".file-upload"),
                ("Gradio components", ".gradio-container"),
            ]
            
            for name, selector in elements_to_find:
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
            page_text = self.driver.page_source.lower()
            f5_indicators = [
                "f5-tts", "f5 tts", "basic-tts", "multi-speech", 
                "voice-chat", "reference audio", "synthesize"
            ]
            
            for indicator in f5_indicators:
                if indicator in page_text:
                    print(f"  ✅ Found '{indicator}' in page")
                else:
                    print(f"  ❌ '{indicator}' not found")
                    
        except Exception as e:
            print(f"❌ Error finding elements: {e}")
    
    def upload_audio_file(self, file_path):
        """Upload audio file to the reference audio section"""
        try:
            print(f"📁 Uploading audio file: {file_path}")
            
            # Wait for the file input to be present
            file_input = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file'][accept*='audio']"))
            )
            
            # Upload the file
            file_input.send_keys(file_path)
            print("✅ Audio file uploaded successfully!")
            
            # Wait a moment for the file to process
            time.sleep(2)
            return True
            
        except Exception as e:
            print(f"❌ Failed to upload audio file: {e}")
            return False
    
    def enter_text_to_generate(self, text):
        """Enter text in the 'Text to Generate' textarea"""
        try:
            print(f"✏️ Entering text: {text}")
            
            # Find the textarea for "Text to Generate"
            textarea = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "textarea[data-testid='textbox'][rows='10']"))
            )
            
            # Clear and enter the text
            textarea.clear()
            textarea.send_keys(text)
            print("✅ Text entered successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Failed to enter text: {e}")
            return False
    
    def open_advanced_settings(self):
        """Open the Advanced Settings dropdown"""
        try:
            print("🔧 Opening Advanced Settings...")
            
            # Find and click the Advanced Settings button
            advanced_button = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button.label-wrap"))
            )
            
            advanced_button.click()
            print("✅ Advanced Settings opened!")
            
            # Wait a moment for the dropdown to expand
            time.sleep(1)
            return True
            
        except Exception as e:
            print(f"❌ Failed to open Advanced Settings: {e}")
            return False
    
    def configure_advanced_settings(self):
        """Configure the advanced settings with specific values"""
        try:
            print("⚙️ Configuring Advanced Settings...")
            
            # Enable Remove Silences checkbox
            try:
                remove_silence_checkbox = self.driver.find_element(
                    By.XPATH, "//span[text()='Remove Silences']/preceding-sibling::input[@type='checkbox']"
                )
                if not remove_silence_checkbox.is_selected():
                    remove_silence_checkbox.click()
                    print("✅ Remove Silences enabled")
            except Exception as e:
                print(f"⚠️ Could not enable Remove Silences: {e}")
            
            # Set Speed to 0.9
            try:
                speed_input = self.driver.find_element(
                    By.XPATH, "//span[text()='Speed']/ancestor::div[@class='head svelte-10lj3xl']//input[@type='number']"
                )
                speed_input.clear()
                speed_input.send_keys("0.9")
                print("✅ Speed set to 0.9")
            except Exception as e:
                print(f"⚠️ Could not set Speed: {e}")
            
            # Set NFE Steps to 32
            try:
                nfe_input = self.driver.find_element(
                    By.XPATH, "//span[text()='NFE Steps']/ancestor::div[@class='head svelte-10lj3xl']//input[@type='number']"
                )
                nfe_input.clear()
                nfe_input.send_keys("32")
                print("✅ NFE Steps set to 32")
            except Exception as e:
                print(f"⚠️ Could not set NFE Steps: {e}")
            
            # Set Cross-Fade Duration to 0.15
            try:
                crossfade_input = self.driver.find_element(
                    By.XPATH, "//span[text()='Cross-Fade Duration (s)']/ancestor::div[@class='head svelte-10lj3xl']//input[@type='number']"
                )
                crossfade_input.clear()
                crossfade_input.send_keys("0.15")
                print("✅ Cross-Fade Duration set to 0.15")
            except Exception as e:
                print(f"⚠️ Could not set Cross-Fade Duration: {e}")
            
            print("✅ Advanced Settings configured!")
            time.sleep(1)
            return True
            
        except Exception as e:
            print(f"❌ Failed to configure Advanced Settings: {e}")
            return False
    
    def close_advanced_settings(self):
        """Close the Advanced Settings dropdown"""
        try:
            print("📁 Closing Advanced Settings...")
            
            # Find and click the Advanced Settings button to close it
            advanced_button = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button.label-wrap"))
            )
            
            advanced_button.click()
            print("✅ Advanced Settings closed!")
            
            # Wait a moment for the dropdown to collapse
            time.sleep(1)
            return True
            
        except Exception as e:
            print(f"❌ Failed to close Advanced Settings: {e}")
            return False
    
    def click_synthesize(self):
        """Click the Synthesize button to generate audio"""
        try:
            print("🎵 Clicking Synthesize button...")
            
            # Find and click the Synthesize button
            synthesize_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[text()='Synthesize']"))
            )
            
            synthesize_button.click()
            print("✅ Synthesize button clicked! Audio generation started...")
            
            # Wait a moment for the process to start
            time.sleep(2)
            return True
            
        except Exception as e:
            print(f"❌ Failed to click Synthesize button: {e}")
            return False
    
    def wait_for_audio_and_download(self, timeout=300):
        """Wait for audio generation to complete and download the file"""
        try:
            print("⏳ Waiting for audio generation to complete...")
            
            # Wait for the download link to appear (indicating audio is ready)
            download_link = None
            start_time = time.time()
            
            while time.time() - start_time < timeout:
                try:
                    # Look for the download link
                    download_element = self.driver.find_element(
                        By.CSS_SELECTOR, "a.download-link[download='audio.wav']"
                    )
                    download_link = download_element.get_attribute("href")
                    
                    if download_link and "gradio_api/file" in download_link:
                        print("✅ Audio generation completed!")
                        break
                        
                except:
                    pass
                
                print("⏳ Still generating... (waiting 5 seconds)")
                time.sleep(5)
            
            if not download_link:
                print("❌ Audio generation timed out or failed")
                return False
            
            # Download the audio file
            print(f"📥 Downloading audio from: {download_link}")
            
            # Generate a unique filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"f5tts_generated_{timestamp}.wav"
            filepath = os.path.join(os.getcwd(), filename)
            
            # Download the file
            response = requests.get(download_link)
            response.raise_for_status()
            
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            print(f"✅ Audio downloaded successfully!")
            print(f"📁 Saved as: {filename}")
            print(f"📍 Location: {filepath}")
            
            # Get file size for confirmation
            file_size = os.path.getsize(filepath)
            print(f"📊 File size: {file_size:,} bytes ({file_size/1024:.1f} KB)")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to download audio: {e}")
            return False
    
    def automate_f5tts_workflow(self):
        """Complete automation workflow for F5-TTS"""
        print("\n🤖 Starting F5-TTS automation workflow...")
        
        # Step 1: Upload audio file
        audio_file_path = r"C:\Users\utsav\OneDrive\Desktop\F5-TTS\Palki.wav"
        if not self.upload_audio_file(audio_file_path):
            print("❌ Failed to upload audio file. Continuing anyway...")
        
        # Step 2: Enter text to generate
        test_text = "Rahul if memory management were that simple you would be Prime Minister by now \n\nSQL helps retrieve update and organize information efficiently it's like a librarian who actually knows where every book is"
        if not self.enter_text_to_generate(test_text):
            print("❌ Failed to enter text. Continuing anyway...")
        
        # Step 3: Open Advanced Settings
        if not self.open_advanced_settings():
            print("❌ Failed to open Advanced Settings. Continuing anyway...")
        
        # Step 4: Configure Advanced Settings
        if not self.configure_advanced_settings():
            print("❌ Failed to configure Advanced Settings. Continuing anyway...")
        
        # Step 5: Close Advanced Settings
        if not self.close_advanced_settings():
            print("❌ Failed to close Advanced Settings. Continuing anyway...")
        
        # Step 6: Click Synthesize button
        if not self.click_synthesize():
            print("❌ Failed to click Synthesize button. Continuing anyway...")
            return
        
        # Step 7: Wait for audio generation and download
        if not self.wait_for_audio_and_download():
            print("❌ Failed to download generated audio. You can download manually from the browser.")
            return
        
        print("✅ Complete automation workflow finished!")
        
        # Step 8: Close browser and exit
        print("🔴 Closing browser and exiting...")
        self.close()
        print("✅ Script completed successfully!")
    
    def keep_open(self):
        """Keep the browser open for testing"""
        if not self.driver:
            return
        
        print("\n🔄 Browser is now open for testing!")
        print("📋 Complete automation finished! You can now:")
        print("  - Review the uploaded audio file")
        print("  - Check the entered text")
        print("  - Review configured Advanced Settings:")
        print("    • Speed: 0.9")
        print("    • NFE Steps: 32") 
        print("    • Cross-Fade Duration: 0.15s")
        print("    • Remove Silences: Enabled")
        print("  - Play the generated audio in browser")
        print("  - Check the downloaded audio file in current directory")
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
        finally:
            self.close()
    
    def close(self):
        """Close the browser"""
        if self.driver:
            print("🔴 Closing browser...")
            self.driver.quit()
            self.driver = None
            print("✅ Browser closed")


def main():
    """Main function to run the Selenium test"""
    print("🚀 F5-TTS Selenium Test Script")
    print("=" * 50)
    
    # Create client
    client = F5TTSSeleniumClient("http://localhost:7860")
    
    # Setup driver
    if not client.setup_driver():
        print("❌ Failed to setup WebDriver. Exiting...")
        return
    
    # Open F5-TTS
    if not client.open_f5tts():
        print("❌ Failed to open F5-TTS. Exiting...")
        client.close()
        return
    
    # Find elements for inspection
    client.find_elements()
    
    # Run the automation workflow
    client.automate_f5tts_workflow()
    
    # Only keep browser open if it wasn't closed by the workflow
    if client.driver:
        # Keep browser open for testing
        client.keep_open()


if __name__ == "__main__":
    main() 