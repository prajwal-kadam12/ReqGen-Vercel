import requests
import sys
import os

def test_meeting_processing(audio_file_path):
    url = "http://localhost:5001/api/process-meeting"
    
    if not os.path.exists(audio_file_path):
        print(f"Error: File {audio_file_path} not found.")
        return

    print(f"Testing /api/process-meeting with {audio_file_path}...")
    
    try:
        with open(audio_file_path, 'rb') as f:
            files = {'audio': f}
            data = {'meeting_type': 'test_meeting'}
            
            response = requests.post(url, files=files, data=data)
            
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("\n✅ Success!")
            print(f"Transcript length: {len(result.get('transcript', ''))}")
            print(f"Summary length: {len(result.get('summary', ''))}")
            print(f"Model used: {result.get('model')}")
            print(f"Compression: {result.get('compression'):.2f}%")
        else:
            print("\n❌ Failed")
            print(response.text)
            
    except Exception as e:
        print(f"\n❌ Exception: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_phi2.py <path_to_audio_file>")
        # Create a dummy file for testing if none provided
        dummy_file = "test_audio.wav"
        if not os.path.exists(dummy_file):
            print("Creating dummy WAV file for connection test...")
            # This won't be a valid audio file really, but enough to hit the endpoint logic
            # actually better to not send garbage audio as whisper might choke.
            # We'll just print usage and exit.
            print("Please provide a valid audio file path.")
    else:
        test_meeting_processing(sys.argv[1])
