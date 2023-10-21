from webcface import Member, Value
from webcface.client_data import ClientData
from webcface.field import Field

data = ClientData("a")
m = Member(Field(data, ""), "a")
v = m.value("fuga")

print(v.get())
v.set(12345)
print(v.get())