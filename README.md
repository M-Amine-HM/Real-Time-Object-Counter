# Vehicle Detection and Counting Web App

A full-stack vehicle detection dashboard with two detection modes:

- Classical motion detection (OpenCV MOG2)
- YOLO vehicle detection (car, truck, bus, motorbike)

The backend streams processed video frames with bounding boxes, IDs, a live count, and FPS. The frontend lets you upload a video, start/stop the webcam stream, and switch detection modes.

## Project Structure

- backend
  - app
    - routes
    - services
    - state.py
- frontend
  - src

## Backend Setup

1. Create a Python environment.
2. Install dependencies:

```bash
pip install -r backend/requirements.txt
```

3. Start the API:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The server runs at `http://localhost:8000`.

## Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

The UI runs at `http://localhost:5173`.

## Usage

- Upload a video to generate a stream URL for processed frames.
- Use the webcam toggle to start/stop live detection.
- Adjust line coordinates to match the road in your scene.

## Notes

- YOLO mode requires the Ultralytics package and downloads weights on first run.
- If YOLO is unavailable, switch to Classical mode.
