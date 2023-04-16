from functools import lru_cache

from s27a_jbq.static import ARR,COLORS

class Chess:
    def __init__(self,name:str,belong:int,is_captain:bool,move:list[list[tuple]],tran_con:list[tuple],tran_move:list[list[tuple]],map_data,win_func):
        self.name = name
        self.belong = belong
        self.is_captain = is_captain
        self.move = move
        self.tran_con = tran_con
        self.tran_move = tran_move
        self.map_data = map_data
        self.win_func = win_func
        self.is_tran = False

    # 棋子位置是否符合规则
    def is_in_position(self,arr:ARR,loc:list[tuple]):
        for i in loc:
            if not i:
                continue
            ad = self.map_data.rl if i[0] == "x" else self.map_data.cl
            ar = arr[0 if i[0] == "x" else 1]
            if (i[1] > 0 and ar == i[1] - 1) or (i[1] < 0 and ar == i[1] + ad):
                return True
        return False

    # 当前可移动位置
    @property
    def now_move(self):
        arr = self.map_data.get_chess_arr(self)
        move = list[list[int]]()
        for i in (self.tran_move if self.is_tran else self.move):
            move.append([])
            # i的示例：[(1,[('y',1),('y',2)]),(2,[('y',3),('y',4)]),(3,)]
            for j in i:
                if len(j) == 1: # 没有判断条件
                    move[-1].append(j[0])
                elif len(j) == 2:
                    if self.is_in_position(arr,j[1]):
                        move[-1].append(j[0])
        return move

    # 在按钮上显示的文字
    def text(self,rev:bool):
        text = ""
        def _in(num,string = " " * 3):
            nonlocal text
            if num in self.now_move[1]:
                text += "*"
            elif num in self.now_move[0]:
                text += "·"
            else:
                text += " "
            text += string
        _in(1)
        _in(2)
        _in(3,"\n")
        _in(4," " * 2)
        _in(5,"\n")
        _in(6)
        _in(7)
        _in(8,"")
        # 插入名字
        text = list(text)
        if rev:
            text.reverse()
        text.insert(12,self.name)
        text = "".join(text)
        # 设置字体颜色
        if self.belong == 1:
            if self.is_tran or not self.tran_con:
                self.fg = COLORS["red-tran-chess-fg"]
            else:
                self.fg = COLORS["red-chess-fg"]
        elif self.belong == 2:
            if self.is_tran or not self.tran_con:
                self.fg = COLORS["blue-tran-chess-fg"]
            else:
                self.fg = COLORS["blue-chess-fg"]
            
        else:
            self.fg = COLORS["neutral-chess-fg"]
        return text

    # 棋子被吃函数
    def be_eaten(self):
        if self.is_captain:
            self.win_func(self.belong) # 败方发送胜利回调
    
    # 升变条件检测
    def tran(self,arr:ARR):
        if self.is_tran:
            return
        if self.is_in_position(arr,self.tran_con):
            self.is_tran = True

class Map:
    def __init__(self,chesses:list,map:list[list[int]],rules:dict):
        self.chesses = chesses
        self.map = map
        self.rules = rules
        self.rl = len(self.map) # 地图行数
        self.cl = len(self.map[0]) # 地图列数
    
    # 初始化棋盘
    # 每局初始化一次
    def init_chessboard(self,win_func):
        self.chessboard = list[list[Chess]]()
        for i in self.map:
            self.chessboard.append([])
            for j in i:
                if j:
                    self.chessboard[-1].append(Chess(*self.chesses[j - 1],self,win_func))
                else:
                    self.chessboard[-1].append(None)
    
    # 获取棋子位置
    def get_chess_arr(self,chess:Chess):
        for i in range(self.rl):
            for j in range(self.cl):
                if self.chessboard[i][j] is chess:
                    return (i,j)

    # 移动棋子
    def move(self,arr1:ARR,arr2:ARR):
        if self.chessboard[arr2[0]][arr2[1]]:
            self.chessboard[arr2[0]][arr2[1]].be_eaten()
        self.chessboard[arr1[0]][arr1[1]],self.chessboard[arr2[0]][arr2[1]] = None,self.chessboard[arr1[0]][arr1[1]]
        if self.rules["tran"]:
            self.chessboard[arr2[0]][arr2[1]].tran(arr2)