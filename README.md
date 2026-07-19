# AI Virtual Mouse: Gesture-Controlled HCI System

An intelligent Human-Computer Interaction (HCI) software application that tracks computer vision landmarker arrays via a standard webcam feed, translating hand gestures into desktop cursor actions (movement, clicking, and scrolling) without physical hardware touch.

Core Processing Pipeline
* **Frame Tracking & Input:** Captures high-definition frames through a live webcam interface.
* **Landmark Detection:** Utilizes real-time coordinate meshes to identify $21$ distinct skeletal points across the human hand.
* **Coordinate Mapping:** Maps tracking camera coordinates proportionally to native desktop screen pixels ($X, Y$) using scaling factor formulas.
* **Automation Automation Engine:** Injects system-level API triggers to control physical desktop mouse parameters.

 Implemented Gesture Command Schema
* **Cursor Navigation:** Trace the coordinate path of the Index Finger tip.
* **Left-Click Command:** Bring the Index Finger and Middle Finger tips close together (minimizing the geometric Euclidean distance between them).
* **Scrolling Mode:** Raise specific combination gestures to move active vertical page components up or down smoothly.

 Tech Stack & Dependencies
* **Language:** Python 3.x
* **Core Libraries:** `opencv-python` (Frame manipulation), `numpy` (Vector operations), `pyautogui` / `pynput` (OS cursor control injection)# VirtualMouseProject
