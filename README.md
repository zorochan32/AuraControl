# AuraControl ✨

[![Python Version][python-shield]][python-url]
[![License: MIT][license-shield]][license-url]

**Control your PC and games using nothing but your hands and voice.**

AuraControl is a Python-based application that uses your webcam to translate real-time hand gestures and voice commands into keyboard and mouse inputs, creating a futuristic, hands-free way to interact with your computer.

<br>

<p align="center">
  <!-- IMPORTANT: Replace this with the URL to the logo you created! -->
  <img src="https://imgur.com/a/u81wAgQ" alt="AuraControl Logo" width="200"/>
</p>

<br>

---



## 🚀 About The Project

AuraControl was born from the idea of creating a more immersive and intuitive way to control games, **with a primary focus on *Minecraft***. Standard keyboard and mouse controls are functional, but what if you could move, jump, and build just by gesturing? This project makes that a reality.

By leveraging the power of computer vision, this application maps a comprehensive set of hand gestures to in-game actions, providing a unique and engaging hands-free experience. The entire system is wrapped in a modern, clean, and user-friendly interface built with CustomTkinter.

### Core Technologies
*   **Python:** The backbone of the project.
*   **OpenCV:** For capturing and processing the live video feed from the webcam.
*   **MediaPipe:** Google's powerful library for high-fidelity, real-time hand and landmark detection.
*   **pydirectinput:** For sending low-level keyboard and mouse inputs, ensuring maximum compatibility with games that require DirectInput.
*   **CustomTkinter:** To create the beautiful and modern graphical user interface (GUI).
*   **SpeechRecognition:** For optional voice command integration.

---

## 📋 Features

*   **Real-time Gesture Control:** Translates hand movements into actions with minimal latency, perfect for gaming.
*   **Stateful Input System:** Correctly handles both "press" (e.g., jump) and "hold" (e.g., walk forward, mine) commands, just like a physical controller.
*   **Intuitive Camera Movement:** Features a configurable dead-zone and smooth tracking for natural and precise camera control.
*   **User-Friendly GUI:** A sleek, dark-mode interface to start/stop the controller, select devices, and toggle features on the fly.
*   **Automatic Device Detection:** Automatically finds and lists all available cameras and microphones, letting you choose the right one.
*   **Configurable Camera View:** Includes a "Mirror Mode" to ensure controls feel natural, regardless of your camera's default settings.

---

## 🏁 Getting Started

Follow these simple steps to get a local copy up and running.

### Prerequisites

*   Python 3.9+
*   A webcam connected to your PC.
*   An internet connection for the initial dependency installation.

### Installation & Usage

1.  **Clone the Repository:**
    ```sh
    git clone https://github.com/zorochan32/AuraControl.git
    cd AuraControl
    ```

2.  **Create and Activate a Virtual Environment:**
    *   This is a crucial step to keep project dependencies isolated.
    ```sh
    # On Windows
    python -m venv venv
    .\venv\Scripts\activate
    ```

3.  **Install Dependencies:**
    *   A `requirements.txt` file is included for your convenience.
    ```sh
    pip install -r requirements.txt
    ```

4.  **Run the Application:**
    *   **IMPORTANT:** To control games, the application must run with administrator privileges.
    *   Right-click your `Command Prompt` or `PowerShell`, select **"Run as administrator"**.
    *   In the administrator terminal, navigate to the project's `src` folder and run the main script:
    ```cmd
    # Inside the administrator terminal, after activating the venv:
    cd src
    python gui_main.py
    ```
5.  **Configure and Play!**
    *   In the AuraControl window, select your desired Camera and Microphone.
    *   Toggle any settings you need (like Mirror Mode).
    *   Click **Start**, switch to your game, and enjoy!

---

## ⚠️ Important Notices

### Beta Software
Please be aware that AuraControl is currently in a **beta stage**. It is fully functional for its primary purpose, but you may encounter bugs. Feedback and contributions are highly encouraged!

### Game Compatibility
> **This version is primarily optimized for *Minecraft* (Java & Bedrock editions).**

The gestures, key bindings (W, A, S, D, E, Space, Ctrl), and camera sensitivity have been fine-tuned for a standard Minecraft control scheme. While it may function with other first-person games that share similar controls, **unexpected behavior or bugs may occur.** Future versions may include user-configurable control profiles for other games.

### Administrator Access & Security
AuraControl requires administrator privileges for **one reason only**: to reliably send keyboard and mouse inputs to applications running at a higher privilege level, such as games in fullscreen mode. This is a technical requirement for the `pydirectinput` library to function correctly.

**Your security is paramount.** The administrator requirement is **not** used for accessing your files, personal data, or network. The application is completely offline and self-contained. **The entire source code is available in this repository for you to review and verify its safety.** We believe in full transparency.

---
## 🧠 How It Works

AuraControl uses MediaPipe to track hand landmarks in real time.
These landmarks are translated into gestures, which are then mapped
to keyboard and mouse inputs using low-level system hooks.

---

## 🖐️ Gesture Guide

| Hand        | Gesture                                | Action                                   |
| :---------- | :------------------------------------- | :--------------------------------------- |
| **Right** | Move hand across the screen            | **Rotate Camera**                        |
| **Right** | All 5 fingers open 🖐️                 | **Move Forward** (Hold W)                |
| **Right** | Thumb pointing left                    | **Strafe Left** (Hold A)                 |
| **Right** | Thumb pointing right                   | **Strafe Right** (Hold D)                |
| **Right** | Thumbs Up 👍                           | **Jump** (Press Space)                   |
| **Right** | Thumbs Down 👎                         | **Crouch** (Hold Ctrl)                   |
| **Left**    | Fist (all fingers closed) ✊         | **Hold Left Mouse Button** (Mine/Attack) |
| **Left**    | Pointing finger up 👆                | **Hold Right Mouse Button** (Use/Block)  |
| **Left**    | Victory sign ✌️                       | **Open Inventory** (Press E)             |

---

## 🛣️ Future Roadmap

*   [ ] Create user-configurable profiles for different games.
*   [ ] Add a GUI element to remap gestures to different keys.
*   [ ] Implement gesture sequences for more complex actions (e.g., "crafting").
*   [ ] Explore full body tracking for even more immersive control.

---

## 📜 License

Distributed under the MIT License. See `LICENSE.md` for more information.

---

<!-- Markdown link & image variables -->
[license-shield]: https://img.shields.io/github/license/zorochan32/AuraControl.svg?style=for-the-badge
[license-url]: https://github.com/zorochan32/AuraControl/blob/main/LICENSE.md
[python-shield]: https://img.shields.io/badge/Python-3.9+-blue.svg?style=for-the-badge
[python-url]: https://www.python.org/
