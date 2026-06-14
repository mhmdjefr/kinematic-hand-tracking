# Vision Ninja 🍉🗡️

A computer vision-based action game inspired by Fruit Ninja, built using Python, OpenCV, and Google MediaPipe. This game tracks your index finger in real-time through the webcam, allowing you to slash falling fruits while avoiding bombs.

## Features
* **Real-time Hand Tracking:** Uses MediaPipe to precisely track hand landmarks.
* **Kinematic Slash Detection:** Calculates the Euclidean distance of the index finger between frames to detect high-speed slash motions.
* **Collision Detection:** Accurate hitboxes for falling objects using mathematical radius calculations.
* **Dynamic Object Spawning:** Randomly generates falling fruits and bombs with varying speeds.
* **Alpha Channel Support:** Transparent PNG overlay capabilities for seamless game assets integration.

## Tech Stack
* Python 3.10
* OpenCV (cv2)
* MediaPipe (Google)
* Numpy

## Prerequisites
It is highly recommended to run this project inside an isolated virtual environment (like Conda) to avoid dependency conflicts, especially on ARM64 architectures (Apple Silicon).

```bash
# Example Conda setup
conda create -n vision-env python=3.10
conda activate vision-env