from webcface import Member, Value, Client
import time

wcli = Client("a")
v = wcli.value("fuga")

print(v.get())
v.set(12345)
print(v.get())


print(wcli.member("example_main").value("test").get_vec())
time.sleep(1)
wcli.sync()
time.sleep(1)
print(wcli.member("example_main").value("test").get_vec())

print(wcli.server_name)
print(wcli.server_version)
wcli.close()