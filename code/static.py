import os
import sys
import xlrd
import json

basepath = os.path.split(__file__)[0]
static_path = os.path.join(basepath,"static.json")
setting_path = os.path.join(basepath,"setting.json")

ARR = tuple[int,int] # 棋子位置数组

class MapViewer:
    # 解析位置条件
    @staticmethod
    def parse_location(data:str):
        """
        X[1]&Y[2]&P[2,3]&T[7]
        ->
        [('X',1),('Y',2),('P',2,3),('T',7)]
        """
        data = data.split("&")
        loc = list[tuple]()
        for i in data:
            if not i:
                continue
            command = i[0]
            args = [int(j) for j in i[2:-1].split("|")]
            loc.append(tuple([command] + args))
        return loc

    # 解析移动规则
    @staticmethod
    def parse_move(data:str):
        """
        1(y:1&y:2),2(y:3&y:4),3
        ->
        [(1,[('y',1),('y',2)]),(2,[('y',3),('y',4)]),(3,)]
        """
        data = data.split(",")
        move = list[tuple]()
        for i in data:
            if not i:
                continue
            if "(" in i and i.endswith(")"):
                move.append((
                    int(i.split("(")[0]),
                    MapViewer.parse_location(i.split("(")[1][:-1])
                ))
            else:
                move.append((int(i),))
        return move

    @staticmethod
    def view(filename:str):
        xs = xlrd.open_workbook(filename)
        # 处理棋子
        chesses_xs = xs.sheet_by_name("chesses")
        chesses = []
        for i in range(chesses_xs.nrows - 1):
            rd = chesses_xs.row(i + 1)
            name = rd[1].value
            belong = int(rd[2].value)
            is_captain = rd[3].value == "c"
            move = [MapViewer.parse_move(k) for k in str(rd[4].value).split(";")]
            tran_con = MapViewer.parse_location(rd[5].value)
            tran_move = [MapViewer.parse_move(k) for k in str(rd[6].value).split(";")]
            if len(move) != 2 or len(tran_move) != 2:
                raise TypeError
            chesses.append([name,belong,is_captain,move,tran_con,tran_move])
        # 处理地图
        map_xs = xs.sheet_by_name("map")
        map = []
        rl = int(map_xs.cell_value(0,1))
        cl = int(map_xs.cell_value(0,3))
        for i in range(rl):
            map.append([])
            for j in range(cl):
                val = map_xs.cell_value(i + 1,j)
                map[-1].append(int(val) if val else None)
        # 处理特殊规则
        rules_xs = xs.sheet_by_name("rules")
        rules = {}
        rules["tran"] = rules_xs.cell_value(1,2) == "c" # 启用升变
        rules["pro_mess"] = rules_xs.cell_value(2,2) == "c" # 将军提示
        rules["restrict_move_ne"] = rules_xs.cell_value(3,2) == "c" # 限制连续3步以上移动中立棋子
        # 将打开的棋盘文件保存到设置中
        with open(setting_path,encoding = "utf-8") as rfile:
            setting = json.load(rfile)
            setting["lastly-load-map"] = filename
        with open(setting_path,"w",encoding = "utf-8") as wfile:
            json.dump(setting,wfile)
        return (chesses,map,rules)

def load_data():
    with open(static_path,encoding = "utf-8") as rfile:
        static = json.load(rfile)
    if os.path.exists(setting_path):
        with open(setting_path,encoding = "utf-8") as rfile:
            setting = json.load(rfile)
    else:
        setting = {
            "color-styles":"normal",
            "lastly-load-map":""
        }
        with open(setting_path,"w",encoding = "utf-8") as wfile:
            json.dump(setting,wfile)
    static_data = {}
    static_data["VERSION"] = static["VERSION"]
    static_data["about"] = static["about"]
    static_data["color-styles"] = [(i,static["color-styles"][i]["name"]) for i in static["color-styles"]]
    static_data["color-style-name"] = setting["color-styles"]
    static_data["colors"] = static["color-styles"][setting["color-styles"]]["colors"]
    static_data["btn-style"] = static["btn-style"]
    static_data["lastly-load-map"] = setting["lastly-load-map"]
    return static_data

try:
    static_data = load_data()
    COLORS = static_data["colors"]
except (FileNotFoundError,KeyError):
    from tkinter.messagebox import showerror
    showerror("错误","配置文件错误, 请尝试删除setting文件或重新下载static文件")
    sys.exit()