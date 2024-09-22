from webcface import Client

wcli = Client("tutorial-send")
wcli.wait_connection()

print("Hello, World! (sender)")

# "data" という名前のvalueデータとして100という値をセット
wcli.value("data").set(100)
# "message" という名前のtextデータとして "Hello World! (sender)" という文字列をセット
wcli.text("message").set("Hello, World! (sender)")

wcli.sync()  # データを送信します
