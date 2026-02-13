# Hugging Face Deployment Guide (Python Backend)

To deploy the updated Python backend (with Phi-2 support) to Hugging Face Spaces, follow these steps.

## 1. Create/Update Space
1. Go to your [Hugging Face Spaces](https://huggingface.co/spaces).
2. Create a new Space or select your existing one.
3. **SDK**: Select **Docker**.
4. **Hardware**: 
   - **IMPORTANT**: For Phi-2 and Whisper Large, you **MUST** use a GPU tier (e.g., **NVIDIA T4 Small** or higher). 
   - The "CPU Basic" tier will crash or be extremely slow.

## 2. Files to Upload
Upload the following files from your `python-backend` folder to the root of your Hugging Face Space:

| File Name | Description |
|-----------|-------------|
| `app.py` | Main Flask entry point |
| `config.py` | Configuration constants |
| `document_generator.py` | T5 and Whisper logic |
| `meeting_summarizer.py` | **[NEW]** Phi-2 and meeting logic |
| `requirements.txt` | Dependencies (updated with `einops`, `protobuf`, etc.) |
| `Dockerfile` | Container build instructions (updated) |

## 3. Configuration Check
The `Dockerfile` is already configured to:
- Install `ffmpeg` (required for audio).
- Use `gunicorn` for a production-ready server.
- Set the timeout to 300 seconds (5 minutes) to handle heavy model processing.

## 4. Connecting your Frontend
Once the Space is building and running:
1. Copy the public URL of your Space (e.g., `https://your-name-reqgen-backend.hf.space`).
2. Update your **Vercel** or local frontend `.env` file:
   ```
   PYTHON_BACKEND_URL=https://your-name-reqgen-backend.hf.space
   ```

## 5. Troubleshooting
If you see a "Critical timeout" or "Connection refused" in Hugging Face logs:
- Ensure the hardware is set to GPU.
- Check the logs for any `ModuleNotFoundError` (though `requirements.txt` should cover everything).
