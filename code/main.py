import xlrd
from tkinter.messagebox import showinfo,showwarning

from .static import ARR,MapViewer,static_data
from .map import Chess,Map
from .window import MainWindow,GameWindow,SettingWindow
from .online import OnlineConn

"""
    未完成：
    1. 特殊规则
    2. 多人联机
    3. 扩展
"""

class App:
    def __init__(self):
        self.conn = OnlineConn(self)
        self.window = MainWindow({
            "get_map":self.get_map,
            "refresh_map":lambda:self.get_map(self.map_path,success_prompt = True),
            "start_game":self.start_game,
            "create_room":self.conn.create,
            "enter_room":self.conn.enter,
            "setting":self.setting
        }) # 窗口调用的函数
        self.map_data = None
        self.map_path = None
        if static_data["lastly-load-map"]:
            self.get_map(static_data["lastly-load-map"],False)

    def get_map(self,filename:str = None,error_prompt:bool = True,success_prompt:bool = False):
        if not filename:
            filename = self.window.choose_map_file()
        if not filename:
            return
        try:
            self.map_data = Map(*MapViewer.view(filename))
            self.map_path = filename
            self.window.set_map(self.map_path)
        except FileNotFoundError:
            if error_prompt:
                showwarning("提示","未找到地图文件")
        except (TypeError,xlrd.biffh.XLRDError):
            if error_prompt:
                showwarning("提示","地图文件格式错误")
        else:
            if success_prompt:
                showinfo("提示","地图文件加载成功")

    def start_game(self,online:bool = False):
        if not self.map_data:
            showinfo("提示","暂未选择地图")
            return
        game = Game(self.map_data,self.conn if online else None)
        self.window.withdraw()
        game.start()
        self.window.deiconify()

    def setting(self):
        setting_window = SettingWindow()
        setting_window.mainloop()

    def run(self):
        self.window.mainloop()

# 游戏类
# 每场创建一个新的Game对象
class Game:
    def __init__(self,map_data:Map,online_conn:OnlineConn = None):
        self.map_data = map_data
        self.online_conn = online_conn
        self.map_data.init_chessboard(self.win)
        self.red_window = GameWindow(1,self.map_data,self.click_func,self.get_info,self.stop)
        self.blue_window = GameWindow(2,self.map_data,self.click_func,self.get_info,self.stop)
        if self.online_conn:
            if self.online_conn.belong == 1: # 红方
                self.online_conn.bind(self.blue_window)
            else:
                self.online_conn.bind(self.red_window)

    def start(self):
        self.running = True
        self.turn = 1
        self.chosen = None
        self.red_window.set_turn(1)
        self.blue_window.set_turn(1)
        while self.running:
            self.red_window.update()
            self.blue_window.update()
        self.red_window.destroy()
        self.blue_window.destroy()

    # 游戏窗口点击棋子的回调函数
    def click_func(self,arr:ARR,belong:int):
        if belong != self.turn:
            return
        window = self.red_window if belong == 1 else self.blue_window
        if self.chosen: # 是否已经选择棋子
            if arr in self.chosen[1]:
                self.map_data.move(self.chosen[0],arr)
                self.turn = 1 if self.turn == 2 else 2
                self.red_window.set_turn(self.turn)
                self.red_window.refresh_map()
                self.blue_window.set_turn(self.turn)
                self.blue_window.refresh_map()
            else:
                window.remove_choose(self.chosen[1])
            self.chosen = None
        else:#选择棋子
            chess = self.map_data.chessboard[arr[0]][arr[1]]
            if not chess:
                return
            if chess.belong != belong and chess.belong != 3:
                return
            can_go = self.get_can_go(chess,arr)
            if can_go:
                self.chosen = [arr,can_go]
                window.choose(can_go)

    # 返回当前棋子可以行走的格子
    def get_can_go(self,chess:Chess,arr:ARR):
        i,j = arr[0],arr[1]
        can_go = list[ARR]()
        #行走一格
        def wk1(x:int,ia:int,ja:int):
            if x in chess.now_move[1]:
                k = 1
                while 0 <= i + ia * k < self.map_data.rl and 0 <= j + ja * k < self.map_data.cl:
                    mp = self.map_data.chessboard[i + ia * k][j + ja * k]
                    if not mp:
                        can_go.append((i + ia * k,j + ja * k))
                    elif chess.belong != 3 and mp.belong != 3 and mp.belong != self.turn:
                        can_go.append((i + ia * k,j + ja * k))
                        break
                    else:
                        break
                    k += 1
            elif x in chess.now_move[0]:
                if 0 <= i + ia < self.map_data.rl and 0 <= j + ja < self.map_data.cl:
                    mp = self.map_data.chessboard[i + ia][j + ja]
                    if (not mp) or (chess.belong != 3 and mp.belong != 3 and mp.belong != self.turn):
                        can_go.append((i + ia,j + ja))
        wk1(1,-1,-1)
        wk1(2,-1,0)
        wk1(3,-1,1)
        wk1(4,0,-1)
        wk1(5,0,1)
        wk1(6,1,-1)
        wk1(7,1,0)
        wk1(8,1,1)
        return can_go

    # 显示棋子基本信息
    def get_info(self,arr:ARR):
        chess = self.map_data.chessboard[arr[0]][arr[1]]
        if not chess:
            return
        belong = "红方" if chess.belong == 1 else "蓝方" if chess.belong == 2 else "中立"
        is_captain = "是" if chess.is_captain else "否"
        is_tran = ("是" if chess.is_tran else "否") if chess.tran_con else "无法升变"
        move = chess.tran_move if chess.is_tran else chess.move
        info = f"名称：{chess.name}\n编号：{chess.id}\n归属：{belong}\n首领棋子：{is_captain}\n是否升变：{is_tran}\n目前可行走函数：{move}"
        showinfo("棋子信息",info)

    def win(self,belong:int):
        showinfo("提示",("红方" if belong == 2 else "蓝方") + "胜利") # 由于被吃棋子发送回调，所以belong相反
        self.stop()

    def stop(self):
        self.running = False