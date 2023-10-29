from collections import defaultdict
import os
import cv2
import numpy as np
from ultralytics import YOLO

async def run_cv(client):
    # Load the YOLOv8 segmentation model
    model = YOLO('yolov8m-seg.pt')

    # Open a video capture from the default camera (change the index if using a different camera)
    cap = cv2.VideoCapture(1)

    # Define the object classes to track
    object_names = ["tissue", "scissors", "knife"]

    # Create a dictionary to store tracking history for each object
    track_history = defaultdict(list)

    # Create a dictionary to keep track of the state of each object
    object_states = defaultdict(lambda: {"state": None, "name": None})

    # Create a dictionary to store the count of objects inside the patient
    objects_inside = {"tissue": 0, "scissors": 0, "knife": 0}

    # Create a dictionary to store the previous state of each object
    previous_object_states = defaultdict(lambda: None)

    # Define a function to check if an object's bounding box overlaps with the center area
    def is_object_at_center(box, box2):
        x1, y1, w1, h1 = box
        x2, y2, w2, h2 = box2

        # Calculate the coordinates of the top-left and bottom-right corners of the boxes
        x1_tl, y1_tl, x1_br, y1_br = x1 - w1 / 2, y1 - h1 / 2, x1 + w1 / 2, y1 + h1 / 2
        x2_tl, y2_tl, x2_br, y2_br = x2 - w2 / 2, y2 - h2 / 2, x2 + w2 / 2, y2 + h2 / 2

        # Check for overlap
        return not (x1_br < x2_tl or x1_tl > x2_br or y1_br < y2_tl or y1_tl > y2_br)

    previous_track_ids = None
    initial_objects_counted = False

    inserted_item_index = 0

    # Main loop for processing video frames
    while cap.isOpened():
        # Read a frame from the video
        success, frame = cap.read()

        if success:
            # Create a dictionary to keep track of the count of objects
            total_object_counts = defaultdict(int)

            # Draw the center area on the frame
            frame_shape = frame.shape
            center_x = frame_shape[1] // 2 - 30
            center_y = frame_shape[0] // 2 - 30
            center_width = center_height = 200
            center_bbox = (center_x, center_y, center_width, center_height)
            center_rect = (center_x - center_width // 2, center_y - center_height // 2, center_width, center_height)

            cv2.rectangle(frame, (center_rect[0], center_rect[1]),
                        (center_rect[0] + center_rect[2], center_rect[1] + center_rect[3]), (0, 0, 255), 2)

            # Run YOLOv8 tracking on the frame, persisting tracks between frames
            results = model.track(frame, persist=True, verbose=False)
            frame = results[0].plot(label_filter=object_names)

            for result in results:
                if result.boxes is None or result.boxes.id is None:
                    continue

                boxes = result.boxes.xywh.cpu()

                track_ids = result.boxes.id.cpu().numpy().astype(int)

                # Loop through tracked objects and check if they are within the center area
                for box, track_id, d in zip(boxes, track_ids, result.boxes):
                    c, conf, id = int(d.cls), float(d.conf), None if d.id is None else int(d.id.item())
                    name = result.names[c]

                    if name is None or name not in object_names:
                        continue

                    total_object_counts[name] += 1

                    track = track_history[track_id]
                    track.append(box)

                    # Only leave a tracking line trail of up to 30
                    if len(track) > 30:
                        track.pop(0)

                    # Draw tracking lines on the annotated frame
                    points = np.array(track).astype(np.int32)
                    for i in range(1, len(points)):
                        cv2.line(frame, tuple(points[i - 1][:2]), tuple(points[i][:2]), (0, 255, 0), 2)

                    if is_object_at_center(box, center_bbox):
                        # Object is within the center area
                        if object_states[track_id]["state"] != "inside":
                            object_states[track_id] = {"state": "inside", "name": name}

                            if previous_object_states[track_id] == "outside":
                                # save frame
                                cwd = os.getcwd()
                                path = f"{cwd}/frames/{inserted_item_index}.jpg"
                                cv2.imwrite(path, frame)
                                client.print(f"objects_inside: {objects_inside}")
                                client.print(f"[EVENT] INSERTED: {name} [{track_id}], {path}")
                                await client.send_item_inserted(path, name)

                                objects_inside[name] += 1
                                inserted_item_index += 1
                    else:
                        if object_states[track_id]["state"] != "outside":
                            object_states[track_id] = {"state": "outside", "name": name}  # set state to outside since not at center

                            if previous_object_states[track_id] == "inside":
                                client.print(f"objects_inside: {objects_inside}")
                                client.print(f"[EVENT] REMOVED: {name} [{track_id}]")
                                await client.send_item_removed(name)
                                objects_inside[name] -= 1

                    previous_object_states[track_id] = object_states[track_id]["state"]

            
            if not initial_objects_counted:
                initial_objects_counted = True
                print("Initial total object counts:")
                for name, count in total_object_counts.items():
                    print(f"{name}: {count}")

            cv2.imshow("Tracking demo", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    # Print the final object counts
    print("Final total object counts:")
    for name, count in total_object_counts.items():
        print(f"{name}: {count}")
    print("Final objects inside count:")
    for name, count in objects_inside.items():
        print(f"{name}: {count}")