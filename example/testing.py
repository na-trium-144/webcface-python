from webcface import Member, Value, Client
import time

wcli = Client("a")
v = wcli.value("fuga")

print(v.get())
v.set(12345)
print(v.get())


time.sleep(1)
wcli.sync()
time.sleep(1)

print(wcli.server_name)
print(wcli.server_version)