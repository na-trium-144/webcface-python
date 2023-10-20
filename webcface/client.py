import threading
import websocket
import time


class Client:
    def __init__(self, name: str = "", host: str = "127.0.0.1", port: int = 7530):
        self.name = name
        self.host = host
        self.port = port
        self.ws = None

        def on_open(ws):
            print("open")

        def on_message(ws, message):
            print("message")

        def on_error(ws, error):
            print(error)

        def on_close(ws, close_status_code, close_msg):
            print("closed")

        def reconnect():
            while True:
                self.ws = websocket.WebSocketApp(
                    f"ws://{host}:{port}/",
                    on_open=on_open,
                    on_message=on_message,
                    on_error=on_error,
                    on_close=on_close,
                )
                try:
                    self.ws.run_forever()
                except Exception as e:
                    print(e)
                time.sleep(1)

        self.ws_thread = threading.Thread(target=reconnect)
        self.ws_thread.start()
