from webcface import Client

wcli = Client("example_closing")
wcli.start()
wcli.value("value").set(100)
wcli.sync()
wcli.close()
