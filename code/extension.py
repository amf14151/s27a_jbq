import os
import shutil

from tkinter.messagebox import askyesno

from .static import ARR

class ExtAPI:
    def __init__(self,app):
        self.app = app

    @property
    def rl(self):
        return self.app.map_data.rl

    @property
    def cl(self):
        return self.app.map_data.cl

    def get_arr_by_rd(self,arr:ARR,r:int,d:int):
        return self.app.map_data.get_arr_by_rd(arr,r,d)

    def get_chess_by_arr(self,arr:ARR):
        return self.app.map_data.chessboard[arr[0]][arr[1]]

    def get_chess_arr_by_id(self,id:int):
        return self.app.map_data.get_chess_arr_by_id(id)

class Extension:
    PATH = "extensions"
    def __init__(self,app):
        self.app = app
        self.api = ExtAPI(app)
        self.extensions = dict[str,dict]()
        self.loc_rules = dict[str]()
        self.check_can_go_funcs = []
        if not os.path.exists(Extension.PATH):
            return
        for i in os.listdir(Extension.PATH):
            self.load_extension(os.path.join(Extension.PATH,i))
        Extension.Ext = self # 全局变量

    def load_extension(self,filename:str):
        def wrapper():
            if os.path.splitext(filename)[1] != ".py":
                return
            with open(filename,encoding = "utf-8") as rfile:
                data = rfile.read()
            local = {}
            exec(data,{"JBQ":self.api},local)
            name = local["EX_NAME"]
            self.extensions[name] = local
            self.loc_rules.update(local.get("loc_rules",{}))
            cf = local.get("check_can_go",None)
            if cf:
                self.check_can_go_funcs.append(cf)
        if self.app.debug:
            wrapper()
        else:
            try:
                wrapper()
            except KeyError:
                res = askyesno("提示",f"扩展{filename}格式错误，是否删除此扩展？")
                if res:
                    os.remove(filename)

    def add_extension(self,filename:str):
        if os.path.splitext(filename)[1] != ".py":
            return
        new_path = os.path.join(Extension.PATH,os.path.split(filename)[-1])
        shutil.copy(filename,new_path)
        self.load_extension(new_path)

    def check_can_go(self,can_go:list[ARR],chess,arr:ARR):
        for i in self.check_can_go_funcs:
            can_go = i(can_go,chess,arr)
        return can_go
