import json
import pickle
from random import random

import uvicorn
from sklearn.ensemble import RandomForestClassifier
from fastapi import FastAPI
import datetime
import time
from starlette.middleware.cors import CORSMiddleware
from URLAnalysis import generate_data_set
from starlette.websockets import WebSocket, WebSocketDisconnect

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # can alter with time
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

model = pickle.load(open('final_model.pkl', 'rb'))

connected_clients = set()


def save_to_history(year, month, day, hour, minute, url, type):
    with open("history.txt", "a") as file:
        file.write(f"{year}|{month}|{day}|{hour}|{minute}|{url}|{type}\n")


def get_time_ago(timestamp):
    now = time.time()
    diff = now - timestamp

    if diff < 60:
        return "just now"
    elif diff < 3600:
        return f"{int(diff // 60)} minutes ago"
    elif diff < 86400:
        return f"{int(diff // 3600)} hours ago"
    elif diff < 2592000:
        return f"{int(diff // 86400)} days ago"
    elif diff < 31536000:
        return f"{int(diff // 2592000)} months ago"
    else:
        return f"{int(diff // 31536000)} years ago"


def get_recent_history():
    with open("history.txt", "r") as file:
        lines = file.readlines()[-6:]
    history = []
    for line in lines:
        parts = line.strip().split("|")
        timestamp = datetime.datetime(int(parts[0]), int(parts[1]), int(parts[2]), int(parts[3]),
                                      int(parts[4])).timestamp()
        history.append({
            "time": get_time_ago(timestamp),
            "url": parts[5],
            "type": parts[6]
        })
    return history


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


@app.get("/api/getTable")
async def get_table():
    recent_history = get_recent_history()
    return recent_history


@app.get("/predict/")
async def predict(url: str):
    sample = [generate_data_set(url)]
    print(sample)
    probability = model.predict_proba(sample)[0]
    print(probability)
    pred = "PHISHING" if probability[0] > 0.5 else "LEGITIMATE"
    now = datetime.datetime.now()
    save_to_history(now.year, now.month, now.day, now.hour, now.minute, url, pred)
    timestamp = datetime.datetime(now.year, now.month, now.day, now.hour,
                                  now.minute).timestamp()
    recent_history = {
        "time": get_time_ago(timestamp),
        "url": url,
        "type": pred
    }
    for client in connected_clients:
        try:
            await client.send_text(json.dumps(recent_history))
        except WebSocketDisconnect:
            connected_clients.remove(client)
    return {"percent": int(probability[1] * 100),
            "predict": pred}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.add(websocket)
    try:
        while True:
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        connected_clients.remove(websocket)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)