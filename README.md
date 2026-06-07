# Object Detection and Counting Web App

A full-stack YOLO detection dashboard that streams processed video frames with bounding boxes, IDs, a live count, and FPS. The frontend lets you upload a video or image, choose multiple YOLO classes from a searchable list, adjust the counting line position, and start/stop the webcam stream.

## Project Structure

- backend
  - app
    - main.py
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
- Upload an image to get a processed JPEG with detected boxes.
- Use the class search box to filter the 80 COCO classes and select multiple labels.
- Move the line slider to change the counting line position.
- Use the webcam toggle to start/stop live detection.

## Notes

- YOLO requires the Ultralytics package and downloads weights on first run.
- Update `DETECT_CLASSES` in `backend/app/main.py` to track other classes.
