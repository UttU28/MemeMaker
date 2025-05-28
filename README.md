# F5-TTS Gradio API Automation

A Python package for automating F5-TTS voice cloning using Gradio API calls with multi-user profile support and camelCase naming conventions.

## Features

- 🎵 **Gradio API Integration**: Direct API calls to F5-TTS (no browser automation needed)
- 👥 **Multi-User Profiles**: Support for 5 different voice profiles
- 🔧 **Configurable Settings**: Speed, NFE steps, cross-fade duration, and silence removal
- 📁 **Audio File Management**: Organized audio files with automatic cleanup
- 📊 **Comprehensive Logging**: Detailed logs for all operations
- 🎯 **camelCase Naming**: Consistent naming conventions throughout

## Installation

1. **Clone or download this repository**
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Ensure F5-TTS is running:**
   - Start your F5-TTS server (usually at `http://localhost:7860`)
   - Make sure the Gradio interface is accessible

## Quick Start

### Basic Usage
```python
from src.client import F5TtsGradioClient

# Create client
client = F5TtsGradioClient("http://localhost:7860")

# Connect to API
client.connectToGradio()

# Generate speech with default user
client.generateSpeechWithUser("user1", "Hello, this is a test!")

# Clean up
client.close()
```

### Using the Interactive Menu
```bash
python basic_usage.py
```

### Simple Test
```bash
python test.py
```

### Main Script
```bash
python main.py
```

## User Profiles

The system includes 5 pre-configured user profiles:

| User ID | Display Name | Voice Style | Speed | NFE Steps | Audio File |
|---------|--------------|-------------|-------|-----------|------------|
| user1   | Palki        | Professional Speaker | 0.9 | 34 | Palki.wav |
| user2   | Shashi        | Casual Speaker | 0.9 | 40 | Shashi.wav |
| user3   | JaiShankar   | Narrator Voice | 0.85 | 36 | JaiShankar.wav |
| user4   | Modi         | Slow & Clear | 0.85 | 32 | Modi.wav |
| user5   | Rahul        | Energetic Speaker | 0.82 | 38 | Rahul.wav |

## Configuration

### Default Configuration (`profiles/defaultConfig.json`)
```json
{
    "speed": 0.8,
    "nfeSteps": 34,
    "crossFadeDuration": 0.16,
    "removeSilences": true,
    "f5ttsUrl": "http://localhost:7860",
    "timeoutSeconds": 300,
    "downloadDirectory": "audio_files/generated",
    "defaultAudioFile": "audio_files/Palki.wav",
    "defaultOutputPrefix": "defaultGenerated"
}
```

### User Profiles (`profiles/userProfiles.json`)
Each user profile contains:
- `userName`: Display name
- `audioFile`: Path to reference audio file
- `config`: Voice generation settings
- `outputPrefix`: Prefix for generated files
- `description`: Profile description

## API Reference

### F5TtsGradioClient

#### Core Methods
- `connectToGradio()`: Connect to F5-TTS Gradio API
- `generateSpeechWithApi(audioFilePath, textToGenerate, userConfig)`: Generate speech using API
- `generateSpeechWithUser(userId, customText)`: Generate speech with user profile
- `downloadAndSaveAudio(apiResult, outputPrefix)`: Save generated audio
- `testConnection()`: Test API connection
- `close()`: Clean up resources

#### Configuration Methods
- `listAvailableUsers()`: Get list of user profiles
- `getUserInfo(userId)`: Get user profile information

### ConfigManager

#### Profile Management
- `getUserProfile(userId)`: Get user profile
- `getUserConfig(userId)`: Get merged configuration
- `getAllUserIds()`: Get all user IDs
- `updateLastUsed(userId)`: Update last used user

#### File Path Methods
- `getAudioFilePathWithFallback(userId)`: Get audio file with fallback
- `getOutputPrefixWithFallback(userId)`: Get output prefix with fallback

### AudioFileManager

#### File Operations
- `validateAudioFile(filePath)`: Validate audio file
- `generateOutputFileName(userPrefix)`: Generate output filename
- `listGeneratedFiles(userPrefix)`: List generated files
- `cleanupOldFiles(maxFiles)`: Clean up old files

### LogManager

#### Logging Methods
- `logInfo(message)`: Log info message
- `logUserAction(userId, action, details)`: Log user action
- `logAudioGeneration(...)`: Log audio generation details
- `logError(error, context)`: Log error with context

## Directory Structure

```
currdir/
├── __init__.py
├── main.py                 # Main script
├── requirements.txt        # Dependencies
├── README.md              # This file
├── basic_usage.py         # Interactive usage examples
├── test.py               # Simple test script
├── src/
│   ├── __init__.py
│   ├── client.py         # F5TtsGradioClient
│   ├── config.py         # ConfigManager
│   └── utils.py          # AudioFileManager, LogManager
├── audio_files/
│   ├── Palki.wav         # Reference audio files
│   ├── Shashi.wav
│   ├── JaiShankar.wav
│   ├── Modi.wav
│   ├── Rahul.wav
│   └── generated/        # Generated audio files
├── profiles/
│   ├── defaultConfig.json    # Default settings
│   └── userProfiles.json     # User profiles
└── logs/                     # Log files
```

## Configuration Parameters

### Voice Generation Settings

- **speed** (0.1-2.0): Speech rate (1.0 = normal speed)
- **nfeSteps** (16-64): Neural Flow Estimation steps (higher = better quality, slower)
- **crossFadeDuration** (0.05-1.0): Smooth transitions between segments (seconds)
- **removeSilences** (boolean): Remove long pauses from generated audio

### System Settings

- **f5ttsUrl**: F5-TTS server URL
- **timeoutSeconds**: Maximum generation wait time
- **downloadDirectory**: Directory for generated files
- **defaultAudioFile**: Fallback audio file
- **defaultOutputPrefix**: Default output file prefix

## Examples

### Generate Speech with Custom Settings
```python
from src.client import F5TtsGradioClient

client = F5TtsGradioClient()
client.connectToGradio()

# Custom configuration
customConfig = {
    "speed": 0.8,
    "nfeSteps": 40,
    "crossFadeDuration": 0.2,
    "removeSilences": True
}

result = client.generateSpeechWithApi(
    audioFilePath="audio_files/Palki.wav",
    textToGenerate="Your custom text here",
    userConfig=customConfig
)

if result:
    savedPath = client.downloadAndSaveAudio(result, "customGenerated")
    print(f"Audio saved to: {savedPath}")

client.close()
```

### Batch Processing Multiple Users
```python
from src.client import F5TtsGradioClient
from src.config import ConfigManager

configManager = ConfigManager()
client = F5TtsGradioClient()
client.connectToGradio()

text = "This is a test message for all users."

for userId in configManager.getAllUserIds():
    print(f"Generating for {userId}...")
    success = client.generateSpeechWithUser(userId, text)
    if success:
        print(f"✅ Success for {userId}")
    else:
        print(f"❌ Failed for {userId}")

client.close()
```

## Troubleshooting

### Common Issues

1. **Connection Failed**
   - Ensure F5-TTS server is running
   - Check the URL in configuration
   - Verify Gradio interface is accessible

2. **Audio File Not Found**
   - Check file paths in user profiles
   - Ensure audio files exist in `audio_files/` directory
   - Verify file permissions

3. **Generation Failed**
   - Check F5-TTS server logs
   - Verify audio file format (WAV, MP3, FLAC supported)
   - Try reducing NFE steps for faster generation

4. **Import Errors**
   - Install required dependencies: `pip install -r requirements.txt`
   - Ensure Python path includes the project directory

### Performance Tips

- **Faster Generation**: Lower `nfeSteps` (16-24 for quick tests)
- **Better Quality**: Higher `nfeSteps` (40-64 for production)
- **Shorter Audio**: Use shorter reference audio files (10-30 seconds)
- **Batch Processing**: Reuse the same client connection for multiple generations

## Dependencies

- `gradio_client>=0.8.0`: Gradio API client
- `datetime`: Date/time utilities (built-in)

## License

This project is provided as-is for educational and research purposes.

## Contributing

Feel free to submit issues, feature requests, or pull requests to improve this automation package. 