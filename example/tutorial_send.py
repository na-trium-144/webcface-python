from webcface import Client
import time

wcli = Client("tutorial-send")


@wcli.func("hoge")
def hoge() -> int:
    print("Function hoge started")
    return 42


@wcli.func("fuga")
def fuga(a: int, b: str) -> int:
    print(f"Function fuga({a}, {b}) started")
    return a


wcli.wait_connection()

print("Hello, World! (sender)")

# "data" という名前のvalueデータとして100という値をセット
wcli.value("data").set(100)
# "message" という名前のtextデータとして "Hello World! (sender)" という文字列をセット
wcli.text("message").set("Hello, World! (sender)")

wcli.sync()  # データを送信します

while True:
    wcli.sync()
    time.sleep(1)
