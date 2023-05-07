import json
import socket
from threading import Thread

from tkinter.messagebox import showinfo,askretrycancel

from .window import GameWindow

class OnlineConn:
    HOST = socket.gethostbyname(socket.gethostname())
    PORT = 10946
    def __init__(self,app):
        self.app = app
        self.client = socket.socket()
        self.can_online = False
        self.is_connecting = False # 是否正在连接服务器
        self.connect()

    def connect(self):
        if self.is_connecting:
            return
        def wrapper():
            self.is_connecting = True
            try:
                self.client.connect((OnlineConn.HOST,OnlineConn.PORT))
                self.can_online = True
            except ConnectionError:
                pass
            self.is_connecting = False
        Thread(target = wrapper).start()

    def check_connect(self):
        if not self.can_online:
            res = askretrycancel("提示","服务器连接失败，是否尝试重新连接？")
            if res:
                self.connect()
                showinfo("提示","正在重新连接，请稍后再试")
            return False
        return True

    def send(self,message):
        try:
            self.client.send(json.dumps(message).encode())
        except ConnectionError:
            self.can_online = False
            self.client = socket.socket()
            self.check_connect()

    def create(self):
        if not self.check_connect():
            return
        self.send(["create","amf"])

    def enter(self):
        if not self.check_connect():
            return
        pass

    def bind(self,window:GameWindow):
        pass
