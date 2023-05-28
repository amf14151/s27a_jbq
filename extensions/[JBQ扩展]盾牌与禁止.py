EX_NAME = "盾牌与禁止"
EX_VERSION = "1.4"

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
                if len(now_move) > 2 and s_chess.belong != chess.belong:
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
                        if s_chess.belong != chess.belong:
                            pr1_arr.append(d_arr)
                        else:
                            pr2_arr.append(d_arr)
    if len(chess.now_move) > 5: # 有忽视禁
        for i in chess.now_move[5]: # 此处代码同无限走
            can_go.append([])
            k = 1
            while True:
                d_arr = JBQ.get_arr_by_rd(arr,i,k)
                if not d_arr:
                    break
                if d_arr in pr1_arr or d_arr in pr2_arr:
                    k += 1
                    continue
                mp = JBQ.get_chess_by_arr(d_arr)
                if not mp: # 空格，继续向远处搜索
                    can_go.append(can_go[-1] + [d_arr])
                elif mp.attr.get("is_pr","") == "c": # 标记为禁的棋子
                    k += 1
                    continue
                elif JBQ.can_eat(chess,mp):
                    can_go.append(can_go[-1] + [d_arr])
                    break
                else:
                    break
                k += 1
    elif len(chess.now_move) > 4: # 有跳禁
        for i in chess.now_move[4]:
            d_arr = JBQ.get_arr_by_rd(arr,i,1)
            if not d_arr:
                continue
            mp = JBQ.get_chess_by_arr(d_arr)
            if d_arr in pr1_arr or d_arr in pr2_arr or (mp and mp.attr.get("is_pr","") == "c"):
                d_arr = JBQ.get_arr_by_rd(arr,i,2)
                if not d_arr:
                    continue
                mp = JBQ.get_chess_by_arr(d_arr)
                if (not mp) or JBQ.can_eat(chess,mp):
                    can_go.append([d_arr])
    new_can_go = list(can_go) # 拷贝副本
    for i,j in enumerate(can_go):
        for k in j:
            w_chess = JBQ.get_chess_by_arr(k)
            if w_chess and w_chess.belong != chess.belong: # 对方棋子
                if arr in sh_arr: # 在盾牌范围内
                    new_can_go[i] = []
                    break
            elif arr in pr1_arr or k in pr1_arr:
                new_can_go[i] = []
                break
            elif k in pr2_arr:
                new_can_go[i] = []
                break
    return new_can_go

HELP = """
在自定义地图时可以在可行走一栏的第三栏（两个分号后，前两栏分别是行走一格与行走无限格）按照相同规则填写，作为盾牌格。棋子指向该格中的对方棋子无法对我方棋子发起攻击
在第四栏可以填写禁止格，棋子指向该格时所有棋子无法进入，已经进入的非本方棋子将被禁锢直到施加禁止的棋子离开或被吃
在第五栏可以填写跳禁格，棋子在此方向可以越过前方一格的禁止格（棋子施加的禁止或带有`is_pr`且值为`c`的标签的棋子）并走到前方两格的位置
在第六栏可以填写无视禁格，棋子在此方向可以行走无限格，且阻挡物如果是禁止格，则忽视该阻挡物
中立棋子施加的盾牌与禁止对所有棋子均有效
"""
