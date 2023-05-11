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

    def move(self,arr1:ARR,arr2:ARR):
        return self.app.map_data.move(arr1,arr2,self.turn)

class Extension:
    def __init__(self,methods:dict[str]):
        self.name = methods["EX_NAME"]
        self.version = methods["EX_VERSION"]
        self.use = True
        self.loc_rules = methods.get("loc_rules",{})
        self.check_can_go = methods.get("check_can_go",None)
        self.after_move = methods.get("after_move",None)

    def text(self):
        return f"{self.name}-{self.version}"

class ExtensionManager:
    PATH = "extensions"
    def __init__(self,app):
        self.debug = app.debug
        self.extapi = ExtAPI(app)
        self.extensions = list[Extension]()
        ExtensionManager.Ext = self # 全局变量
        if not os.path.exists(ExtensionManager.PATH):
            return
        for i in os.listdir(ExtensionManager.PATH):
            self.load_extension(os.path.join(ExtensionManager.PATH,i))

    def load_extension(self,filename:str):
        def wrapper():
            if os.path.splitext(filename)[1] != ".py":
                return
            with open(filename,encoding = "utf-8") as rfile:
                data = rfile.read()
            local = {}
            exec(data,{"JBQ":self.extapi},local)
            self.extensions.append(Extension(local))
        if self.debug:
            wrapper()
        else:
            try:
                wrapper()
            except:
                res = askyesno("提示",f"扩展{filename}格式错误，是否删除此扩展？")
                if res:
                    os.remove(filename)

    def add_extension(self,filename:str):
        if os.path.splitext(filename)[1] != ".py":
            return
        new_path = os.path.join(ExtensionManager.PATH,os.path.split(filename)[-1])
        shutil.copy(filename,new_path)
        self.load_extension(new_path)

    @property
    def loc_rules(self):
        loc_rules = {}
        for i in self.extensions:
            if not i.use:
                continue
            loc_rules.update(i.loc_rules)
        return loc_rules

    def check_can_go(self,can_go:list[list[ARR]],chess,arr:ARR):
        for i in self.extensions:
            if not i.use:
                continue
            if not i.check_can_go:
                continue
            if self.debug:
                can_go = i.check_can_go(can_go,chess,arr)
            else:
                try:
                    can_go = i.check_can_go(can_go,chess,arr)
                except:
                    pass
            can_go = [j for j in can_go if j]
        return can_go

    def after_move(self,arr1:ARR,arr2:ARR):
        for i in self.extensions:
            if not i.use:
                continue
            if not i.after_move:
                continue
            if self.debug:
                i.after_move(arr1,arr2)
            else:
                try:
                    i.after_move(arr1,arr2)
                except:
                    pass
