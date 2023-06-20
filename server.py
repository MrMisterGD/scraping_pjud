from flask import Flask
from app.init import app
from app.controllers.recas import *
from twisted.internet import reactor
import threading

if __name__ == "__main__":
    reactor_thread = threading.Thread(target=reactor.run, kwargs={'installSignalHandlers': False})
    reactor_thread.start()
    app.run(host='0.0.0.0', port=8084, debug=True, use_reloader=False)
    reactor_thread.join()