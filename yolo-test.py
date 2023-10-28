from collections import defaultdict
import cv2
import numpy as np
from ultralytics import YOLO

model = YOLO('yolov8m-seg.pt')
cap = cv2.VideoCapture(0)
objects_to_track = ["tissue", "scissors", "knife"]
track_history = defaultdict(lambda: [])

# Define a function to check if an object is at the center of the frame
def is_object_at_center(box, frame_shape):
    x, y, w, h = box
    frame_center_x = frame_shape[1] / 2
    frame_center_y = frame_shape[0] / 2
    return x <= frame_center_x <= x + w and y <= frame_center_y <= y + h

while cap.isOpened():
    success, frame = cap.read()

    if success:
        results = model.track(frame, persist=True)
        for result in results:
            if result.boxes is None or result.boxes.id is None:
                continue
            boxes = result.boxes.xywh.cpu()
            track_ids = result.boxes.id.cpu().numpy().astype(int)
            frame_shape = frame.shape

            frame = result.plot()

            for box, track_id in zip(boxes, track_ids):
                if is_object_at_center(box, frame_shape):
                    # Object is at the center of the frame
                    track = track_history[track_id]
                    track.append(box)
                    if len(track) > 30:
                        track.pop(0)

                    points = np.array(track).astype(np.int32)
                    for i in range(1, len(points)):
                        cv2.line(frame, tuple(points[i - 1][:2]), tuple(points[i][:2]), (0, 255, 0), 2)

        cv2.imshow("Tracking", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    else:
        break

cap.release()
cv2.destroyAllWindows()
