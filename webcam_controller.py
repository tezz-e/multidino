import cv2
import mediapipe as mp
import serial
import time
import sys
import math

# Configuration
COM_PORT = 'COM12'
BAUD_RATE = 115200
PINCH_THRESHOLD = 0.08      # Distance threshold (normalized). Below = pinched, Above = open.
COOLDOWN_FRAMES = 15        # Prevent double-jumping instantly

# Initialize Serial
try:
    ser = serial.Serial(
        port=COM_PORT, 
        baudrate=BAUD_RATE, 
        timeout=0, 
        write_timeout=0.1,
        xonxoff=False,
        rtscts=False,
        dsrdtr=False
    )
    # ESP32-S3 Native USB CDC requires DTR to be True to accept data!
    ser.setDTR(True)
    ser.setRTS(True)
    print(f"Connected to ESP32 on {COM_PORT}")
except Exception as e:
    print(f"\n[ERROR] Failed to connect to {COM_PORT}.")
    print("Please make sure the ESP32 is plugged in and you close the Arduino Serial Monitor!")
    print(e)
    ser = None

# Modern MediaPipe Tasks API
BaseOptions = mp.tasks.BaseOptions
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

options = HandLandmarkerOptions(
    base_options=BaseOptions(model_asset_path='hand_landmarker.task'),
    running_mode=VisionRunningMode.VIDEO,
    num_hands=1
)

# Start Video Capture
cap = cv2.VideoCapture(0)

# State
is_pinched = False
cooldown_counter = 0

print("\n" + "="*40)
print("DINO-DUEL WEBCAM CONTROLLER ACTIVE!")
print("Hold THUMB and INDEX together (pinch) normally.")
print("Raise your INDEX finger (open pinch) to JUMP!")
print("Press 'q' in the camera window to quit.")
print("="*40 + "\n")

# Use with block to automatically clean up the model resources
with HandLandmarker.create_from_options(options) as landmarker:
    frame_timestamp_ms = 0
    
    while cap.isOpened():
        success, image = cap.read()
        if not success:
            continue

        frame_timestamp_ms += int(1000 / 30) # approx 30 fps increments
        
        # Flip image horizontally for a selfie-view display
        image = cv2.flip(image, 1)
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Convert to MediaPipe Image format
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image_rgb)
        
        # Run hand landmarker
        hand_landmarker_result = landmarker.detect_for_video(mp_image, frame_timestamp_ms)
        
        if hand_landmarker_result.hand_landmarks:
            for hand_landmarks in hand_landmarker_result.hand_landmarks:
                # Thumb tip is index 4, Index tip is index 8
                thumb_tip = hand_landmarks[4]
                index_tip = hand_landmarks[8]
                
                # Calculate 3D Euclidean distance (normalized 0.0 to 1.0)
                dx = thumb_tip.x - index_tip.x
                dy = thumb_tip.y - index_tip.y
                dz = thumb_tip.z - index_tip.z
                distance = math.sqrt(dx*dx + dy*dy + dz*dz)
                
                # Draw visual line between thumb and index
                h, w, c = image.shape
                tx, ty = int(thumb_tip.x * w), int(thumb_tip.y * h)
                ix, iy = int(index_tip.x * w), int(index_tip.y * h)
                
                color = (0, 255, 0) # Green = Pinched (Down)
                
                if cooldown_counter > 0:
                    cooldown_counter -= 1
                    
                # State Machine Logic
                if distance < PINCH_THRESHOLD:
                    # Fingers are pinched
                    is_pinched = True
                elif distance > PINCH_THRESHOLD + 0.02: # 0.02 hysteresis to prevent flickering
                    # Fingers are open
                    color = (0, 0, 255) # Red = Open (Jump)
                    
                    if is_pinched and cooldown_counter == 0:
                        # We just opened the pinch!
                        print(f"JUMP! (dist={distance:.3f})")
                        if ser:
                            try:
                                ser.write(b'J')
                            except serial.SerialTimeoutException:
                                pass # Ignore if the write buffer is full
                        cooldown_counter = COOLDOWN_FRAMES
                        is_pinched = False
                elif not is_pinched:
                    # In between threshold but previously open
                    color = (0, 0, 255)
                    
                # Draw the UI
                cv2.circle(image, (tx, ty), 8, color, -1)
                cv2.circle(image, (ix, iy), 8, color, -1)
                cv2.line(image, (tx, ty), (ix, iy), color, 3)
                
                cv2.putText(image, f"Dist: {distance:.3f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

        cv2.imshow('Dino-Duel Webcam Controller', image)
        if cv2.waitKey(5) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()
if ser:
    ser.close()
