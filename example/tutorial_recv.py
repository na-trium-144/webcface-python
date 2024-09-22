from webcface import Client
import time

wcli = Client("tutorial-recv")
wcli.wait_connection()

print("Hello, World! (receiver)")

while True:
    # "tutorial-send" が送信している "data" という名前のvalueデータをリクエスト&取得
    data = wcli.member("tutorial-send").value("data").try_get()
    if data is not None:
        # 送信されたデータがあれば取得できるはず
        print(f"data = {data}")
    else:
        # まだなにも送信されていない
        print("data is None")

    # "tutorial-send" が送信している "message" という名前のtextデータをリクエスト&取得
    message = wcli.member("tutorial-send").text("message").try_get()
    if message is not None:
        print(f"message = {message}")
    else:
        print("message is None")

    wcli.sync()  # データを受信します
    time.sleep(1)
