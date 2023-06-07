import os
import csv
import json

COLOR_STYLES = {
    "normal":{
        "name":"经典",
        "colors":{
            "chessboard":"khaki",
            "red-label":"pink",
            "blue-label":"skyblue",
            "chess-bg":"lightyellow",
            "selected-chess-bg":"yellow",
            "blank-feasible-bg":"lightgreen",
            "occupied-feasible-bg":"pink",
            "red-chess-fg":"lightcoral",
            "red-tran-chess-fg":"red",
            "blue-chess-fg":"cornflowerblue",
            "blue-tran-chess-fg":"blue",
            "neutral-chess-fg":"green"
        }
    },
    "dark":{
        "name":"暗色",
        "colors":{
            "chessboard":"grey",
            "red-label":"pink",
            "blue-label":"skyblue",
            "chess-bg":"darkslategrey",
            "selected-chess-bg":"darkgrey",
            "blank-feasible-bg":"green",
            "occupied-feasible-bg":"firebrick",
            "red-chess-fg":"pink",
            "red-tran-chess-fg":"lightcoral",
            "blue-chess-fg":"deepskyblue",
            "blue-tran-chess-fg":"dodgerblue",
            "neutral-chess-fg":"lightgreen"
        }
    }
}

class Setting:
    def __init__(self,setting_path = "setting.json"):
        self.setting_path = setting_path

    def read(self) -> dict[str]:
        if not os.path.exists(self.setting_path):
            setting = {
                "color-styles":"normal",
                "lastly-load-map":"",
                "record-path":"",
                "used-extensions":[]
            }
            self.write(setting)
            return setting
        with open(self.setting_path,encoding = "utf-8") as rfile:
            return json.load(rfile)

    def write(self,setting:dict[str]):
        with open(self.setting_path,"w",encoding = "utf-8") as wfile:
            json.dump(setting,wfile)

    def __getitem__(self,key:str):
        return self.read()[key]

    def __setitem__(self,key:str,value):
        setting = self.read()
        setting[key] = value
        self.write(setting)

def save_record(history:list[tuple[list[list],str]],record_path):
    if not record_path:
        return
    print_chessboard = []
    for index,i in enumerate(history):
        print_chessboard.append([f"回合{index + 1}"])
        print_chessboard.extend([[k.name if k else " " for k in j] for j in i[0]])
    with open(record_path,"w",newline = "") as wfile:
        writer = csv.writer(wfile)
        writer.writerows(print_chessboard)
