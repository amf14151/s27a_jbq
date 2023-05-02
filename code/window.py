import tkinter as tk
import webbrowser as wb
from tkinter.messagebox import showinfo
from tkinter.filedialog import askopenfilename

from .static import ARR,check_update,static_data,refresh_color
from .map import Map

class MainWindow(tk.Tk):
    def __init__(self,app_api:dict,debug:bool):
        super().__init__()
        self.app_api = app_api
        self.title(f"精班棋 {static_data['VERSION']}{' [debug mode]' if debug else ''}")
        self.geometry("480x280")
        self.resizable(width = False,height = False)
        self.start_btn = tk.Button(self,text = "单人游戏",width = 60,height = 3,**static_data["btn-style"],command = self.app_api["start_game"])
        self.start_btn.pack(pady = 5)
        self.map_label = tk.Label(self,text = "暂未选择",width = 60,height = 3,**static_data["btn-style"])
        self.map_label.pack(pady = 5)
        self.map_btn_frame = tk.Frame(self)
        self.map_btn_frame.pack(pady = 5)
        self.get_map_btn = tk.Button(self.map_btn_frame,text = "选择地图",width = 15,height = 2,**static_data["btn-style"],command = self.app_api["get_map"])
        self.get_map_btn.pack(side = "left",padx = 5)
        self.refresh_map_btn = tk.Button(self.map_btn_frame,text = "刷新地图",width = 15,height = 2,**static_data["btn-style"],command = self.app_api["refresh_map"])
        self.refresh_map_btn.pack(side = "right",padx = 5)
        self.init_menu()

    # 初始化菜单栏
    def init_menu(self):
        self.menu = tk.Menu(self)
        # 文件菜单
        self.file_menu = tk.Menu(self.menu,tearoff = False)
        self.menu.add_cascade(label = "文件(F)",underline = 3,menu = self.file_menu)
        self.file_menu.add_command(label = "选择地图",command = self.app_api["get_map"])
        self.file_menu.add_command(label = "刷新地图",command = self.app_api["refresh_map"])
        self.file_menu.add_separator()
        self.file_menu.add_command(label = "设置",command = self.app_api["setting"])
        self.file_menu.add_separator()
        self.file_menu.add_command(label = "退出",accelerator = "Alt+F4",command = self.destroy)
        # 游戏菜单
        self.game_menu = tk.Menu(self.menu,tearoff = False)
        self.menu.add_cascade(label = "游戏(G)",underline = 3,menu = self.game_menu)
        self.game_menu.add_command(label = "单人游戏",command = self.app_api["start_game"])
        self.game_menu.add_separator()
        self.game_menu.add_command(label = "新建对局",command = self.app_api["create_room"])
        self.game_menu.add_command(label = "加入对局",command = self.app_api["enter_room"])
        self.config(menu = self.menu)
        # 帮助菜单
        self.help_menu = tk.Menu(self.menu,tearoff = False)
        self.menu.add_cascade(label = "帮助(H)",underline = 3,menu = self.help_menu)
        self.help_menu.add_command(label = "精班棋文档",command = lambda:wb.open("https://github.com/amf14151/s27a_jbq/README.md"))
        self.help_menu.add_separator()
        self.help_menu.add_command(label = "反馈",command = lambda:wb.open("https://github.com/amf14151/s27a_jbq"))
        self.help_menu.add_command(label = "检查更新",command = check_update)
        self.help_menu.add_separator()
        self.help_menu.add_command(label = "关于精班棋",command = self.show_about)

    def choose_map_file(self):
        filename = askopenfilename(filetypes = [("Excel Files","*.xls *.xlsx"),("All Files","*.*")],title = "选择地图文件")
        return filename
    
    def set_map(self,filename:str):
        self.map_label["text"] = f"当前地图: \n{filename}"

    def show_about(self):
        showinfo("关于精班棋",static_data["about"].format(static_data["VERSION"]))

class GameWindow(tk.Tk):
    def __init__(self,belong:int,map_data:Map,click_func,info_func,stop_func):
        super().__init__()
        self.belong = belong
        self.map_data = map_data
        self.click_func = click_func
        self.info_func = info_func
        self.title("红方" if self.belong == 1 else "蓝方")
        self.resizable(width = False,height = False)
        self.protocol("WM_DELETE_WINDOW",stop_func)
        self.init_chessboard()
        self.refresh_map()

    #反方棋盘渲染反转横纵坐标
    def getx(self,x:int):
        return x if self.belong == 1 else self.map_data.rl - x - 1

    def gety(self,y:int):
        return y if self.belong == 1 else self.map_data.cl - y - 1

    def init_chessboard(self):
        self.turn_label = tk.Label(self,height = 3,width = 24,bg = static_data["colors"][f"{'red' if self.belong == 1 else 'blue'}-label"]) # 回合提示
        self.turn_label.pack()
        self.chess_frame = tk.Frame(self,bg = static_data["colors"]["chessboard"])
        self.chess_btn = list[list[tk.Button]]()
        for i in range(self.map_data.rl):
            self.chess_btn.append([])
            for j in range(self.map_data.cl):
                self.chess_btn[-1].append(tk.Button(self.chess_frame,height = 3,width = 8,relief = "flat",bd = 0,command = self.click(i,j)))
                self.chess_btn[-1][-1].bind("<Button 3>",self.click(i,j,True))
                self.chess_btn[-1][-1].grid(row = i,column = j,padx = 1,pady = 1)
        self.chess_frame.pack()
        self.mess_label = tk.Label(self,height = 3,width = 24)
        self.mess_label.pack()

    # 点击棋子回调中转函数
    def click(self,x:int,y:int,info:bool = False):
        def wrapper(event = None):
            if info:
                self.info_func((self.getx(x),self.gety(y)))
            else:
                self.click_func((self.getx(x),self.gety(y)),self.belong)
        return wrapper

    def set_turn(self,turn:int):
        self.turn_label["text"] = f"{'己方' if turn == self.belong else '对方'}回合"

    def choose(self,can_go:list[ARR]):
        for i in can_go:
            bg = static_data["colors"]["occupied-feasible-bg" if self.map_data.chessboard[i[0]][i[1]] else "blank-feasible-bg"]
            self.chess_btn[self.getx(i[0])][self.gety(i[1])]["bg"] = bg

    def remove_choose(self,can_go:list[ARR]):
        for i in can_go:
            self.chess_btn[self.getx(i[0])][self.gety(i[1])]["bg"] = static_data["colors"]["chess-bg"]

    def refresh_map(self):
        for i in range(self.map_data.rl):
            for j in range(self.map_data.cl):
                chess = self.map_data.chessboard[self.getx(i)][self.gety(j)]
                if chess:
                    self.chess_btn[i][j]["text"] = chess.text(self.belong == 2)
                    self.chess_btn[i][j]["fg"] = chess.fg
                else:
                    self.chess_btn[i][j]["text"] = ""
                self.chess_btn[i][j]["bg"] = static_data["colors"]["chess-bg"]

class SettingWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("设置")
        self.geometry("240x180")
        self.resizable(width = False,height = False)
        # 颜色样式
        self.set_color_style_label = tk.Label(self,text = "设置颜色样式",width = 20,height = 2)
        self.set_color_style_label.pack(pady = 5)
        self.set_color_style_var = tk.StringVar()
        self.set_color_style_radius = list[tk.Radiobutton]()
        for i in static_data["color-styles"]:
            self.set_color_style_radius.append(tk.Radiobutton(self,text = i[1],variable = self.set_color_style_var,value = i[0],command = self.set_color(i[0])))
            if i[0] == static_data["color-style-name"]:
                self.set_color_style_radius[-1].select()
            self.set_color_style_radius[-1].pack(pady = 5)

    def set_color(self,value:str):
        return lambda:refresh_color(value)
