import copy

from ..__constants__ import __version__
from .static import ARR,MapViewer
from .map import Chess,Map
from .extension import ExtensionManager

# 游戏类
# 每场创建一个新的Game对象
class Game:
    def __init__(self,map_data:Map,ext_manager:ExtensionManager):
        self.map_data = map_data
        self.ext_manager = ext_manager
        self.ext_manager.set_map(self.map_data)
        self.map_data.init_chessboard(self.win)
        self.recorder = Recorder(self.map_data)
        self.chosen = None
        self.ext_manager.extapi.win = self.win
        self.ext_manager.extapi.stalemate = lambda:self.stop("stalemate")

    def start(self):
        self.running = True
        self.stop_type = ""
        self.turn = 1
        self.ext_manager.extapi.turn = self.turn

    # 将军检测
    def is_mess(self,cap_belong:int):
        can_go = list[ARR]()
        cap_arr = list[ARR]()
        for i in range(self.map_data.rl):
            for j in range(self.map_data.cl):
                chess = self.map_data.chessboard[i][j]
                if not chess:
                    continue
                if chess.belong != cap_belong and chess.belong != 3:
                    can_go.extend(self.get_can_go(chess,(i,j)))
                elif chess.belong == cap_belong and chess.is_captain:
                    cap_arr.append((i,j))
        for i in cap_arr:
            if i in can_go:
                return True
        return False

    # 游戏窗口点击棋子的回调函数
    def click(self,arr:ARR):
        if self.chosen: # 是否已经选择棋子
            if arr in self.chosen[1]:
                self.map_data.move(self.chosen[0],arr,self.turn)
                # 刚移动后的扩展调用
                self.ext_manager.after_move(self.chosen[0],arr)
                self.turn = 1 if self.turn == 2 else 2
                self.recorder.add_history(self.map_data,self.turn)
                self.chosen = None
                self.ext_manager.extapi.turn = self.turn
                return "walk"
            else:
                self.chosen = None
                return "clear_chosen"
        else: # 选择棋子
            chess = self.map_data.chessboard[arr[0]][arr[1]]
            if not chess:
                return "nothing"
            if chess.belong != self.turn and chess.belong != 3:
                return "nothing"
            if chess.belong == 3:
                if self.turn == 1 and self.map_data.red_move_ne == 2 or self.turn == 2 and self.map_data.blue_move_ne == 2:
                    return "nothing"
            can_go = self.get_can_go(chess,arr)
            if can_go:
                self.chosen = [arr,can_go]
                return "choose"
            else:
                return "nothing"

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
        can_go = self.ext_manager.check_can_go([i for i in can_go if i],chess,arr) # 载入扩展修改can_go
        can_go_set = set[ARR]() # 集合去重
        for i in can_go:
            for j in i:
                can_go_set.add(j)
        return list(can_go_set)

    # 悔棋及撤销
    def back(self,steps:int):
        data = self.recorder.rollback(steps)
        if data:
            self.map_data.chessboard,self.turn = data
            self.ext_manager.extapi.turn = self.turn
            return True
        return False

    def win(self,turn:int):
        self.stop("red" if turn == 1 else "blue")

    def stop(self,type:str = "stop"):
        self.stop_type = type
        self.running = False

class Recorder:
    def __init__(self,map_data:Map):
        self.history = list[tuple[list[list[Chess]],str]]()
        self.history.append((self.copy_chessboard(map_data.chessboard),1)) # 初始也在其中，走完后立即add
        self.now = 1 # 当前位置（不含）

    @staticmethod
    def copy_chessboard(chessboard:list[list[Chess]]):
        new_chessboard = list[list[Chess]]()
        for i in chessboard:
            new_chessboard.append([])
            for j in i:
                if j:
                    new_chessboard[-1].append(copy.copy(j))
                else:
                    new_chessboard[-1].append(None)
        return new_chessboard

    def add_history(self,map_data:Map,turn:str):
        del self.history[self.now:]
        self.history.append((self.copy_chessboard(map_data.chessboard),turn))
        self.now += 1

    def rollback(self,steps:int): # steps可以是负数（撤销）
        if self.now - steps < 1 or self.now - steps > len(self.history):
            return
        self.now -= steps
        data = self.history[self.now - 1]
        return (self.copy_chessboard(data[0]),data[1])
