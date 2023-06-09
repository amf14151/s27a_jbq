def NP(args:tuple[int],arr:tuple[int,int]):
    get_abs_pos = lambda a,al:(a - 1) if a > 0 else a + al
    arrs = [(get_abs_pos(args[i],JBQ.rl),get_abs_pos(args[i + 1],JBQ.cl)) for i in range(0,len(args),2)]
    return arr not in arrs

def C(args:tuple[int],arr:tuple[int,int]):
    number = 0
    for i in range(JBQ.rl):
        for j in range(JBQ.cl):
            chess = JBQ.get_chess_by_arr((i,j))
            if chess and (args[0] == 0 or args[0] == chess.id):
                number += 1
    return args[1] <= number <= args[2]

def D(args:tuple[int],arr:tuple[int,int]):
    i_arr = JBQ.get_chess_arr_by_id(args[0]) # 相对棋子（cp）坐标
    if not i_arr:
        return False
    dis = abs(i_arr[0] - arr[0]) + abs(i_arr[1] - arr[1]) # 相对距离
    if args[1] == 1 and dis > args[2]: # 大于
        return True
    elif args[1] == 0 and dis == args[2]: # 等于
        return True
    elif args[1]== -1 and dis < args[2]: # 小于
        return True
    return False

def R(args:tuple[int],arr:tuple[int,int]):
    i_arr = JBQ.get_chess_arr_by_id(args[0]) # 相对棋子（cp）坐标
    if not i_arr:
        return False
    dis = abs(i_arr[0] - arr[0]) + abs(i_arr[1] - arr[1]) # 相对距离
    in_dis = False
    if args[1] == 1 and dis > args[2]: # 大于
        in_dis = True
    elif args[1] == 0 and dis == args[2]: # 等于
        in_dis = True
    elif args[1]== -1 and dis < args[2]: # 小于
        in_dis = True
    if not in_dis:
        return False
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
    return dire in args[3:]

def T(args:tuple[int],arr:tuple[int,int]):
    return not JBQ.get_chess_arr_by_id(args[0])

EX_NAME = "更多的可行走函数"
EX_VERSION = "1.2"

loc_rules = {
    "NP":NP,
    "C":C,
    "D":D,
    "R":R,
    "T":T
}

HELP = """
`NP[x1|y1|x2|y2|...]`，当棋子不在`(x1,y1)`、`(x2,y2)`等点时，该规则的值为`true`，否则为`false`
`C[i|m|n]`，当场上编号为`i`的棋子（当`i`的值为0时表示所有棋子）的数量介于[m,n]之间时，该规则的值为`true`，否则为`false`
`D[i|t|d]`，当棋子与编号为`i`的棋子（该棋子必须是唯一存活的，否则该规则的值为`false`）的直角距离（即只能横纵移动时从一个棋子移动到另一个的步数）大于（当`t`的值为1）或等于（当`t`的值为0）或小于（当`t`的值为-1）`d`时，该规则的值为`true`，否则为`false`
`R[i|t|d|r1|r2|...]`，当编号为`i`的棋子（该棋子必须是唯一存活的，否则该规则的值为`false`）在棋子的`r`（`r1`、`r2`等）侧且此时还满足`D[i|t|d]`时，该规则的值为`true`，否则为`false`
`T[i]`，当场上仍有多个编号为`i`的棋子或无编号为`i`的棋子时，该规则的值为`true`，否则为`false`
"""
