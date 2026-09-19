"""
Hand Gesture Volume Control
---------------------------
Uses OpenCV (webcam) + MediaPipe (hand tracking) to change the system volume
based on the distance between your thumb tip and index fingertip.

    Fingers close together  -> volume 0%
    Fingers spread apart    -> volume 100%

Install:
    pip install opencv-python mediapipe numpy
    pip install pycaw comtypes        # Windows only

Run:
    python hand_volume_control.py

Press 'q' to quit.
"""

import math
import platform
import subprocess
import time

import cv2
import mediapipe as mp
import numpy as np

# ----------------------------- Configuration -----------------------------
CAM_INDEX = 0            # change if you have multiple cameras
FRAME_W, FRAME_H = 1280, 720
MIN_DIST = 30            # pixel distance that maps to 0% volume
MAX_DIST = 250           # pixel distance that maps to 100% volume
SMOOTHING = 0.25         # 0-1, lower = smoother but slower to react
DETECTION_CONF = 0.7
TRACKING_CONF = 0.7
# -------------------------------------------------------------------------

OS = platform.system()


# ------------------------- Cross-platform volume -------------------------
class VolumeController:
    """Sets the system master volume (0-100) on Windows, macOS and Linux."""

    def __init__(self):
        self._win_volume = None
        if OS == "Windows":
            from ctypes import POINTER, cast
            from comtypes import CLSCTX_ALL
            from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

            speakers = AudioUtilities.GetSpeakers()
            if hasattr(speakers, "EndpointVolume"):  # newer pycaw
                self._win_volume = speakers.EndpointVolume
            else:  # older pycaw
                interface = speakers.Activate(
                    IAudioEndpointVolume._iid_, CLSCTX_ALL, None
                )
                self._win_volume = cast(interface, POINTER(IAudioEndpointVolume))

    def set(self, percent: int):
        percent = int(max(0, min(100, percent)))
        if OS == "Windows":
            self._win_volume.SetMasterVolumeLevelScalar(percent / 100.0, None)
        elif OS == "Darwin":  # macOS
            subprocess.run(
                ["osascript", "-e", f"set volume output volume {percent}"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        else:  # Linux (ALSA / PulseAudio)
            subprocess.run(
                ["amixer", "-D", "pulse", "sset", "Master", f"{percent}%"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )


# ------------------------------- Main app --------------------------------
def main():
    volume = VolumeController()

    mp_hands = mp.solutions.hands
    mp_draw = mp.solutions.drawing_utils
    hands = mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=1,
        min_detection_confidence=DETECTION_CONF,
        min_tracking_confidence=TRACKING_CONF,
    )

    cap = cv2.VideoCapture(CAM_INDEX)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_W)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_H)
    if not cap.isOpened():
        raise RuntimeError("Could not open webcam. Check CAM_INDEX.")

    vol_percent = 0.0      # smoothed volume value
    last_sent = -1         # last volume actually applied
    prev_time = 0

    while True:
        ok, frame = cap.read()
        if not ok:
            break

        frame = cv2.flip(frame, 1)  # mirror view
        h, w, _ = frame.shape
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb)

        if results.multi_hand_landmarks:
            hand = results.multi_hand_landmarks[0]
            mp_draw.draw_landmarks(frame, hand, mp_hands.HAND_CONNECTIONS)

            # Landmark 4 = thumb tip, 8 = index fingertip
            x1, y1 = int(hand.landmark[4].x * w), int(hand.landmark[4].y * h)
            x2, y2 = int(hand.landmark[8].x * w), int(hand.landmark[8].y * h)
            cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

            # Draw the gesture
            cv2.circle(frame, (x1, y1), 10, (255, 0, 255), cv2.FILLED)
            cv2.circle(frame, (x2, y2), 10, (255, 0, 255), cv2.FILLED)
            cv2.line(frame, (x1, y1), (x2, y2), (255, 0, 255), 3)

            # Distance -> volume %
            dist = math.hypot(x2 - x1, y2 - y1)
            target = np.interp(dist, [MIN_DIST, MAX_DIST], [0, 100])

            # Exponential smoothing to reduce jitter
            vol_percent += (target - vol_percent) * SMOOTHING
            vol_int = int(round(vol_percent))

            # Only call the OS when the value actually changes
            if vol_int != last_sent:
                volume.set(vol_int)
                last_sent = vol_int

            # Visual feedback: green dot at minimum, red dot at maximum
            if dist <= MIN_DIST:
                cv2.circle(frame, (cx, cy), 12, (0, 255, 0), cv2.FILLED)
            elif dist >= MAX_DIST:
                cv2.circle(frame, (cx, cy), 12, (0, 0, 255), cv2.FILLED)
            else:
                cv2.circle(frame, (cx, cy), 12, (255, 0, 255), cv2.FILLED)

        # ---- Volume bar on the left ----
        bar_top, bar_bottom = 150, 400
        bar_y = int(np.interp(vol_percent, [0, 100], [bar_bottom, bar_top]))
        cv2.rectangle(frame, (50, bar_top), (85, bar_bottom), (0, 255, 0), 3)
        cv2.rectangle(frame, (50, bar_y), (85, bar_bottom), (0, 255, 0), cv2.FILLED)
        cv2.putText(frame, f"{int(round(vol_percent))} %", (40, 440),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        # ---- FPS ----
        now = time.time()
        fps = 1 / (now - prev_time) if prev_time else 0
        prev_time = now
        cv2.putText(frame, f"FPS: {int(fps)}", (40, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

        cv2.imshow("Hand Gesture Volume Control", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    hands.close()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
