from tkinter.messagebox import showinfo,showerror

from .static import ARR,MapViewer,static_data,save_record
from .map import Chess,Map,HistoryRecorder
from .window import MainWindow,GameWindow,SettingWindow
from .extension import ExtAPI,ExtensionManager

class App:
    chess = Chess # 扩展调用
    running = False
    def __init__(self):
        if App.running:
            raise RuntimeError("App只能有一个实例")
        App.RUNNING = True
        self.map_data = None
        self.map_path = None
        self.open_setting = False

    def run(self,debug:bool = False):
        self.debug = debug
        self.extension_manager = ExtensionManager(self)
        self.window = MainWindow({
            # 主窗口调用的函数
            "get_map":self.get_map,
            "refresh_map":lambda:self.get_map(self.map_path,success_prompt = True),
            "start_game":self.start_game,
            "setting":self.setting
        },self.debug)
        if static_data["lastly-load-map"]:
            self.get_map(static_data["lastly-load-map"],False)
        self.window.mainloop()

    # 获取并加载地图
    def get_map(self,filename:str = None,error_prompt:bool = True,success_prompt:bool = False):
        if not filename:
            filename = self.window.choose_map_file()
        if not filename:
            return
        if self.debug:
            self.map_data = Map(*MapViewer.view(filename))
        else:
            try:
                self.map_data = Map(*MapViewer.view(filename))
            except FileNotFoundError:
                if error_prompt:
                    showerror("错误","未找到地图文件")
                return
            except:
                if error_prompt:
                    showerror("错误","地图文件格式错误")
                return
        if success_prompt:
            showinfo("提示","地图文件加载成功")
        self.map_path = filename
        self.window.set_map(self.map_path)

    def start_game(self):
        if self.open_setting:
            return
        if not self.map_data:
            showinfo("提示","暂未选择地图")
            return
        self.window.withdraw()
        if self.debug:
            game = Game(self.map_data,self.debug)
            game.start()
        else:
            try:
                game = Game(self.map_data,self.debug)
                game.start()
            except Exception as e:
                showerror("错误",f"游戏运行错误：{e}")
        self.window.deiconify()

    def add_extension(self):
        filename = self.window.choose_extension_file()
        self.extension_manager.add_extension(filename)
        self.window.refresh_extension()

    def setting(self):
        if not self.open_setting:
            self.open_setting = True
            setting_window = SettingWindow(self.close_setting_window,self.add_extension,self.window.refresh_extension)
            setting_window.mainloop()

    def close_setting_window(self,window:SettingWindow):
        self.open_setting = False
        window.destroy()

# 游戏类
# 每场创建一个新的Game对象
class Game:
    def __init__(self,map_data:Map,debug:bool):
        self.map_data = map_data
        self.map_data.init_chessboard(self.win)
        self.history_recorder = HistoryRecorder(self.map_data)
        game_api = {
            "click":self.click,
            "get_chess":lambda arr:self.map_data.chessboard[arr[0]][arr[1]],
            "get_can_go":self.get_can_go,
            "chosen_turn":lambda:self.turn if self.chosen else None,
            "back":self.back,
            "stop":self.stop
        }
        self.red_window = GameWindow(1,self.map_data,game_api,debug)
        self.blue_window = GameWindow(2,self.map_data,game_api,debug)
        ExtAPI.win = self.win
        ExtAPI.stalemate = self.stalemate

    def start(self):
        self.running = True
        self.turn = 1
        self.chosen = None
        self.refresh()
        while self.running:
            self.red_window.update()
            self.blue_window.update()
        self.red_window.destroy()
        self.blue_window.destroy()

    def refresh(self):
        turn = (self.history_recorder.now,len(self.history_recorder.history))
        self.red_window.set_text("turn",self.turn,turn)
        self.blue_window.set_text("turn",self.turn,turn)
        ExtAPI.turn = self.turn
        self.red_window.refresh_map()
        self.blue_window.refresh_map()

    # 游戏窗口点击棋子的回调函数
    def click(self,arr:ARR,belong:int):
        if belong != self.turn:
            return
        window = self.red_window if belong == 1 else self.blue_window
        if self.chosen: # 是否已经选择棋子
            if arr in self.chosen[1]:
                self.map_data.move(self.chosen[0],arr,self.turn)
                # 刚移动后的扩展调用
                ExtensionManager.Ext.after_move(self.chosen[0],arr)
                # 将军检测
                can_go = list[ARR]()
                cap_arr = list[ARR]()
                for i in range(self.map_data.rl):
                    for j in range(self.map_data.cl):
                        chess = self.map_data.chessboard[i][j]
                        if not chess:
                            continue
                        if chess.belong == self.turn:
                            can_go.extend(self.get_can_go(chess,(i,j)))
                        elif chess.belong != self.turn and chess.belong != 3 and chess.is_captain:
                            cap_arr.append((i,j))
                mess = False
                for i in cap_arr:
                    if i in can_go:
                        mess = True
                        break
                self.red_window.set_text("mess",self.turn if mess else 0)
                self.blue_window.set_text("mess",self.turn if mess else 0)
                self.turn = 1 if self.turn == 2 else 2
                self.history_recorder.add_history(self.map_data,self.turn)
                self.refresh()
            else:
                window.choose(*self.chosen,remove = True)
            self.chosen = None
        else: # 选择棋子
            chess = self.map_data.chessboard[arr[0]][arr[1]]
            if not chess:
                return
            if chess.belong != belong and chess.belong != 3:
                return
            if chess.belong == 3:
                if self.turn == 1 and self.map_data.red_move_ne == 2:
                    return
                elif self.turn == 2 and self.map_data.blue_move_ne == 2:
                    return
            can_go = self.get_can_go(chess,arr)
            if can_go:
                self.chosen = [arr,can_go]
                window.choose(*self.chosen)

    # 返回当前棋子可以行走的格子
    def get_can_go(self,chess:Chess,arr:ARR):
        can_go = list[list[ARR]]()
        for i in chess.now_move[0]: # 行走一格
            d_arr = self.map_data.get_arr_by_rd(arr,i,1)
            if not d_arr:
                continue
            mp = self.map_data.chessboard[d_arr[0]][d_arr[1]]
            if (not mp) or self.map_data.can_eat(chess,mp):
                can_go.append([d_arr])
        for i in chess.now_move[1]:
            can_go.append([])
            k = 1
            while True:
                d_arr = self.map_data.get_arr_by_rd(arr,i,k)
                if not d_arr:
                    break
                mp = self.map_data.chessboard[d_arr[0]][d_arr[1]]
                if not mp: # 空格，继续向远处搜索
                    can_go.append(can_go[-1] + [d_arr])
                elif self.map_data.can_eat(chess,mp):
                    can_go.append(can_go[-1] + [d_arr])
                    break
                else:
                    break
                k += 1
        can_go = ExtensionManager.Ext.check_can_go([i for i in can_go if i],chess,arr) # 载入扩展修改can_go
        can_go_set = set[ARR]() # 集合去重
        for i in can_go:
            for j in i:
                can_go_set.add(j)
        return list(can_go_set)

    # 悔棋及撤销
    def back(self,steps:int):
        data = self.history_recorder.rollback(steps)
        if data:
            self.map_data.chessboard,self.turn = data
            self.refresh()

    def win(self,turn:int):
        showinfo("提示",f"{'红方' if turn == 1 else '蓝方'}胜利")
        self.stop()

    # 和棋
    # 只能由扩展触发
    def stalemate(self):
        showinfo("提示","双方和棋")
        self.stop()

    def stop(self):
        try:
            save_record(self.history_recorder.history) # 记录棋局
        except PermissionError:
            showerror("错误","棋局记录文件被占用")
        self.running = False
