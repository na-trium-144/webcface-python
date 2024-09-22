from webcface import Client, Value, Text, Promise
import time

wcli = Client("tutorial-recv")
wcli.wait_connection()

print("Hello, World! (receiver)")

sender = wcli.member("tutorial-send")


@sender.value("data").on_change
def on_data_change(v: Value):
    print(f"data changed: {v.get()}")


@sender.text("message").on_change
def on_message_change(t: Text):
    print(f"message changed: {t}")


while True:
    # tutorial-send の "hoge" という関数を呼び出します
    hoge_p = sender.func("hoge").run_async()

    @hoge_p.on_finish
    def on_hoge_finish(hoge_p: Promise):
        # hoge_p が完了したとき、結果を表示します
        if hoge_p.is_error:
            print(f"Error in hoge(): {hoge_p.rejection}")
        else:
            print(f"hoge() = {hoge_p.response}")

    fuga_p = sender.func("fuga").run_async(123, "abc")

    @fuga_p.on_finish
    def on_fuga_finish(fuga_p: Promise):
        # fuga_p が完了したとき、結果を表示します
        if fuga_p.is_error:
            print(f"Error in fuga(): {fuga_p.rejection}")
        else:
            print(f"fuga() = {fuga_p.response}")

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
