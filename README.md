
# 1v1 Real-Time Rock Paper Scissors 🎮

A fast-paced, real-time multiplayer Rock, Paper, Scissors web game. Built from scratch using Python, Flask, and WebSockets to ensure instant state synchronization between players without page refreshes.

## ✨ Features

* **Real-Time Multiplayer:** Instant gameplay powered by WebSockets (`Flask-SocketIO`).
* **Custom Game Modes:** * Best of 3 / Best of 5 Rounds
  * 60s / 120s Timed Free Play
* **Seamless Game Loop:** Automatic 3-second round transitions keep the action moving without requiring manual "Ready Up" clicks.
* **Polished UI/UX:** * Modern dark-mode interface with CSS transitions.
  * Dynamic scoreboard and timer synchronization.
* **Immersive FX:** * Audio cues for selecting, winning, losing, and tying.
  * Victory confetti (`canvas-confetti`) and screen-shake/red-flash effects for losses.

## 🛠️ Tech Stack

* **Frontend:** Vanilla HTML5, CSS3, JavaScript
* **Backend:** Python 3, Flask
* **WebSockets:** Flask-SocketIO, Socket.IO client
* **Server / Production Worker:** Gunicorn, Eventlet
* **Deployment:** Render

## 🚀 Local Development Setup

To run this project locally, clone the repository and set up the environment.

**1. Clone the repository:**

```bash
git clone [https://github.com/yourusername/rps-game.git](https://github.com/yourusername/rps-game.git)
cd rps-game

**2. Create and activate a virtual environment:**

**Bash**

```

uv venv
source .venv/bin/activate

```

**3. Install dependencies:**

**Bash**

```

uv pip install flask flask-socketio eventlet gunicorn

```

**4. Run the development server:**

**Bash**

```

python app.py

```

**5. Play:**

Open `http://localhost:5000` in two separate browser windows (or one normal and one incognito), enter the same room code, and start playing!

## ☁️ Deployment

This app is configured for easy deployment on platforms that support persistent WebSocket connections, such as  **Render** .

1. Connect your GitHub repository to a new Render Web Service.
2. Set the Build Command: `pip install -r requirements.txt`
3. Set the Start Command: `gunicorn -k eventlet -w 1 app:app`

*(Note: On Render's Free Tier, the application will sleep after 15 minutes of inactivity. The first request after a sleep period may take ~50 seconds to wake the server).*

```
