# F5-TTS Selenium Automation

A Python package for automating F5-TTS voice cloning with multiple user profiles and camelCase naming conventions.

## 🚀 Features

- **Multi-User Support**: Manage multiple voice profiles with individual configurations
- **Automated Voice Generation**: Complete automation of F5-TTS web interface
- **Flexible Configuration**: Default settings with per-user overrides
- **Audio File Management**: Organized storage and cleanup of generated audio
- **Comprehensive Logging**: Detailed logging of all operations
- **camelCase Naming**: Consistent camelCase naming throughout the codebase

## 📁 Project Structure

```
currdir/
├── __init__.py                 # Main package initialization
├── main.py                     # Original F5TTSSeleniumClient class
├── requirements.txt            # Project dependencies
├── README.md                   # This file
├── basic_usage.py             # Example usage and quick start
├── src/                       # Source code modules
│   ├── __init__.py           # Source package initialization
│   ├── client.py             # F5TtsSeleniumClient implementation
│   ├── config.py             # Configuration management
│   └── utils.py              # Utility classes
├── audio_files/              # Audio file storage
│   ├── user1.wav            # Reference audio files
│   ├── user2.wav
│   ├── user3.wav
│   ├── user4.wav
│   ├── user5.wav
│   └── generated/           # Generated output files
├── profiles/                # Configuration files
│   ├── defaultConfig.json  # Default settings
│   └── userProfiles.json   # All user profiles
└── logs/                   # Execution logs
```

## 🛠️ Installation

### Prerequisites

1. **Python 3.6+**
2. **Google Chrome Browser**
3. **ChromeDriver** (matching your Chrome version)
4. **F5-TTS Server** running on `http://localhost:7860`

### Setup

1. **Clone or download this project**
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Add your audio files** to the `audio_files/` directory
4. **Configure user profiles** in `profiles/userProfiles.json`

## 🎯 Quick Start

### Basic Usage

```python
# Run the basic usage example
python basic_usage.py
```

### Direct Usage

```python
from src.client import F5TtsSeleniumClient
from src.config import ConfigManager

# Initialize configuration manager
configManager = ConfigManager()

# Get user configuration
userId = "user1"
userConfig = configManager.getUserConfig(userId)

# Create and run client
client = F5TtsSeleniumClient(userConfig["f5ttsUrl"])
client.setupDriver()
client.openF5tts()
client.automateF5ttsWorkflowWithUser(userId)
```

## 👥 User Profiles

### Default Configuration (`profiles/defaultConfig.json`)

```json
{
    "speed": 0.8,
    "nfeSteps": 34,
    "crossFadeDuration": 0.16,
    "removeSilences": true,
    "f5ttsUrl": "http://localhost:7860",
    "timeoutSeconds": 300,
    "downloadDirectory": "audio_files/generated"
}
```

### User Profiles (`profiles/userProfiles.json`)

Each user profile includes:
- `userName`: Display name
- `displayName`: Friendly display name
- `audioFile`: Path to reference audio file
- `config`: User-specific settings (overrides defaults)
- `outputPrefix`: Prefix for generated files
- `description`: Profile description

Example user profile:
```json
{
    "user1": {
        "userName": "User One",
        "displayName": "Professional Speaker",
        "audioFile": "audio_files/user1.wav",
        "config": {
            "speed": 0.8,
            "nfeSteps": 34,
            "crossFadeDuration": 0.16,
            "removeSilences": true
        },
        "outputPrefix": "user1Generated",
        "description": "Professional voice for business presentations"
    }
}
```

## 🔧 Configuration Options

### Audio Settings

- **speed**: Speech speed (0.1 - 2.0)
- **nfeSteps**: NFE steps for generation quality (16-64)
- **crossFadeDuration**: Cross-fade duration in seconds (0.1-1.0)
- **removeSilences**: Remove silence from audio (true/false)

### System Settings

- **f5ttsUrl**: F5-TTS server URL
- **timeoutSeconds**: Maximum wait time for generation
- **downloadDirectory**: Output directory for generated files

## 📚 API Reference

### ConfigManager

```python
configManager = ConfigManager()

# Load configurations
defaultConfig = configManager.loadDefaultConfig()
userProfiles = configManager.loadUserProfiles()

# Get user-specific data
userConfig = configManager.getUserConfig("user1")
audioFilePath = configManager.getAudioFilePath("user1")
outputPrefix = configManager.getOutputPrefix("user1")

# Manage users
allUserIds = configManager.getAllUserIds()
isValid = configManager.validateUserProfile("user1")
configManager.updateLastUsed("user1")
```

### AudioFileManager

```python
audioManager = AudioFileManager()

# File validation and management
isValid = audioManager.validateAudioFile("path/to/audio.wav")
absolutePath = audioManager.getAbsolutePath("relative/path.wav")

# Generated file management
fileName = audioManager.generateOutputFileName("user1Generated")
filePath = audioManager.getGeneratedFilePath(fileName)
generatedFiles = audioManager.listGeneratedFiles("user1Generated")

# Cleanup
deletedCount = audioManager.cleanupOldFiles(maxFiles=50)
```

### LogManager

```python
logManager = LogManager()

# Logging methods
logManager.logInfo("Information message")
logManager.logWarning("Warning message")
logManager.logError("Error message")

# Specialized logging
logManager.logUserAction("user1", "AudioGeneration", "Started")
logManager.logAudioGeneration("user1", 150, "user1.wav", "output.wav", 45.2)
```

## 🎵 Usage Examples

### 1. Basic Automation

```python
python basic_usage.py
# Select option 1 for basic usage with default user
```

### 2. Multi-User Selection

```python
python basic_usage.py
# Select option 2 to choose from available user profiles
```

### 3. Custom Text Generation

```python
from src.client import F5TtsSeleniumClient
from src.config import ConfigManager

configManager = ConfigManager()
client = F5TtsSeleniumClient()

client.setupDriver()
client.openF5tts()

# Upload specific audio file
client.uploadAudioFile("audio_files/user3.wav")

# Enter custom text
customText = "Your custom text to generate speech from."
client.enterTextToGenerate(customText)

# Configure settings
client.openAdvancedSettings()
client.configureAdvancedSettings()
client.closeAdvancedSettings()

# Generate and download
client.clickSynthesize()
client.waitForAudioAndDownload()
```

## 🔍 Troubleshooting

### Common Issues

1. **ChromeDriver not found**
   - Download ChromeDriver from https://chromedriver.chromium.org/
   - Ensure it's in your PATH or project directory

2. **F5-TTS not accessible**
   - Verify F5-TTS is running on http://localhost:7860
   - Check firewall and network settings

3. **Audio file not found**
   - Ensure audio files exist in `audio_files/` directory
   - Check file paths in `userProfiles.json`

4. **Permission errors**
   - Ensure write permissions for `audio_files/generated/` and `logs/`

### Debug Mode

Enable debug logging:
```python
from src.utils import LogManager
import logging

logManager = LogManager(logLevel=logging.DEBUG)
```

## 📝 Logging

Logs are automatically saved to `logs/` directory with daily rotation:
- **File**: `f5tts_automation_YYYYMMDD.log`
- **Format**: Timestamp, level, and detailed messages
- **Cleanup**: Automatic cleanup of logs older than 30 days

## 🤝 Contributing

1. Follow camelCase naming conventions
2. Add type hints to all functions
3. Include docstrings for all classes and methods
4. Test with multiple user profiles
5. Update README for new features

## 📄 License

This project is open source. Feel free to modify and distribute.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section
2. Review log files in `logs/` directory
3. Ensure all prerequisites are installed
4. Verify F5-TTS server is running

---

**Happy Voice Cloning! 🎤✨** 