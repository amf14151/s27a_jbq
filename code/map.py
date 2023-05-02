from .static import ARR,static_data

class Chess:
    def __init__(self,id:int,name:str,belong:int,is_captain:bool,move:list[list[tuple]],tran_con:list[tuple],tran_move:list[list[tuple]],map_data,win_func):
        self.id = id
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
        get_abs_pos = lambda a,al:(a - 1) if a > 0 else a + al # 把输入的含正负坐标转换为0-n的坐标
        for i in loc:
            command = i[0]
            if command == "X": # 函数X（行）
                for j in i[1:]:
                    if arr[0] == get_abs_pos(j,self.map_data.rl):
                        return True
            elif command == "Y": # 函数Y（列）
                for j in i[1:]:
                    if arr[1] == get_abs_pos(j,self.map_data.cl):
                        return True
            elif command == "P": # 函数P（点）
                if arr == [get_abs_pos(i[1],self.map_data.rl),get_abs_pos(i[2],self.map_data.cl)]:
                    return True
            elif command == "D" or command == "R": # 函数D[i|t|d]（相对距离） 函数R[i|r|t|d]（相对距离、方向）
                i_arr = self.map_data.get_chess_arr_by_id(i[1]) # 相对棋子坐标
                if not i_arr:
                    continue
                dis = abs(i_arr[0] - arr[0]) + abs(i_arr[1] - arr[1]) # 相对距离
                in_dis = False
                if i[2] == 1 and dis > i[3]: # 大于
                    in_dis = True
                elif i[2] == 0 and dis == i[3]: # 等于
                    in_dis = True
                elif i[2] == -1 and dis < i[3]: # 小于
                    in_dis = True
                if not in_dis:
                    continue
                if command == "D":
                    return True
                # 还需要进行方向判定
                if i_arr[0] < arr[0]: # i棋子x坐标较小（在上方）
                    if i_arr[1] < arr[1]:
                        dire = 1
                    elif i_arr[1] == arr[1]:
                        dire = 2
                    else:
                        dire = 3
                elif i_arr[0] == arr[0]:
                    if i_arr[1] < arr[1]:
                        dire = 4
                    elif i_arr[1] == arr[1]: # 重合，不计
                        dire = 0
                    else:
                        dire = 5
                else:
                    if i_arr[1] < arr[1]:
                        dire = 6
                    elif i_arr[1] == arr[1]:
                        dire = 7
                    else:
                        dire = 8
                if dire in i[4:]:
                    return True
            elif command == "T": # 函数T[i]（多个、已死亡）
                if not self.map_data.get_chess_arr_by_id(i[1]):
                    return True
        return False

    # 当前可移动位置
    @property
    def now_move(self):
        arr = self.map_data.get_chess_arr(self)
        move = list[list[int]]()
        for i in (self.tran_move if self.is_tran else self.move):
            move.append([])
            # i的示例：[(1,[('Y',1),('Y',2)]),(2,[('Y',3),('Y',4)]),(3,)]
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
        now_move = self.now_move # 每次调用self.now_move都需要重新计算，因此先赋值中间变量
        def _in(num,string = " " * 3):
            nonlocal text
            if num in now_move[1]:
                text += "*"
            elif num in now_move[0]:
                text += "·"
            else:
                text += " "
            text += string
        _in(1)
        _in(2)
        _in(3,"\n")
        _in(4," " * 2) # 空出名字位置
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
                self.fg = static_data["colors"]["red-tran-chess-fg"]
            else:
                self.fg = static_data["colors"]["red-chess-fg"]
        elif self.belong == 2:
            if self.is_tran or not self.tran_con:
                self.fg = static_data["colors"]["blue-tran-chess-fg"]
            else:
                self.fg = static_data["colors"]["blue-chess-fg"]
            
        else:
            self.fg = static_data["colors"]["neutral-chess-fg"]
        return text

    # 获取基本信息
    @property
    def info(self):
        belong = "红方" if self.belong == 1 else "蓝方" if self.belong == 2 else "中立"
        is_captain = "是" if self.is_captain else "否"
        is_tran = ("是" if self.is_tran else "否") if self.tran_con else "无法升变"
        move = self.tran_move if self.is_tran else self.move
        info = f"名称：{self.name}\n编号：{self.id}\n归属：{belong}\n首领棋子：{is_captain}\n是否升变：{is_tran}\n目前可行走函数：{move}"
        return info

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
        self.red_move_ne = 0 # 红方移动中立棋子次数
        self.blue_move_ne = 0
    
    # 初始化棋盘
    # 每局初始化一次
    def init_chessboard(self,win_func):
        self.chessboard = list[list[Chess]]()
        for i in self.map:
            self.chessboard.append([])
            for j in i:
                if j:
                    self.chessboard[-1].append(Chess(j,*self.chesses[j - 1],self,win_func))
                else:
                    self.chessboard[-1].append(None)
    
    # 获取棋子位置
    def get_chess_arr(self,chess:Chess):
        for i in range(self.rl):
            for j in range(self.cl):
                if self.chessboard[i][j] is chess:
                    return (i,j)

    def get_chess_arr_by_id(self,id:int):
        x = None
        for i in range(self.rl):
            for j in range(self.cl):
                if self.chessboard[i][j] and self.chessboard[i][j].id == id:
                    if x:
                        return None
                    x = (i,j)
        return x

    # 移动棋子
    def move(self,arr1:ARR,arr2:ARR,turn:int):
        if self.rules["restrict_move_ne"] and self.chessboard[arr1[0]][arr1[1]] and self.chessboard[arr1[0]][arr1[1]].belong == 3:
            if turn == 1:
                self.red_move_ne += 1
            else:
                self.blue_move_ne += 1
        else:
            if turn == 1:
                self.red_move_ne = 0
            else:
                self.blue_move_ne = 0
        if self.chessboard[arr2[0]][arr2[1]]:
            self.chessboard[arr2[0]][arr2[1]].be_eaten()
        self.chessboard[arr1[0]][arr1[1]],self.chessboard[arr2[0]][arr2[1]] = None,self.chessboard[arr1[0]][arr1[1]]
        if self.rules["tran"]:
            self.chessboard[arr2[0]][arr2[1]].tran(arr2)