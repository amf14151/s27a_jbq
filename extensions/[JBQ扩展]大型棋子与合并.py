EX_NAME = "大型棋子与合并"
EX_VERSION = "1.3"

def check_can_go(can_go:list[list[tuple[int,int]]],chess,arr:tuple[int,int]):
    # 根据相对位置确定的绝对位置
    def get_abs_epd_list(epd_list):
        for i in range(len(epd_list)):
                for j in range(len(epd_list[0])):
                    if epd_list[i][j] == 0:
                        self_epdarr = (i,j)
        abs_epd_list = list[list[tuple[int,int]]]()
        for i in range(len(epd_list)):
            abs_epd_list.append([])
            for j in range(len(epd_list[0])):
                abs_epd_list[-1].append((arr[0] + i - self_epdarr[0],arr[1] + j - self_epdarr[1]))
        return abs_epd_list
    if not chess.attr.get("is_epd",False): # 未合体棋子
        for i in range(len(can_go)):
            for j in range(len(can_go[i])):
                e_chess = JBQ.get_chess_by_arr(can_go[i][j])
                if e_chess and e_chess.attr.get("is_epd",False):
                    del can_go[i][j]
        if not chess.attr.get("epd",None):
            return can_go
    if chess.attr.get("is_epd",False): # 已经合体
        can_go = [[],[],[],[]]
        if chess.attr.get("epd",None): # 主棋子
            epd_list = eval(chess.attr["epd"])
            abs_epd_list = get_abs_epd_list(epd_list)
            x1,x2 = abs_epd_list[0][0][0] - 1,abs_epd_list[-1][0][0] + 1
            y1,y2 = abs_epd_list[0][0][1] - 1,abs_epd_list[0][-1][1] + 1
            x1_ok = x2_ok = y1_ok = y2_ok = True
            for i in range(len(abs_epd_list[0])):
                y = i + y1 + 1
                if x1 >= 0 and x1_ok:
                    if JBQ.get_chess_by_arr((x1,y)):
                        x1_ok = False
                        can_go[0] = []
                    else:
                        can_go[0].append((x1,y))
                if x2 < JBQ.rl and x2_ok:
                    if JBQ.get_chess_by_arr((x2,y)):
                        x2_ok = False
                        can_go[1] = []
                    else:
                        can_go[1].append((x2,y))
            for i in range(len(abs_epd_list)):
                x = i + x1 + 1
                if y1 >= 0 and y1_ok:
                    if JBQ.get_chess_by_arr((x,y1)):
                        y1_ok = False
                        can_go[2] = []
                    else:
                        can_go[2].append((x,y1))
                if y2 < JBQ.rl and y2_ok:
                    if JBQ.get_chess_by_arr((x,y2)):
                        y2_ok = False
                        can_go[3] = []
                    else:
                        can_go[3].append((x,y2))
        else:
            return can_go
    else:
        epd_list = eval(chess.attr["epd"])
        abs_epd_list = get_abs_epd_list(epd_list)
        for i in range(len(abs_epd_list)):
            for j in range(len(abs_epd_list[0])):
                if epd_list[i][j] == 0:
                    continue
                epd_arr = abs_epd_list[i][j] # 要搜寻棋子在chessboard中的位置
                if 0 <= epd_arr[0] < JBQ.rl and 0 <= epd_arr[1] < JBQ.cl:
                    chess = JBQ.get_chess_by_arr(epd_arr)
                    if (not chess) or chess.id != epd_list[i][j]:
                        return can_go
                else:
                    return can_go
    can_go.append([arr])
    return can_go

def after_move(arr1:tuple[int,int],arr2:tuple[int,int]):
    def get_abs_epd_list(epd_list):
        for i in range(len(epd_list)):
                for j in range(len(epd_list[0])):
                    if epd_list[i][j] == 0:
                        self_epdarr = (i,j)
        abs_epd_list = list[list[tuple[int,int]]]()
        for i in range(len(epd_list)):
            abs_epd_list.append([])
            for j in range(len(epd_list[0])):
                abs_epd_list[-1].append((arr1[0] + i - self_epdarr[0],arr1[1] + j - self_epdarr[1]))
        return abs_epd_list
    if arr1 == arr2: # 走到自己的位置
        chess = JBQ.get_chess_by_arr(arr1)
        if not chess.attr.get("epd",None):
            return
        epd_list = eval(chess.attr["epd"])
        abs_epd_list = get_abs_epd_list(epd_list)
        is_epd = chess.attr.get("is_epd",False)
        for i in abs_epd_list:
            for j in i:
                epd_chess = JBQ.get_chess_by_arr(j)
                if is_epd: # 已经合体，解体
                    epd_chess.attr["is_epd"] = False
                    epd_chess.name = epd_chess.attr["f_name"]
                    epd_chess.move,epd_chess.tran_move = epd_chess.attr["f_move"],epd_chess.attr["f_tran_move"]
                else:
                    epd_chess.attr["is_epd"] = True
                    epd_chess.attr["f_name"] = epd_chess.name # 原名称
                    epd_chess.name = chess.attr["epd_name"].strip('"')
                    epd_chess.attr["f_move"],epd_chess.attr["f_tran_move"] =  epd_chess.move,epd_chess.tran_move
                    epd_chess.move = epd_chess.tran_move = [[(2,),(4,),(5,),(7,)],[]]
    else:
        chess = JBQ.get_chess_by_arr(arr2)
        if chess.attr.get("is_epd",False):
            JBQ.move(arr2,arr1) # 先移动回原点
            epd_list = eval(chess.attr["epd"])
            abs_epd_list = get_abs_epd_list(epd_list)
            x1,x2 = abs_epd_list[0][0][0] - 1,abs_epd_list[-1][0][0] + 1
            y1,y2 = abs_epd_list[0][0][1] - 1,abs_epd_list[0][-1][1] + 1
            if arr2[0] == x1: # 向上走
                for i in abs_epd_list:
                    for j in i:
                        JBQ.move(j,(j[0] - 1,j[1]))
            elif arr2[0] == x2: # 向下走
                for i in abs_epd_list[::-1]:
                    for j in i:
                        JBQ.move(j,(j[0] + 1,j[1]))
            elif arr2[1] == y1: # 向左走
                for i in abs_epd_list:
                    for j in i:
                        JBQ.move(j,(j[0],j[1] - 1))
            elif arr2[1] == y2: # 向右走
                for i in abs_epd_list:
                    for j in i[::-1]:
                        JBQ.move(j,(j[0],j[1] + 1))

HELP = """
可以占据多格的大型棋子
棋子的拆分与合并
"""
