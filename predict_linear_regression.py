import websocket
import json
import threading
import time
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

# Global variables
price_data = []
MAX_DATA_POINTS = 100

def on_message(ws, message):
    global price_data
    json_message = json.loads(message)
    price = float(json_message['p'])
    timestamp = int(json_message['E'])
    price_data.append({'timestamp': timestamp, 'price': price})

    if len(price_data) > MAX_DATA_POINTS:
        price_data.pop(0)

def on_error(ws, error):
    print(error)

def on_close(ws):
    print("### Connection closed ###")

def on_open(ws):
    print("### Connection opened ###")

def start_websocket():
    ws = websocket.WebSocketApp("wss://stream.binance.com:9443/ws/btcusdt@trade",
                                on_open=on_open,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    ws.run_forever()

def predict_prices():
    while len(price_data) < 10:
        print("Not enough data to make predictions. Collected data points: "+str(len(price_data)))
        time.sleep(3)

    df = pd.DataFrame(price_data)
    df['relative_time'] = (df['timestamp'] - df['timestamp'].iloc[-1]) / 1000.0

    X = df['relative_time'].values.reshape(-1, 1)
    y = df['price'].values

    model = LinearRegression()
    model.fit(X, y)

    future_times = np.array([0.1, 30, 60, 120])  # seconds into the future
    future_X = future_times.reshape(-1, 1)
    predictions = model.predict(future_X)

    print("\nPredictions:")
    for t, price in zip(future_times, predictions):
        if price > predictions[0]:
            print(f"Predicted price in %d seconds: %.2f (>)" % (t, price))
        else:
            print(f"Predicted price in %d seconds: %.2f (<)" % (t, price))

def schedule_predictions():
    while True:
        #time.sleep(15)
        predict_prices()
        input()


if __name__ == "__main__":
    # Start WebSocket thread
    ws_thread = threading.Thread(target=start_websocket)
    ws_thread.start()

    # Start Prediction thread
    prediction_thread = threading.Thread(target=schedule_predictions)
    prediction_thread.start()
