
# AI Job Hunt - Capstone Project

This repository contains the full-stack application for our Oregon State University CS 467 Capstone project.  
It is built with a React (Vite) frontend and a Python backend.  

## Getting Started

### Prerequisites  

Node.js (v18 or higher)  
Python (v3.9 or higher)  
Git  

### Initial Setup (First Time Only)

#### 1. Backend Setup

Navigate to the backend directory:  
```
cd backend
```
Create a virtual environment:  
> (If python doesn't work, try using python3.)  
```
python -m venv venv
```
Activate the virtual environment:  
```
# Windows
.\venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

Install dependencies:  
```
pip install -r requirements.txt
```
Start the backend server:  
```
cd ../
uvicorn backend.main:app --reload
```

#### 2. Frontend Setup  
Open a new terminal and navigate to the frontend directory:  
```
cd frontend
```
Install dependencies:  
```
npm install
```
Start the development server:  
```
npm run dev
```
Open your browser to the URL provided in the terminal (usually http://localhost:5173).  

### Quick Start (after initial setup)

Use these commands for daily development to get everything running.  

#### **Step A: Start the Backend**  
1.  Open a terminal and navigate to `/backend`.  
2.  **Activate the Environment:**  
    * **Windows:** `.\venv\Scripts\activate`  
    * **Mac/Linux:** `source venv/bin/activate`  
3.  **Run the API:**  
    * `uvicorn main:app --reload` (or your chosen server command)  

#### **Step B: Start the Frontend**  
1.  Open a **second** terminal window and navigate to `/frontend`.  
2.  **Run the App:**  
    * `npm run dev`  
3.  Open `http://localhost:5173` in your browser.  

## Tech Stack

Frontend: React.js, Vite  
Backend: Python, FastAPI  
Database: MongoDB  

## Contribution Guidelines
To maintain code quality and ensure the main branch stays stable, please follow these rules:  

Branching: Create a new branch for every feature or fix (git checkout -b feature-name).  

Pull Requests: All code must be merged via a Pull Request (PR).  

Code Reviews: At least one other team member must review and approve a PR before it can be merged into main.  

Local Testing: Ensure both the frontend and backend run locally without errors before submitting a PR.  

## Developer Notes  

### Adding New Dependencies  

* **If you install a Python package:** Run `pip freeze > requirements.txt` so others can update their environment.  
* **If you install a Node package:** Simply commit the updated `package.json` and `package-lock.json`.
  
API Proxy: The frontend is configured to proxy /api requests to `http://127.0.0.1:8000.`  
