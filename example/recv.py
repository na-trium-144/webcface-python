import time
from webcface import Client, Member, Value, Text, Func, Log

wcli = Client("example_recv")

@wcli.on_member_entry.connect
def member_entry(m: Member) -> None:
    print(f"Member Entry {m.name}")

    # todo: なぜかイベントが機能してない
    @m.on_value_entry.connect
    def value_entry(v: Value) -> None:
        print(f"Value Entry {v.name}")

    @m.on_text_entry.connect
    def text_entry(v: Text) -> None:
        print(f"Text Entry {v.name}")

    @m.on_func_entry.connect
    def func_entry(v: Func) -> None:
        print(f"Func Entry {v.name} args={v.args}")

    @m.log().signal.connect
    def log_append(v: Log) -> None:
        for l in v.get():
            print(f"Log {l.level}: {l.message}")
        v.clear()

    print("aaaa")


wcli.start()

while True:
    time.sleep(1)
    main = wcli.member("example_main")
    print(f"example_main.test = {main.value('test')}")
    main.func("func1").run_async()
    result = main.func("func2").run_async(9, 7.1, False, "")
    try:
        print(f"func2(9, 7.1, False, '') = {result.result}")
    except Exception as e:
        print(e)
