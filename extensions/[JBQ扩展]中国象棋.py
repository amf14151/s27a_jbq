EX_NAME = "中国象棋"
EX_VERSION = "0.1"

def check_can_go(can_go:list[list[tuple[int,int]]],chess,arr:tuple[int,int]):
    if chess.name == "相" or chess.name == "象":
        for i,j in enumerate(can_go):
            if len(j) >= 2:
                can_go[i] = [j[1]]
            else:
                can_go[i] = []
    elif chess.name == "炮":
        for i in can_go:
            if JBQ.get_chess_by_arr(i[-1]):
                del i[-1]
            for j in [2,4,5,7]:
                k = 1
                mt = False
                while True:
                    s_arr = JBQ.get_arr_by_rd(arr,j,k)
                    if not s_arr:
                        break
                    ch = JBQ.get_chess_by_arr(s_arr)
                    if ch:
                        if not mt:
                            mt = True
                        else:
                            if ch.belong != JBQ.turn:
                                i.append(s_arr)
                            break
                    k += 1
    elif chess.name == "马":
        for i in [[2,1,3],[4,1,6],[5,3,8],[7,6,8]]:
            s_arr = JBQ.get_arr_by_rd(arr,i[0],1)
            if not s_arr:
                continue
            ch = JBQ.get_chess_by_arr(s_arr)
            if ch: # 蹩马腿
                continue
            for j in i[1:]:
                s2_arr = JBQ.get_arr_by_rd(s_arr,j,1)
                ch = JBQ.get_chess_by_arr(s2_arr)
                if ch and ch.belong == JBQ.turn:
                    continue
                can_go.append([s2_arr])
    return can_go

def after_move(arr1,arr2):
    # 将帅不能照面
    for i in range(3,6):
        chesses = []
        c1 = c2 = False
        for j in range(JBQ.rl): # 读取一列中的每一个
            chess = JBQ.get_chess_by_arr((j,i))
            if chess:
                chesses.append(chess)
                if chess.name == "将":
                    c1 = True
                elif chess.name == "帅":
                    c2 = True
        if c1 and c2:
            for j,k in enumerate(chesses):
                if k.name == "将":
                    if chesses[j + 1].name == "帅":
                        JBQ.win(1 if JBQ.turn == 2 else 2)

HELP = """
中国象棋还原版，请使用 https://github.com/amf14151/s27a_jbq/blob/main/map/中国象棋.xlsx 地图
"""
