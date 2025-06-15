# 🎬 AI Voice Cloning & Automated Video Generation System

> **A comprehensive AI-powered pipeline that transforms GRE vocabulary words into engaging educational videos with cloned voices, dynamic visuals, and intelligent content generation.**

## 🌟 Project Overview

This sophisticated system combines multiple AI technologies to automatically create educational videos from vocabulary words. It generates natural dialogues, clones specific voices, detects emotional contexts, and produces professional-quality videos with subtitles and visual elements.

### ✨ Key Features

- **🤖 AI Dialogue Generation**: Creates natural conversations using OpenAI GPT or local Ollama models
- **🎤 Voice Cloning**: High-quality speech synthesis using F5-TTS with custom voice profiles
- **😊 Mood Detection**: Intelligent emotion recognition for character expression matching
- **🎥 Automated Video Production**: Complete video pipeline with backgrounds, overlays, and subtitles
- **🔄 Bulk Processing**: Continuous processing of large vocabulary datasets
- **🎲 Dynamic Content**: Random background selection for variety
- **📱 Mobile-Optimized**: Vertical video format (1080x1920) for social media

## 🏗️ System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Input Word    │───▶│  LLM Service    │───▶│   Dialogue      │
│   (GRE Vocab)   │    │ (OpenAI/Ollama) │    │  Generation     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                        │
                                                        ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Final Video     │◀───│ Video Pipeline  │◀───│ Voice Cloning   │
│   Output        │    │   (FFmpeg)      │    │   (F5-TTS)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                ▲                        │
                                │                        ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Background     │───▶│ Mood Detection  │◀───│ Audio Files     │
│   Videos        │    │ & Image Match   │    │  Generation     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🛠️ Technology Stack

### Core AI Services
- **🧠 Large Language Models**: OpenAI GPT-3.5/4 or Local Ollama (Llama 3.2)
- **🎤 Text-to-Speech**: F5-TTS (High-quality voice cloning)
- **👂 Speech Recognition**: WhisperX (For subtitle alignment)
- **😊 Emotion AI**: Custom mood detection system

### Media Processing
- **🎬 Video Processing**: FFmpeg with CUDA acceleration
- **🔊 Audio Processing**: PyDub, AudioSegment
- **📝 Subtitle Generation**: SRT format with word-level timing

### Infrastructure
- **🖥️ GPU Acceleration**: NVIDIA CUDA for video encoding
- **🌐 Web Interface**: Gradio (F5-TTS integration)
- **💾 Data Storage**: JSON-based configuration and progress tracking

## 📁 Project Structure

```
VoiceClonning_F5-TTS/
├── 🎬 main.py                 # Main pipeline orchestrator
├── 📥 downloadCrop.py         # YouTube video downloader & processor
├── 📝 prompts.py             # LLM prompt templates
├── ⚙️ requirements.txt        # Python dependencies
├── 📚 README.md              # This documentation
│
├── 📊 data/                   # Core data directory
│   ├── 🎞️ background/        # Background video library (001-020)
│   ├── 🖼️ images/            # Character emotion images
│   ├── 🔊 audio_files/       # Voice samples & generated audio
│   ├── 🎥 video_output/      # Final processed videos
│   ├── 📄 greWords.json      # GRE vocabulary database (4977+ words)
│   ├── 👥 userProfiles.json  # Voice & character configurations
│   ├── 💾 wordData.json      # Processing metadata & progress
│   └── 🎬 outro.mp4          # Video ending sequence
│
├── 🔧 src/                   # Core modules
│   ├── 🤖 llm.py            # Language model service
│   ├── 🎤 client.py         # F5-TTS integration
│   ├── ⚙️ config.py         # Configuration management
│   └── 🛠️ utils.py          # Audio/file utilities
│
├── 🏗️ F5-TTS/               # Voice cloning engine
└── 📊 logs/                 # Processing logs & analytics
```

## 🚀 Installation & Setup

### Prerequisites
- **Python 3.8+**
- **NVIDIA GPU** with CUDA support
- **FFmpeg** with CUDA encoding
- **8GB+ RAM** recommended

### 1. Clone Repository
```bash
git clone <repository-url>
cd VoiceClonning_F5-TTS
```

### 2. Create Virtual Environment
```bash
python -m venv env
# Windows
env\Scripts\activate
# Linux/Mac
source env/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Setup F5-TTS Service
```bash
cd F5-TTS
pip install -e .
# Start Gradio service
python -m f5_tts.gradio_app
```

### 5. Configure Environment
```bash
# Create .env file
echo "OPENAI_API_KEY=your_openai_key_here" > .env
echo "OLLAMA_URL=http://localhost:11434" >> .env
```

### 6. Prepare Voice Samples
Place voice samples in `data/audio_files/`:
- `Modi.wav`, `Palki.wav`, `JaiShankar.wav`, etc.

## 🎯 Usage Guide

### Single Word Processing
```bash
# Process a single vocabulary word (background auto-selected)
python main.py "aberrant"
```

### Bulk Processing (Recommended)
```bash
# Process all unused words continuously (each gets random background)
python main.py --bulk
# or
python main.py -b
```

### Background Video Management
```bash
# Download and prepare background videos from YouTube
python downloadCrop.py
```

### Key Features
- **🎲 Automatic Background Selection**: Each video gets a randomly selected background
- **🔄 Continuous Processing**: Bulk mode processes all words until completion
- **⚡ GPU Acceleration**: CUDA-accelerated video processing for speed
- **📊 Progress Tracking**: Real-time progress updates and statistics

## 🔄 Complete Workflow

### 1. **Word Input**
- Single word: Manual input
- Bulk mode: Automatic from `greWords.json`

### 2. **Dialogue Generation**
- LLM creates natural conversation around the word
- Multiple characters discuss word meaning and usage
- Contextual examples and explanations

### 3. **Voice Synthesis**
- F5-TTS clones specific character voices
- High-quality audio generation (16kHz, mono)
- Automatic silence trimming and cleanup

### 4. **Mood Detection**
- AI analyzes dialogue tone and emotion
- Matches appropriate character expressions
- Selects corresponding facial expression images

### 5. **Video Assembly**
- Random background video selection
- Character image overlays with timing
- Audio synchronization and mixing
- CUDA-accelerated video encoding

### 6. **Subtitle Generation**
- WhisperX word-level transcription
- SRT format with precise timing
- Styled subtitles with word highlighting
- Main word overlay with emphasis

### 7. **Final Output**
- Mobile-optimized format (1080x1920)
- H.264 encoding with NVIDIA acceleration
- Automatic file naming and organization

## ⚙️ Configuration Files

### `userProfiles.json`
Defines character voices and emotions:
```json
{
  "users": {
    "modi": {
      "displayName": "Modi",
      "audioFile": "Modi.wav",
      "emotions": {
        "confident": "data/images/modi_confidentl.png",
        "serious": "data/images/modi_seriousr.png"
      }
    }
  }
}
```

### `greWords.json`
Vocabulary database with progress tracking:
```json
{
  "1": {
    "word": "abate",
    "used": false,
    "finalVideoFile": ""
  }
}
```

## 🎨 Character System

### Available Characters
- **Modi**: Political leader voice & expressions
- **Palki**: News anchor voice & analytical expressions  
- **JaiShankar**: Diplomatic voice & strategic expressions
- **Shashi**: Eloquent speaker voice & thoughtful expressions
- **Rahul**: Young politician voice & varied expressions

### Emotion Types
- `confident`, `serious`, `amused`, `analytical`
- `diplomatic`, `eloquent`, `contemplative`
- `surprised`, `confused`, `sheepish`

## 🎬 Video Production Features

### Background Videos
- 20 unique background videos (`background001.mp4` - `background020.mp4`)
- Random selection for variety
- Mobile-optimized format (1080x1920)
- 1.5-minute segments for consistency

### Visual Effects
- Dynamic character overlays
- Emotion-synchronized expressions
- Professional subtitle styling
- Word emphasis and highlighting
- Smooth transitions and timing

### Audio Processing
- Multi-speaker voice cloning
- Automatic silence detection
- Audio concatenation and mixing
- Volume normalization
- High-quality output (24kHz AAC)

## 🚀 Performance & Optimization

### GPU Acceleration
- **NVIDIA CUDA**: Video encoding acceleration
- **H.264 NVENC**: Hardware-accelerated compression
- **Memory Optimization**: Efficient batch processing

### Processing Speed
- **Single Word**: ~2-3 minutes
- **Bulk Processing**: ~150 words/hour
- **Background Preparation**: ~30 seconds per 1.5min segment

### Quality Settings
- **Video**: 1080x1920, H.264, CRF 23
- **Audio**: 24kHz, AAC, stereo
- **Subtitles**: SRT with word-level timing

## 🔧 Advanced Features

### Bulk Processing
- Continuous processing with progress tracking
- Automatic error recovery and skipping
- Session statistics and completion metrics
- Graceful interruption (Ctrl+C) with saved progress

### Error Handling
- Robust exception handling at each step
- Automatic fallbacks (GPU→CPU, OpenAI→Ollama)
- Missing file detection and replacement
- Process recovery and continuation

### Monitoring & Logging
- Detailed processing logs
- Performance metrics tracking
- Error reporting and debugging
- Progress visualization

## 📈 Use Cases

### Educational Content
- **Vocabulary Building**: GRE, SAT, academic preparation
- **Language Learning**: Pronunciation and context
- **Academic Videos**: Professional educational content

### Content Creation
- **Social Media**: Instagram, TikTok, YouTube Shorts
- **E-learning**: Course materials and tutorials
- **Marketing**: Educational brand content

### Accessibility
- **Audio Learning**: For visual learners
- **Multi-language**: Easy voice adaptation
- **Consistent Quality**: Automated production standards

## 🛠️ Troubleshooting

### Common Issues

**F5-TTS Connection Failed**
```bash
# Check Gradio service
curl http://localhost:7860/
# Restart if needed
cd F5-TTS && python -m f5_tts.gradio_app
```

**CUDA/GPU Issues**
```bash
# Verify CUDA installation
nvidia-smi
# Check FFmpeg CUDA support
ffmpeg -hwaccels
```

**Audio Generation Fails**
- Verify voice samples in `data/audio_files/`
- Check file permissions and formats
- Ensure F5-TTS service is running

**Video Processing Errors**
- Confirm background videos exist
- Check disk space availability
- Verify FFmpeg installation

## 🔮 Future Enhancements

### Planned Features
- **Multi-language Support**: International voice cloning
- **Advanced Emotions**: More nuanced expression detection
- **Interactive Mode**: Real-time preview and editing
- **Cloud Integration**: Scalable processing infrastructure
- **API Interface**: RESTful service for integration

### Optimization Goals
- **Faster Processing**: Optimized pipeline efficiency
- **Better Quality**: Enhanced voice and video quality
- **More Voices**: Expanded character library
- **Smart Caching**: Reduced regeneration overhead

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create feature branch: `git checkout -b feature/new-feature`
3. Follow coding standards and add tests
4. Submit pull request with detailed description

### Guidelines
- Follow Python PEP 8 style guidelines
- Add comprehensive docstrings
- Include error handling and logging
- Test with both single and bulk processing

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **F5-TTS**: High-quality voice cloning technology
- **OpenAI**: GPT language models for dialogue generation
- **Ollama**: Local LLM inference capability
- **WhisperX**: Precise speech recognition and alignment
- **FFmpeg**: Powerful multimedia processing framework

---

## 📞 Support

For issues, questions, or contributions:
- **Documentation**: This README and inline code comments
- **Logs**: Check `logs/` directory for detailed error information
- **Testing**: Use single word mode for debugging before bulk processing

**Happy Video Creation! 🎬✨** 