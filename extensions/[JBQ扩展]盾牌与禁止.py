EX_NAME = "盾牌与禁止"
EX_VERSION = "1.1"

def check_can_go(can_go:list[list[tuple[int,int]]],chess,arr:tuple[int,int]):
    # 查找对方与中立方当前在场的所有盾牌与禁止
    sh_arr = list[tuple[int,int]]() # 对方与中立方盾牌
    pr1_arr = list[tuple[int,int]]() # 对方与中立方禁止
    pr2_arr = list[tuple[int,int]]() # 我方禁止
    for i in range(JBQ.rl):
        for j in range(JBQ.cl):
            s_chess = JBQ.get_chess_by_arr((i,j))
            if s_chess:
                now_move = s_chess.now_move
                if len(now_move) > 2 and s_chess.belong != JBQ.turn:
                    for k in now_move[2]:
                        d_arr = JBQ.get_arr_by_rd((i,j),k,1) # 计算偏移量（针对四周布盾，而不是自身）
                        if not d_arr:
                            continue
                        sh_arr.append(d_arr)
                if len(now_move) > 3:
                    for k in now_move[3]:
                        d_arr = JBQ.get_arr_by_rd((i,j),k,1) # 计算偏移量（针对四周布禁锢，而不是自身）
                        if not d_arr:
                            continue
                        if s_chess.belong != JBQ.turn:
                            pr1_arr.append(d_arr)
                        else:
                            pr2_arr.append(d_arr)
    new_can_go = list(can_go)
    for i,j in enumerate(can_go):
        for k,l in enumerate(j):
            w_chess = JBQ.get_chess_by_arr(l)
            if w_chess and w_chess.belong != chess.belong: # 对方棋子
                if arr in sh_arr: # 在盾牌范围内
                    del new_can_go[i][k:]
                    break
            elif arr in pr1_arr or l in pr1_arr:
                del new_can_go[i][k:]
                break
            elif l in pr2_arr:
                del new_can_go[i][k:]
                break
    return new_can_go

HELP = """
在自定义地图时可以在可行走一栏的第三栏（两个分号后，前两栏分别是行走一格与行走无限格）按照相同规则填写，作为盾牌格。该格中的对方棋子无法对我方棋子发起攻击
同理，在第四栏可以填写禁止格，该格所有棋子无法进入，已经进入的非本方棋子将被禁锢直到施加禁止的棋子离开或被吃
中立棋子施加的盾牌与禁止对所有棋子均有效
"""
