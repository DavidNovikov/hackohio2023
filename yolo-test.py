# Import necessary libraries
from collections import defaultdict
import cv2
import numpy as np
from ultralytics import YOLO

# Load the YOLOv8 segmentation model
model = YOLO('yolov8m-seg.pt')

# Open a video capture from the default camera (change the index if using a different camera)
cap = cv2.VideoCapture(0)

# Define the object classes to track
objects_to_track = ["tissue", "scissors", "knife"]

# Create a dictionary to store tracking history for each object
track_history = defaultdict(lambda: [])

# Define a threshold for how long an object needs to be at the center to be considered inside the patient
center_duration_threshold = 5

# Define the center area (a rectangle)
center_area_color = (0, 0, 255)
center_area_thickness = 2

# Create a dictionary to keep track of the state of each object
object_states = defaultdict(lambda: "outside")

# Create a dictionary to keep track of the count of objects
object_counts = defaultdict(int)

# Create a dictionary to store the previous state of each object
previous_object_states = defaultdict(lambda: "outside")

# Define a function to check if an object's bounding box overlaps with the center area
def is_object_at_center(box, center_rect):
    x, y, w, h = box
    rect_x, rect_y, rect_w, rect_h = center_rect
    return x < rect_x + rect_w and x + w > rect_x and y < rect_y + rect_h and y + h > rect_y


initalObjectsCounted = False
# Main loop for processing video frames
while cap.isOpened():
    # Read a frame from the video
    success, frame = cap.read()

    if success:
        # Draw the center area on the frame
        frame_shape = frame.shape
        center_x = frame_shape[1] // 2
        center_y = frame_shape[0] // 2
        center_width = center_height = 150
        center_rect = (center_x - center_width // 2, center_y - center_height // 2, center_width, center_height)

        cv2.rectangle(frame, (center_rect[0], center_rect[1]),
                      (center_rect[0] + center_rect[2], center_rect[1] + center_rect[3]), center_area_color, center_area_thickness)

        # Run YOLOv8 tracking on the frame, persisting tracks between frames
        results = model.track(frame, persist=True, verbose=False)
        frame = results[0].plot()

        for result in results:
            if result.boxes is None or result.boxes.id is None:
                continue

            boxes = result.boxes.xywh.cpu()
            track_ids = result.boxes.id.cpu().numpy().astype(int)

            # Loop through tracked objects and check if they are within the center area
            for box, track_id, d in zip(boxes, track_ids, reversed(result.boxes)):
                c, conf, id = int(d.cls), float(d.conf), None if d.id is None else int(d.id.item())
                name = result.names[c]

                track = track_history[track_id]
                track.append(box)

                if not initalObjectsCounted:
                    # Update object count
                    object_counts[name] += 1

                # Only leave a tracking line trail of up to 30
                if len(track) > 30:
                    track.pop(0)

                # Draw tracking lines on the annotated frame
                points = np.array(track).astype(np.int32)
                for i in range(1, len(points)):
                    cv2.line(frame, tuple(points[i - 1][:2]), tuple(points[i][:2]), (0, 255, 0), 2)

                if is_object_at_center(box, center_rect):
                    # Object is within the center area
                    if len(track) >= center_duration_threshold:
                        # The object has been within the center area for the threshold duration, consider it inside the patient
                        if object_states[track_id] == "outside":
                            print(f"{name} with track ID {track_id} is potentially inside the patient.")
                            
                            # Update object count and state
                            object_counts[name] += 1
                            object_states[track_id] = "inside"
                    elif object_states[track_id] == "inside":
                        # Object was inside but has not stayed long enough in the center
                        print(f"{name} with track ID {track_id} has returned to the center area but has not stayed long enough.")

                else:
                    # Object is outside the center area
                    if object_states[track_id] == "inside":
                        print(f"{name} with track ID {track_id} has moved outside the patient's body.")
                        
                        # Update object count and state
                        object_counts[name] -= 1
                        if object_counts[name] < 0:
                            object_counts[name] = 0
                        object_states[track_id] = "outside"

            
            if not initalObjectsCounted:
                initalObjectsCounted = True
                print("Initial object counts:")
                for name, count in object_counts.items():
                    print(f"{name}: {count}")

            cv2.imshow("YOLOv8 Tracking", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

# Print the final object counts
for name, count in object_counts.items():
    print(f"Number of {name}s detected inside the patient's body: {count}")

# Release the video capture object and close the display window
cap.release()
cv2.destroyAllWindows()
