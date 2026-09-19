# Hand Gesture Volume Control

Control your computer's volume with a pinch of your fingers. This project uses **OpenCV** to read your webcam and **MediaPipe** to track your hand, then maps the distance between your thumb and index finger to the system volume.

<!-- Add a demo GIF or screenshot here, e.g. ![Demo](demo.gif) -->

## Features

- Real-time hand tracking through your webcam
- Volume control by changing the distance between thumb and index fingertip
- On-screen volume bar and FPS counter
- Smoothing to reduce jitter
- Works on Windows, macOS and Linux

## How It Works

1. OpenCV captures frames from the webcam.
2. MediaPipe detects 21 hand landmarks in each frame.
3. The script measures the distance between the thumb tip (landmark 4) and index fingertip (landmark 8).
4. That distance is mapped to a 0-100% volume level and applied to the system volume.

Fingers together means 0%, and fingers fully apart means 100%.

## Requirements

- Python 3.8 - 3.11
- A webcam
- Windows, macOS or Linux

## Installation

```bash
git clone https://github.com/YOUR-USERNAME/hand-gesture-volume-control.git
cd hand-gesture-volume-control
pip install -r requirements.txt
```

## Usage

```bash
python hand_volume_control.py
```

- Hold your hand in front of the webcam.
- Move your thumb and index finger closer together or further apart to change the volume.
- Press **q** to quit.

## Configuration

These values are at the top of `hand_volume_control.py`:

| Setting | Default | Description |
|---|---|---|
| `CAM_INDEX` | `0` | Which camera to use |
| `MIN_DIST` | `30` | Pixel distance that maps to 0% volume |
| `MAX_DIST` | `250` | Pixel distance that maps to 100% volume |
| `SMOOTHING` | `0.25` | Lower is smoother but slower to react |

## Platform Notes

| OS | Volume backend |
|---|---|
| Windows | [pycaw](https://github.com/AndreMiras/pycaw) |
| macOS | `osascript` (built in) |
| Linux | `amixer` (ALSA / PulseAudio) |

## Troubleshooting

- **Camera doesn't open:** Change `CAM_INDEX` to `1` or `2`, and make sure no other app is using the webcam.
- **Volume doesn't reach 0% or 100%:** Adjust `MIN_DIST` and `MAX_DIST` to suit your camera and distance from it.
- **Volume jumps around:** Lower `SMOOTHING` and make sure your hand is well lit.
- **`mp.solutions` error:** Install a compatible MediaPipe version with `pip install mediapipe==0.10.14`.
- **Linux, no volume change:** Check that `amixer` is installed (`sudo apt install alsa-utils`).

## Built With

- [OpenCV](https://opencv.org/)
- [MediaPipe](https://developers.google.com/mediapipe)
- [NumPy](https://numpy.org/)
- [pycaw](https://github.com/AndreMiras/pycaw) (Windows)

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
