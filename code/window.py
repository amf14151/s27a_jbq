import tkinter as tk
import webbrowser

from tkinter.messagebox import showinfo
from tkinter.filedialog import askopenfilename

from .__constants__ import __version__
from .static import ARR,RELEASE_DATE,static_data,refresh_extension,refresh_color
from .map import Map
from .extension import Extension,ExtensionManager

class MainWindow(tk.Tk):
    def __init__(self,app_api:dict,debug:bool):
        super().__init__()
        self.app_api = app_api
        self.title(f"精班棋 {__version__}{' [debug mode]' if debug else ''}")
        self.minsize(480,360)
        self.resizable(width = False,height = False)
        self.start_btn = tk.Button(self,text = "开始游戏",width = 60,height = 3,**static_data["shape-style"]["btn-style"],command = self.app_api["start_game"])
        self.start_btn.pack(pady = 5)
        self.map_label = tk.Label(self,text = "未选择地图",width = 60,height = 3,**static_data["shape-style"]["label-style"])
        self.map_label.pack(pady = 5)
        self.map_btn_frame = tk.Frame(self)
        self.map_btn_frame.pack(pady = 5)
        self.get_map_btn = tk.Button(self.map_btn_frame,text = "选择地图",width = 15,height = 2,**static_data["shape-style"]["btn-style"],command = self.app_api["get_map"])
        self.get_map_btn.pack(side = "left",padx = 5)
        self.refresh_map_btn = tk.Button(self.map_btn_frame,text = "刷新地图",width = 15,height = 2,**static_data["shape-style"]["btn-style"],command = self.app_api["refresh_map"])
        self.refresh_map_btn.pack(side = "right",padx = 5)
        self.extension_label = tk.Label(self,width = 60,**static_data["shape-style"]["label-style"])
        self.extension_label.pack(pady = 5)
        self.set_extension_btn = tk.Button(self,text = "设置扩展",width = 15,height = 2,**static_data["shape-style"]["btn-style"],command = self.app_api["setting"])
        self.set_extension_btn.pack(pady = 5)

        self.refresh_extension()
        self.init_menu()

    # 初始化菜单栏
    def init_menu(self):
        self.menu = tk.Menu(self)
        self.config(menu = self.menu)
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
        self.game_menu.add_command(label = "开始游戏",command = self.app_api["start_game"])
        # 帮助菜单
        self.help_menu = tk.Menu(self.menu,tearoff = False)
        self.menu.add_cascade(label = "帮助(H)",underline = 3,menu = self.help_menu)
        self.help_menu.add_command(label = "精班棋文档",command = self.open_url("https://github.com/amf14151/s27a_jbq/blob/main/README.md"))
        self.help_menu.add_command(label = "获取地图",command = self.open_url("https://github.com/amf14151/s27a_jbq/tree/main/map"))
        self.help_menu.add_command(label = "获取扩展",command = self.open_url("https://github.com/amf14151/s27a_jbq/tree/main/extensions"))
        self.help_menu.add_separator()
        self.help_menu.add_command(label = "反馈",command = self.open_url("https://github.com/amf14151/s27a_jbq/issues"))
        self.help_menu.add_separator()
        self.help_menu.add_command(label = "关于精班棋",command = self.show_about)

    def choose_map_file(self):
        filename = askopenfilename(filetypes = [("Excel Files","*.xlsx"),("All Files","*.*")],title = "选择地图文件")
        return filename
    
    def choose_extension_file(self):
        filename = askopenfilename(filetypes = [("Python Files","*.py")],title = "选择扩展文件")
        return filename

    def refresh_extension(self):
        refresh_extension(ExtensionManager.Ext.extensions)
        ext = "\n".join([(i.text() + ("" if i.use else "(未启用)")) for i in ExtensionManager.Ext.extensions])
        self.extension_label["text"] = f"当前已加载扩展：\n{ext}" if ext else "未加载扩展"

    def set_map(self,filename:str):
        self.map_label["text"] = f"当前地图: \n{filename}"

    def open_url(self,url:str):
        return lambda:webbrowser.open(url)

    def show_about(self):
        showinfo("关于精班棋",f"版本: {__version__}\n发布日期: {RELEASE_DATE}")

class GameWindow(tk.Tk):
    def __init__(self,belong:int,map_data:Map,game_api:dict):
        super().__init__()
        self.belong = belong
        self.map_data = map_data
        self.game_api = game_api
        self.can_go_prompt_list = ["·","*","o","x"]
        self.title("红方" if self.belong == 1 else "蓝方")
        self.resizable(width = False,height = False)
        self.protocol("WM_DELETE_WINDOW",self.game_api["stop"])
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
        self.game_menu.add_command(label = "退出游戏",accelerator = "Alt+F4",command = self.game_api["stop"])
        # 功能菜单
        self.func_menu = tk.Menu(self.menu,tearoff = False)
        self.menu.add_cascade(label = "功能(F)",underline = 3,menu = self.func_menu)
        if True and self.map_data.rules["back"]: # 仅在单人模式下生效
            self.func_menu.add_command(label = "悔棋",command = lambda:self.game_api["back"](1))
            self.func_menu.add_command(label = "撤销悔棋",command = lambda:self.game_api["back"](-1))
            self.func_menu.add_separator()
        self.func_menu.add_command(label = "切换棋子大小",command = self.change_chess_height)

    def map_info(self):
        rules = {
            "tran":"启用升变",
            "back":"启用悔棋",
            "restrict_move_ne":"限制连续3步以上移动中立棋子"
        }
        info = "特殊规则：\n"
        for i in rules:
            info += f"{rules[i]}：{'是' if self.map_data.rules[i] else '否'}\n"
        exts = "\n    ".join([i.text() for i in ExtensionManager.Ext.extensions if i.use])
        if exts:
            info += f"已启用扩展：\n    {exts}"
        else:
            info = info[:-1]
        showinfo("地图信息",info)

    def change_chess_height(self):
        for i in self.chess_btn:
            for j in i:
                if j["height"] == 3: # 大棋子
                    j["height"] = 2
                    j["width"] = 5
                else:
                    j["height"] = 3
                    j["width"] = 8

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
                self.chess_btn[-1].append(tk.Button(self.chess_frame,height = 3,width = 8,relief = "flat",bd = 0,command = self.click(i,j,1)))
                self.chess_btn[-1][-1].bind("<Button 3>",self.click(i,j,3))
                self.chess_btn[-1][-1].grid(row = i,column = j,padx = 1,pady = 1)
        self.chess_frame.pack()
        self.mess_label = tk.Label(self,height = 3,width = 24)
        self.mess_label.pack()
        if len(self.chess_btn) > 8 or len(self.chess_btn[0]) > 12:
            self.change_chess_height()

    # 点击棋子回调中转函数
    def click(self,x:int,y:int,key:int):
        def wrapper(event = None):
            if key == 1:
                self.game_api["click"]((self.getx(x),self.gety(y)),self.belong)
            else:
                self.game_api["info"]((self.getx(x),self.gety(y)))
        return wrapper

    def set_text(self,type:str,fro:int,turn:tuple = None):
        if type == "turn": # 设置回合
            self.turn_label["text"] = f"{'己方' if fro == self.belong else '对方'}回合\n回合数：{turn[0]}/{turn[1]}"
        elif type == "mess": # 设置将军
            self.mess_label["text"] = f"{'红方' if fro == 1 else '蓝方'}将军！" if fro else ""

    def choose(self,can_go:list[ARR],remove:bool = False):
        for i in can_go:
            bg = "chess-bg" if remove else ("occupied-feasible-bg" if self.map_data.chessboard[i[0]][i[1]] else "blank-feasible-bg")
            self.chess_btn[self.getx(i[0])][self.gety(i[1])]["bg"] = static_data["colors"][bg]

    def refresh_map(self):
        for i in range(self.map_data.rl):
            for j in range(self.map_data.cl):
                chess = self.map_data.chessboard[self.getx(i)][self.gety(j)]
                if chess:
                    text,fg = self.get_chess_text(chess)
                    self.chess_btn[i][j]["text"] = text
                    self.chess_btn[i][j]["fg"] = fg
                else:
                    self.chess_btn[i][j]["text"] = ""
                self.chess_btn[i][j]["bg"] = static_data["colors"]["chess-bg"]

    # 在按钮上显示的文字及颜色
    def get_chess_text(self,chess):
        can_go_prompt = list[str]()
        now_move = chess.now_move # 先赋值中间变量，避免调用self.now_move属性时重新计算
        for i in range(1,9):
            is_add = False
            for j,k in enumerate(now_move):
                if i in k:
                    can_go_prompt.append(self.can_go_prompt_list[j])
                    is_add = True
                    break
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
        return text,static_data["colors"][fg]

class SettingWindow(tk.Tk):
    def __init__(self,add_ext_func,refresh_ext_func):
        super().__init__()
        self.title("设置")
        self.minsize(480,360)
        self.resizable(width = False,height = False)
        self.main_frame = tk.Frame(self) # 解决布局分布在两侧的问题
        self.main_frame.pack()
        # 扩展
        self.extension_frame = tk.Frame(self.main_frame)
        self.extension_frame.pack(side = "left",fill = "y",padx = 18)
        self.extension_label = tk.Label(self.extension_frame,text = "已加载扩展",width = 24,height = 2,**static_data["shape-style"]["label-style"])
        self.extension_label.pack(pady = 5)
        self.extension_btns = list[tk.Button]()
        for i in ExtensionManager.Ext.extensions:
            self.extension_btns.append(tk.Button(self.extension_frame,text = i.text(),width = 20,**static_data["shape-style"]["btn-style"]))
            self.extension_btns[-1]["bg"] = "lightgreen" if i.use else "pink"
            self.extension_btns[-1]["command"] = self.use_extension(self.extension_btns[-1],i,refresh_ext_func)
            self.extension_btns[-1].pack(pady = 5)
        self.add_extension_btn = tk.Button(self.extension_frame,text = "添加扩展",width = 16,height = 2,**static_data["shape-style"]["btn-style"],command = add_ext_func)
        self.add_extension_btn.pack(pady = 5)
        # 颜色样式
        self.color_style_frame = tk.Frame(self.main_frame)
        self.color_style_frame.pack(side = "right",fill = "y",padx = 18)
        self.set_color_style_label = tk.Label(self.color_style_frame,text = "设置颜色样式",width = 24,height = 2,**static_data["shape-style"]["label-style"])
        self.set_color_style_label.pack(pady = 5)
        self.set_color_style_var = tk.StringVar()
        self.set_color_style_radius = list[tk.Radiobutton]()
        for i in static_data["color-styles"]:
            self.set_color_style_radius.append(tk.Radiobutton(self.color_style_frame,text = i[1],variable = self.set_color_style_var,value = i[0],command = self.set_color(i[0])))
            if i[0] == static_data["color-style-name"]:
                self.set_color_style_radius[-1].select()
            self.set_color_style_radius[-1].pack(pady = 5)

    def use_extension(self,button:tk.Button,extension:Extension,refresh_ext_func):
        def wrapper():
            extension.use = not extension.use
            button["bg"] = "lightgreen" if extension.use else "pink"
            refresh_ext_func()
        return wrapper

    def set_color(self,value:str):
        return lambda:refresh_color(value)
