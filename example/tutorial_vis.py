from webcface import Client, Arg, view_components
import sys
import time


def hoge() -> int:
    print("Function hoge started")
    return 42


def fuga(a: int, b: str) -> int:
    print(f"Function fuga({a}, {b}) started")
    return a


wcli = Client("tutorial")
wcli.func("hoge").set(hoge)
wcli.func("fuga").set(
    fuga,
    args=[
        Arg(init=100),
        Arg(option=["foo", "bar", "baz"]),
    ],
)
sys.stdout = wcli.logging_io
wcli.wait_connection()

print("Hello, World!")

i = 0

while True:
    i += 1
    wcli.value("hoge").set(i)  # 「hoge」という名前のvalueに値をセット
    if i % 2 == 0:
        wcli.text("fuga").set("even")  # 「fuga」という名前のtextに文字列をセット
    else:
        wcli.text("fuga").set("odd")

    with wcli.view("sample") as v:
        v.add("Hello, world!\n")  # テキスト表示
        v.add("i = ", i, "\n")
        # ↑ v.add("i = ") と v.add(i) をするのと同じ
        v.add(view_components.button("hoge", hoge))  # ボタン
        # ref_str = InputRef()
        # v.add(view_components.text_input("str", bind=ref_str))  # 文字列入力
        # v.add(
        #     view_components.button(
        #         "print",
        #         # クリックすると、入力した文字列を表示
        #         lambda: print(f"str = {ref_str.as_str()}"),
        #     )
        # )
        v.add("\n")
    # withを抜けると、ここまでにvに追加したものがwcliに反映される

    wcli.sync()  # wcli に書き込んだデータを送信する (繰り返し呼ぶ必要がある)
    time.sleep(1)
