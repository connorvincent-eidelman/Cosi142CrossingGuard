import cv2
import numpy as np
from ultralytics import YOLO
import csv
import datetime
import subprocess
try:
    from moviepy.editor import VideoFileClip, AudioFileClip, CompositeAudioClip
except ImportError:
    print("MoviePy not available, audio will not be added to video")
    VideoFileClip = None

# Sound paths
lock_sound_path = '/System/Library/Sounds/Ping.aiff'
overtake_sound_path = '/System/Library/Sounds/Glass.aiff'
progress_sound_path = '/System/Library/Sounds/Pop.aiff'  # For progress milestones
car_detect_sound_path = '/System/Library/Sounds/Basso.aiff'  # For car detection
bus_detect_sound_path = '/System/Library/Sounds/Funk.aiff'  # For bus detection

# Preload audio clips
try:
    lock_clip = AudioFileClip(lock_sound_path)
    overtake_clip = AudioFileClip(overtake_sound_path)
    progress_clip = AudioFileClip(progress_sound_path)
    car_detect_clip = AudioFileClip(car_detect_sound_path)
    bus_detect_clip = AudioFileClip(bus_detect_sound_path)
    audio_clips_preloaded = True
except Exception as e:
    print(f"Error preloading audio clips: {e}")
    audio_clips_preloaded = False

# List to collect audio clips
audio_clips = []

# Track progress milestones played
progress_milestones = {25, 50, 75, 100}
played_milestones = set()

# Track if bus passed sound played
bus_passed_sound_played = False

# Preload audio clips
try:
    lock_clip = AudioFileClip(lock_sound_path)
    overtake_clip = AudioFileClip(overtake_sound_path)
    progress_clip = AudioFileClip(progress_sound_path)
    car_detect_clip = AudioFileClip(car_detect_sound_path)
    bus_detect_clip = AudioFileClip(bus_detect_sound_path)
    audio_clips_preloaded = True
except Exception as e:
    print(f"Error preloading audio clips: {e}")
    audio_clips_preloaded = False

# Load YOLO model
model = YOLO("yolov8n.pt")

video_path = "/Users/connorv-e/car_videos/video/videoplayback (1).mp4"
output_path = "/Users/connorv-e/car_videos/video/annotated_video.mp4"
data_log_path = "/Users/connorv-e/car_videos/overtake_data.csv"
overtake_log_path = "/Users/connorv-e/car_videos/overtake_events.csv"

# Setup CSV logging
csv_file = open(data_log_path, 'w', newline='')
csv_writer = csv.writer(csv_file)
csv_writer.writerow(['Timestamp', 'Frame', 'Time_Sec', 'Car_ID', 'Vertical_Dist', 'Horizontal_Dist', 'Distance_to_Bus', 'Line_Angle_Deg'])

# Setup overtake events CSV
overtake_csv_file = open(overtake_log_path, 'w', newline='')
overtake_csv_writer = csv.writer(overtake_csv_file)
overtake_csv_writer.writerow(['Timestamp', 'Frame', 'Time_Sec', 'Car_ID', 'Horizontal_Shift', 'Angle', 'Distance_Change'])

cap = cv2.VideoCapture(video_path)

fps = cap.get(cv2.CAP_PROP_FPS)
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

fourcc = cv2.VideoWriter_fourcc(*"mp4v")
out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

frame_count = 0
overtaken = False

# Store the locked car
target_car_id = None

# Track metrics history for motion/trend detection
metrics_history = {}  # {car_id: [(frame, dx, dy, dist, angle), ...]}

while cap.isOpened():

    ret, frame = cap.read()
    if not ret:
        break

    frame_count += 1

    results = model.track(frame, persist=True)

    bus_boxes = []
    car_boxes = []

    if results[0].boxes.id is not None:

        boxes = results[0].boxes.xyxy.cpu().numpy()
        ids = results[0].boxes.id.cpu().numpy()
        classes = results[0].boxes.cls.cpu().numpy()

        for box, track_id, cls in zip(boxes, ids, classes):

            x1, y1, x2, y2 = box.astype(int)
            cx = int((x1 + x2) / 2)
            cy = int((y1 + y2) / 2)

            # Bus
            if cls == 5:

                bus_boxes.append((cx, cy, x1, y1, x2, y2))

                cv2.rectangle(frame,(x1,y1),(x2,y2),(0,255,0),2)
                cv2.putText(frame,"Bus",(x1,y1-10),
                            cv2.FONT_HERSHEY_SIMPLEX,0.9,(0,255,0),2)
                # Record bus detection sound
                if audio_clips_preloaded:
                    audio_clips.append(bus_detect_clip.set_start(frame_count / fps))

            # Car
            if cls == 2:

                car_boxes.append((track_id, cx, cy, x1, y1, x2, y2))

                cv2.rectangle(frame,(x1,y1),(x2,y2),(255,0,0),2)
                cv2.putText(frame,f"Car {int(track_id)}",(x1,y1-10),
                            cv2.FONT_HERSHEY_SIMPLEX,0.9,(255,0,0),2)
                # Record car detection sound
                if audio_clips_preloaded:
                    audio_clips.append(car_detect_clip.set_start(frame_count / fps))

    # ----- OVERTAKE ANALYSIS -----

    if bus_boxes and car_boxes:

        bus_cx, bus_cy, bx1, by1, bx2, by2 = bus_boxes[0]

        # -------- LOCK ONTO CAR --------

        # -------- LOCK ONTO CAR (ONLY IF BEHIND BUS) --------

        if target_car_id is None:

            # Filter cars that are behind the bus
            cars_behind_bus = [car for car in car_boxes if car[2] > bus_cy]

            if len(cars_behind_bus) > 0:

                closest_car = min(
                    cars_behind_bus,
                    key=lambda c: np.sqrt((c[1]-bus_cx)**2 + (c[2]-bus_cy)**2)
                )

                target_car_id = closest_car[0]

                print(f"Locking onto Car ID {target_car_id}")
                # Record lock sound event
                if audio_clips_preloaded:
                    audio_clips.append(lock_clip.set_start(frame_count / fps))

        # -------- FIND LOCKED CAR --------

        locked_car = None

        for car in car_boxes:
            if car[0] == target_car_id:
                locked_car = car
                break

        # If lost, reset tracking
        if locked_car is None:
            target_car_id = None
            continue

        track_id, cx, cy, x1, y1, x2, y2 = locked_car

        # Highlight tracked car
        cv2.rectangle(frame,(x1,y1),(x2,y2),(0,165,255),3)

        cv2.putText(frame,
                    f"TRACKED CAR {int(track_id)}",
                    (x1, y1-35),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0,165,255),
                    2)

        # Draw line between bus and tracked car
        cv2.line(frame,(bus_cx,bus_cy),(cx,cy),(255,255,0),3)

        # Vertical distance
        vertical_distance = bus_cy - cy
        
        # Calculate line metrics for logging
        dx = cx - bus_cx
        dy = vertical_distance
        dist_to_bus = np.sqrt(dx**2 + dy**2)
        line_angle_deg = np.degrees(np.arctan2(dy, dx)) if dist_to_bus > 0 else 0
        
        # Log line data to CSV
        csv_writer.writerow([
            datetime.datetime.now().isoformat(),
            frame_count,
            frame_count / fps,
            int(track_id),
            f"{dy:.2f}",
            f"{dx:.2f}",
            f"{dist_to_bus:.2f}",
            f"{line_angle_deg:.2f}"
        ])

        cv2.putText(frame,
                    f"Vertical: {int(vertical_distance)}px | Horizontal: {int(dx)}px",
                    (20,40),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0,0,255),
                    2)
        
        cv2.putText(frame,
                    f"Angle: {line_angle_deg:.1f}° | Dist: {dist_to_bus:.1f}px",
                    (20,65),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (100,200,255),
                    2)

        # ----- PASS PROGRESS -----
        
        # Progress based on horizontal distance (the real overtake signal)
        max_horiz = 150
        progress = min(max(dx / max_horiz, 0), 1)
        percent = int(progress * 100)

        # Check for progress milestones
        for milestone in progress_milestones:
            if percent >= milestone and milestone not in played_milestones:
                if audio_clips_preloaded:
                    audio_clips.append(progress_clip.set_start(frame_count / fps))
                played_milestones.add(milestone)

        cv2.putText(frame,
                    f"Lateral Progress: {percent}%",
                    (20,90),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (255,255,255),
                    2)

        # Draw progress bar
        bar_x = 20
        bar_y = 110
        bar_w = 200
        bar_h = 15

        cv2.rectangle(frame,(bar_x,bar_y),(bar_x+bar_w,bar_y+bar_h),(255,255,255),2)
        cv2.rectangle(frame,
                      (bar_x,bar_y),
                      (bar_x + int(bar_w*progress), bar_y+bar_h),
                      (0,255,0) if not overtaken else (0,0,255),
                      -1)

        # ----- OVERTAKE DETECTION (TREND-BASED) -----
        
        # Initialize history for this car if needed
        if track_id not in metrics_history:
            metrics_history[track_id] = []
        
        # Store current metrics
        metrics_history[track_id].append({
            'frame': frame_count,
            'dx': dx,
            'dy': dy,
            'dist': dist_to_bus,
            'angle': line_angle_deg
        })
        
        # Keep only last 30 frames worth of history (~1 second at 30fps)
        if len(metrics_history[track_id]) > 30:
            metrics_history[track_id].pop(0)
        
        # Check overtake conditions
        if not overtaken and len(metrics_history[track_id]) >= 10:
            
            current = metrics_history[track_id][-1]
            history_start = metrics_history[track_id][0]
            
            # Condition 1: Horizontal distance has increased significantly
            dx_change = current['dx'] - history_start['dx']
            
            # Condition 2: Line angle is becoming more horizontal (toward 0°)
            current_angle = current['angle']
            
            # Condition 3: Distance to bus is increasing (car moving farther away)
            dist_increasing = current['dist'] > history_start['dist']
            
            # Overtake signature: large horizontal movement + horizontal angle + increasing distance
            if dx_change > 40 and current_angle > -20 and dist_increasing:
                
                overtaken = True
                time_sec = frame_count / fps
                
                # Log overtake event
                overtake_csv_writer.writerow([
                    datetime.datetime.now().isoformat(),
                    frame_count,
                    time_sec,
                    int(track_id),
                    dx_change,
                    current_angle,
                    current['dist'] - history_start['dist']
                ])
                
                print(
                    f"✓ OVERTAKE DETECTED by car {int(track_id)} "
                    f"at frame {frame_count} ({time_sec:.2f}s)"
                )
                print(
                    f"  Horizontal shift: {dx_change:.1f}px | "
                    f"Angle: {current_angle:.1f}° | "
                    f"Distance: {history_start['dist']:.1f}→{current['dist']:.1f}px"
                )
                # Record overtake sound event
                if audio_clips_preloaded:
                    audio_clips.append(overtake_clip.set_start(time_sec))

        # ----- DISPLAY ALERT -----

        if overtaken and not bus_passed_sound_played:
            if audio_clips_preloaded:
                audio_clips.append(overtake_clip.set_start(frame_count / fps))  # Reuse overtake sound for bus passed
            bus_passed_sound_played = True

        if overtaken:

            cv2.putText(frame,
                        "BUS PASSED",
                        (width//2 - 200,150),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        2,
                        (0,0,255),
                        5)

    out.write(frame)

cap.release()
out.release()
csv_file.close()
overtake_csv_file.close()

# Add audio to the video
if VideoFileClip is not None:
    print("Adding audio to video...")
    video = VideoFileClip(output_path)
    if audio_clips:
        composite_audio = CompositeAudioClip(audio_clips)
        video = video.set_audio(composite_audio)

    output_with_audio = output_path.replace('.mp4', '_with_audio.mp4')
    video.write_videofile(output_with_audio, codec='libx264', audio_codec='aac')

    print("Annotated video with audio saved to:", output_with_audio)
else:
    print("Annotated video saved to:", output_path)

print(f"Line data logged to: {data_log_path}")
print(f"Overtake events logged to: {overtake_log_path}")

if not overtaken:
    print("No overtaking detected")