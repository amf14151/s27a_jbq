import tkinter as tk
from tkinter.messagebox import showinfo

from ..__constants__ import __version__
from ..game import Game
from ..game.static import ARR
from ..game.map import Chess
from ..game.extension import ExtensionManager
from .setting import COLOR_STYLES,Setting

class GameWindow(tk.Tk):
    def __init__(self,belong:int,game:Game,debug:bool):
        super().__init__()
        self.belong = belong
        self.game = game
        self.debug = debug
        self.colors = COLOR_STYLES[Setting()["color-styles"]]["colors"]
        self.can_go_prompt_list = ["·","*","o","x","$","%"]
        self.show_can_go_prompt = True
        self.title("红方" if self.belong == 1 else "蓝方")
        self.resizable(width = False,height = False)
        self.protocol("WM_DELETE_WINDOW",self.game.stop)
        self.init_menu()
        self.init_chessboard()
        self.refresh_map()

    # 初始化菜单栏
    def init_menu(self):
        self.menu = tk.Menu(self)
        self.config(menu = self.menu)
        # 游戏菜单
        self.game_menu = tk.Menu(self.menu,tearoff = False)
        self.menu.add_cascade(label = "游戏(G)",underline = 3,menu = self.game_menu)
        self.game_menu.add_command(label = "查看地图信息",command = self.map_info)
        self.game_menu.add_separator()
        if False:
            self.game_menu.add_command(label = "查看当前房间")
            self.game_menu.add_separator()
        self.game_menu.add_command(label = "退出游戏",accelerator = "Alt+F4",command = self.game.stop)
        # 功能菜单
        self.func_menu = tk.Menu(self.menu,tearoff = False)
        self.menu.add_cascade(label = "功能(F)",underline = 3,menu = self.func_menu)
        if True and self.game.map_data.rules["back"]: # 仅在单人模式下生效
            self.func_menu.add_command(label = "悔棋",command = lambda:self.back(1))
            self.func_menu.add_command(label = "撤销悔棋",command = lambda:self.back(-1))
            self.func_menu.add_separator()
        self.func_menu.add_command(label = "切换棋子大小",command = self.change_chess_height)
        self.func_menu.add_command(label = "显示/隐藏可行走提示",command = self.change_show_prompt)

    def back(self,steps:int):
        if not self.game.back(steps):
            showinfo("提示","操作失败")

    def change_chess_height(self):
        for i in self.chess_btn:
            for j in i:
                if j["height"] == 3: # 大棋子
                    j["height"] = 2
                    j["width"] = 5
                else:
                    j["height"] = 3
                    j["width"] = 8

    def change_show_prompt(self):
        self.show_can_go_prompt = not self.show_can_go_prompt
        self.refresh_map()

    #反方棋盘渲染反转横纵坐标
    def getx(self,x:int):
        return x if self.belong == 1 else self.game.map_data.rl - x - 1

    def gety(self,y:int):
        return y if self.belong == 1 else self.game.map_data.cl - y - 1

    def init_chessboard(self):
        self.turn_label = tk.Label(self,height = 3,width = 24,bg = self.colors[f"{'red' if self.belong == 1 else 'blue'}-label"]) # 回合提示
        self.turn_label.pack()
        self.chess_frame = tk.Frame(self,bg = self.colors["chessboard"])
        self.chess_btn = list[list[tk.Button]]()
        for i in range(self.game.map_data.rl):
            self.chess_btn.append([])
            for j in range(self.game.map_data.cl):
                self.chess_btn[-1].append(tk.Button(self.chess_frame,height = 3,width = 8,relief = "flat",bd = 0,command = self.click(i,j,1)))
                self.chess_btn[-1][-1].bind("<Button 3>",self.click(i,j,3))
                self.chess_btn[-1][-1].bind("<Enter>",self.click(i,j,4))
                self.chess_btn[-1][-1].bind("<Leave>",self.click(i,j,5))
                self.chess_btn[-1][-1].grid(row = i,column = j,padx = 1,pady = 1)
        self.chess_frame.pack()
        self.mess_label = tk.Label(self,height = 3,width = 24)
        self.mess_label.pack()
        if len(self.chess_btn) > 8 or len(self.chess_btn[0]) > 12:
            self.change_chess_height()
            self.change_show_prompt()

    def bind_window(self,window):
        self.b_window = window

    def refresh_map(self,call_by_b_window:bool = False):
        for i in range(self.game.map_data.rl):
            for j in range(self.game.map_data.cl):
                chess = self.game.map_data.chessboard[self.getx(i)][self.gety(j)]
                if chess:
                    text,fg = self.get_chess_text(chess)
                    self.chess_btn[i][j]["text"] = text
                    self.chess_btn[i][j]["fg"] = fg
                else:
                    self.chess_btn[i][j]["text"] = ""
                self.chess_btn[i][j]["bg"] = self.colors["chess-bg"]
        self.turn_label["text"] = f"{'己方' if self.game.turn == self.belong else '对方'}回合\n回合数：{self.game.recorder.now}/{len(self.game.recorder.history)}"
        if not call_by_b_window and getattr(self,"b_window",None):
            self.b_window.refresh_map(True)

    # 点击棋子回调中转函数
    def click(self,x:int,y:int,key:int):
        x = self.getx(x)
        y = self.gety(y)
        def wrapper(event = None):
            if key == 1: # 左键
                if self.belong == self.game.turn:
                    turn = self.game.turn
                    state = self.game.click((x,y))
                    if state == "walk":
                        self.mess_label["text"] = f"{'红方' if turn == 1 else '蓝方'}将军！" if self.game.is_mess(turn) else ""
                    if state == "choose":
                        self.choose(*self.game.chosen)
                    else:
                        self.refresh_map()
                return
            else:
                chess = self.game.map_data.chessboard[x][y]
                if not chess:
                    return
            if key == 3: # 右键
                self.chess_info(chess)
                return
            else:
                if self.game.chosen and self.game.turn == self.belong:
                    return
            if key == 4: # 进入
                self.choose(None,self.game.get_can_go(chess,(x,y)))
            elif key == 5: # 离开
                self.choose(None,self.game.get_can_go(chess,(x,y)),remove = True)
        return wrapper

    def map_info(self):
        rules = {
            "tran":"启用升变",
            "back":"启用悔棋",
            "restrict_move_ne":"限制连续3步以上移动中立棋子"
        }
        info = "特殊规则：\n"
        for i in rules:
            info += f"{rules[i]}：{'是' if self.game.map_data.rules[i] else '否'}\n"
        exts = "\n    ".join([i.text() for i in ExtensionManager.Ext.extensions if i.use])
        if exts:
            info += f"已启用扩展：\n    {exts}"
        else:
            info = info[:-1]
        showinfo("地图信息",info)

    def chess_info(self,chess:Chess):
        belong = "红方" if chess.belong == 1 else "蓝方" if chess.belong == 2 else "中立"
        is_captain = "是" if chess.is_captain else "否"
        is_tran = ("是" if chess.is_tran else "否") if chess.tran_con else "无法升变"
        info = f"名称：{chess.name}\n编号：{chess.id}\n归属：{belong}\n首领棋子：{is_captain}\n是否升变：{is_tran}"
        if self.debug:
            if chess.attr:
                attr = "\n    ".join([f"{i}：{j}" for i,j in zip(chess.attr.keys(),chess.attr.values())])
                info += f"\n其他参数：\n    {attr}"
            move = chess.tran_move if chess.is_tran else chess.move
            show_move = ""
            for i in range(len(move)):
                if not move[i]:
                    continue
                show_move += f"\n    第{i + 1}项（{self.can_go_prompt_list[i]}）："
                for j in move[i]:
                    show_move += f"\n        方向{j[0]}："
                    if j[1:]:
                        show_move += f"{j[1:]}"
                    else:
                        show_move += "任意"
            info += f"\n目前可行走函数：{show_move}"
        showinfo("棋子信息",info)

    def choose(self,arr:ARR,can_go:list[ARR],remove:bool = False):
        if arr:
            bg = "chess-bg" if remove else "selected-chess-bg"
            self.chess_btn[self.getx(arr[0])][self.gety(arr[1])]["bg"] = self.colors[bg]
        for i in can_go:
            bg = "chess-bg" if remove else ("occupied-feasible-bg" if self.game.map_data.chessboard[i[0]][i[1]] else "blank-feasible-bg")
            self.chess_btn[self.getx(i[0])][self.gety(i[1])]["bg"] = self.colors[bg]

    # 在按钮上显示的文字及颜色
    def get_chess_text(self,chess:Chess) -> tuple[str,str]:
        if self.show_can_go_prompt:
            can_go_prompt = list[str]()
            now_move = chess.now_move # 先赋值中间变量，避免调用self.now_move属性时重新计算
            for i in range(1,9):
                is_add = False
                for j,k in enumerate(now_move):
                    if i in k:
                        if is_add: # 仅保留最后一项
                            del can_go_prompt[-1]
                        can_go_prompt.append(self.can_go_prompt_list[j])
                        is_add = True
                if not is_add:
                    can_go_prompt.append(" ")
            if self.belong == 2: # 反方棋盘
                can_go_prompt.reverse()
            # 生成名字
            name_withspace = chess.name
            name_length = len(chess.name.encode(encoding = "gbk"))
            side = True # True为右侧
            while name_length < 6:
                if side:
                    name_withspace += " "
                else:
                    name_withspace = " " + name_withspace
                side = not side
                name_length += 1
            can_go_prompt.insert(4,name_withspace)
            # 合并空格
            text = ""
            whitespace = ["   ","   ","\n","","","\n","   ","   ",""]
            for i in range(9):
                text += (can_go_prompt[i] + whitespace[i])
        else:
            text = chess.name
        # 设置颜色
        if chess.belong == 1:
            if chess.is_tran or not chess.tran_con:
                fg = "red-tran-chess-fg"
            else:
                fg = "red-chess-fg"
        elif chess.belong == 2:
            if chess.is_tran or not chess.tran_con:
                fg = "blue-tran-chess-fg"
            else:
                fg = "blue-chess-fg"
        else:
            fg = "neutral-chess-fg"
        return text,self.colors[fg]
