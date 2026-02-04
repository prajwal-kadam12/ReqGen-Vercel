---
title: ReqGen Audio Transcription API
emoji: 🎤
colorFrom: blue
colorTo: purple
sdk: docker
pinned: false
license: mit
app_port: 7860
---

# ReqGen - Audio Transcription & Document Generation API

A Flask-based REST API for audio transcription using OpenAI Whisper and text summarization using T5 models.

## Features

- 🎤 **Audio Transcription** - Convert audio to text using OpenAI Whisper
- 📝 **Text Summarization** - Summarize transcribed text using T5 models
- 📄 **Document Generation** - Generate BRD/PO documents from text

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Health check |
| `/api/transcribe` | POST | Transcribe audio file |
| `/api/summarize` | POST | Summarize text |
| `/api/process-audio` | POST | Transcribe + Summarize (combined) |
| `/api/generate-document` | POST | Generate BRD/PO document |

## Usage

### Transcribe Audio
```bash
curl -X POST https://YOUR-SPACE-URL/api/process-audio \
  -F "audio=@your_audio.mp3"
```

### Summarize Text
```bash
curl -X POST https://YOUR-SPACE-URL/api/summarize \
  -H "Content-Type: application/json" \
  -d '{"text": "Your text here..."}'
```

## Supported Audio Formats

- MP3, WAV, M4A, OGG, FLAC, AAC, WMA, WebM

## Configuration

Models used:
- **Whisper**: tiny (for faster processing)
- **T5**: google/flan-t5-small (for summarization)

## License

MIT License
