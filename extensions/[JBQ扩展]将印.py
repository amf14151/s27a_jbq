EX_NAME = "将印"
EX_VERSION = "1.1"

class Mark:
    def __init__(self):
        self.mark_belong = 2

    # 获取turn方首领位置
    def get_captain(self,turn:int):
        for i in range(JBQ.rl):
            for j in range(JBQ.cl):
                chess = JBQ.get_chess_by_arr((i,j))
                if chess and chess.belong == turn and chess.is_captain:
                    return (i,j)

    # 获取turn方的大旗位置
    def get_banner(self,turn:int):
        captain_arr = self.get_captain(turn)
        if not captain_arr: # 首领已死亡
            return (-1,-1)
        banner = eval(JBQ.get_chess_by_arr(captain_arr).attr["banner"])
        return (banner[0] - 1,banner[1] - 1)

    # 将领在有将印时可以走到大旗中
    def check_can_go(self,can_go:list[list[tuple[int,int]]],chess,arr:tuple[int,int]):
        if chess.is_captain and self.mark_belong == JBQ.turn:
            banner_arr = self.get_banner(JBQ.turn)
            if arr != banner_arr: # 不在大旗中
                if -1 <= arr[0] - banner_arr[0] <= 1 and -1 <= arr[0] - banner_arr[0] <= 1: # 在大旗附近
                    banner_chess = JBQ.get_chess_by_arr(banner_arr)
                    if (not banner_chess) or (banner_chess.belong != 3 and banner_chess.belong != JBQ.turn):
                        can_go.append([banner_arr])
        return can_go

    # 判断是否更换将印位置，在将领大旗中切换move函数
    def after_move(self,arr1:tuple[int,int],arr2:tuple[int,int]):
        banner_arr = self.get_banner(1 if JBQ.turn == 2 else 2)
        if arr2 == banner_arr:
            self.mark_belong = 1 if self.mark_belong == 2 else 2
        cap_arr = self.get_captain(JBQ.turn)
        banner_arr = self.get_banner(JBQ.turn)
        chess = JBQ.get_chess_by_arr(cap_arr)
        if cap_arr == banner_arr: # 将领在大旗中
            chess.attr["f_move"],chess.attr["f_tran_move"] =  chess.move,chess.tran_move
            chess.move = chess.tran_move = eval(chess.attr["move_in_banner"])
        elif chess.attr.get("f_move",None) != None:
            chess.move,chess.tran_move = chess.attr["f_move"],chess.attr["f_tran_move"]
            del chess.attr["f_move"]
            del chess.attr["f_tran_move"]

mark = Mark()

check_can_go = mark.check_can_go
after_move = mark.after_move

HELP = """
将印是一种印记，默认为后手方所有。双方各有一特殊位置定为“大旗”，当持有将印一方的将领走入本方大旗时变为特殊形态，当本方任意棋子走入对方大旗时若将印为对方所有，则交由己方
在首领棋子栏新增“banner”项，形式为`(x,y)`，为本方大旗位置
新增“move_in_banner”项，形式为处理后的可行走规则，为持有将印时将领在本方大旗中的可行走规则
"""
