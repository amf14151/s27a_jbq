import os

from .static import ARR

class ExtAPI:
    @property
    def rl(self):
        return self.map_data.rl

    @property
    def cl(self):
        return self.map_data.cl

    def get_arr_by_rd(self,arr:ARR,r:int,d:int):
        return self.map_data.get_arr_by_rd(arr,r,d)

    def get_chess_by_arr(self,arr:ARR):
        return self.map_data.chessboard[arr[0]][arr[1]]

    def get_chess_arr_by_id(self,id:int):
        return self.map_data.get_chess_arr_by_id(id)

    def can_eat(self,chess1,chess2):
        return self.map_data.can_eat(chess1,chess2)

    def add_chess(self,id:int,arr:ARR):
        self.map_data.add_chess(id,arr)

    def move(self,arr1:ARR,arr2:ARR):
        return self.map_data.move(arr1,arr2,self.turn)

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
    def __init__(self):
        self.extensions = list[Extension]()
        self.extapi = ExtAPI()

    def set_map(self,map_data):
        self.extapi.map_data = map_data
        map_data.ext_manager = self

    def load_extension(self,filename:str):
        if os.path.splitext(filename)[1] != ".py":
            return
        with open(filename,encoding = "utf-8") as rfile:
            data = rfile.read()
        local = {}
        exec(data,{"JBQ":self.extapi},local)
        extension = Extension(local)
        self.extensions.append(extension)
        return extension

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
            new_can_go = i.check_can_go(can_go,chess,arr)
            can_go = [j for j in new_can_go if j]
        return can_go

    def after_move(self,arr1:ARR,arr2:ARR):
        for i in self.extensions:
            if not i.use:
                continue
            if not i.after_move:
                continue
            i.after_move(arr1,arr2)
