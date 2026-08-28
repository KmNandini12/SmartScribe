import requests
import time

API_URL = "http://127.0.0.1:8000/api/v1"

print("1. Uploading transcript...")
with open("test_transcript.txt", "rb") as f:
    response = requests.post(f"{API_URL}/transcripts/", files={"file": f})
    
if response.status_code != 201:
    print("Error uploading:", response.text)
    exit(1)
    
transcript = response.json()
transcript_id = transcript["id"]
print(f"Uploaded successfully. Transcript ID: {transcript_id}")

print("\n2. Triggering summarize job...")
response = requests.post(f"{API_URL}/jobs/summarize", json={"transcript_id": transcript_id})
if response.status_code != 202:
    print("Error starting job:", response.text)
    exit(1)

job_id = response.json()["job_id"]
print(f"Job triggered successfully. Job ID: {job_id}")

print("\n3. Polling for completion...")
while True:
    response = requests.get(f"{API_URL}/jobs/{job_id}")
    job = response.json()
    status = job["status"]
    print(f"Status: {status}")
    
    if status in ["COMPLETED", "FAILED", "FAILED_TIMEOUT"]:
        break
        
    time.sleep(2)

print("\nTest completed.")
