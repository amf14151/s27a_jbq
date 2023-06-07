import sys
if sys.platform != "win32":
    sys.stdout("窗口式应用必须在Windows系统中运行")
    sys.exit()

import os
import shutil

import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showinfo,showerror,askyesno
from tkinter.filedialog import askopenfilename,asksaveasfilename

from ..__constants__ import __version__
from ..game import Game
from ..game.map import Map
from ..game.static import MapViewer
from ..game.extension import ExtensionManager,Extension
from .game_window import GameWindow
from .setting import COLOR_STYLES,Setting,save_record

class WindowApp(tk.Tk):
    EXTENSION_PATH = "extensions"
    def __init__(self,debug:bool = False):
        super().__init__()
        self.debug = debug
        self.setting = Setting()
        self.ext_manager = ExtensionManager()
        if not os.path.exists(WindowApp.EXTENSION_PATH):
            os.mkdir(WindowApp.EXTENSION_PATH)
        for i in os.listdir(WindowApp.EXTENSION_PATH):
            path = os.path.join(WindowApp.EXTENSION_PATH,i)
            if self.debug:
                self.ext_manager.load_extension(path)
            else:
                try:
                    self.ext_manager.load_extension(path)
                except:
                    ans = askyesno("错误",f"扩展{path}导入错误，是否删除此扩展？")
                    if ans:
                        os.remove(path)
        self.title(f"精班棋 {__version__}{' [debug mode]' if debug else ''}")
        self.minsize(600,360)
        self.geometry("720x480")
        self.init_style()
        self.init_window()
        self.set_game_mode(11)
        self.map_data = None
        if self.debug:
            self.get_map(True)
        else:
            try:
                self.get_map(True)
            except:
                pass
        self.refresh_extension_style()

    def init_style(self):
        ttk.Style(self).configure("Main.TNotebook")
        ttk.Style(self).configure("Main.TFrame",background = "lightskyblue")
        ttk.Style(self).configure("Main.StartGame.TButton",background = "lightskyblue",font = ("新宋体",16))
        ttk.Style(self).configure("Main.Info.TLabel",background = "lightskyblue",font = ("新宋体",11))
        ttk.Style(self).configure("Main.Ext.TLabel")
        ttk.Style(self).configure("Main.TMenubutton",background = "white",font = ("新宋体",12))
        ttk.Style(self).configure("Main.TButton",background = "lightskyblue")
        ttk.Style(self).configure("Main.TRadiobutton",background = "lightskyblue",font = ("新宋体",11))

    def init_window(self):
        self.tabs = ttk.Notebook(self,style = "Main.TNotebook")
        self.tabs.pack(expand = True,fill = "both")
        # 游戏窗口
        self.game_frame = ttk.Frame(self)
        self.tabs.add(self.game_frame,text = "精班棋")
        self.start_game_frame = ttk.Frame(self.game_frame,style = "Main.TFrame")
        self.start_game_frame.pack(fill = "y",side = "left",padx = 12,pady = 12)
        self.start_game_btn = ttk.Button(self.start_game_frame,padding = 12,text = "开始游戏",width = 16,style = "Main.StartGame.TButton",command = self.start_game)
        self.start_game_btn.pack(padx = 8,pady = 4)
        self.game_mode_menu = tk.Menu(self,tearoff = 0)
        self.game_mode_menu.add_command(label = "单人模式",command = lambda:self.set_game_mode(11))
        self.game_mode_menu.add_command(label = "残局模式",command = lambda:self.set_game_mode(12))
        self.game_mode_menu.add_separator()
        self.game_mode_menu.add_command(label = "联机模式",command = lambda:self.set_game_mode(21))
        self.game_mode_menubtn = ttk.Menubutton(self.start_game_frame,menu = self.game_mode_menu,padding = 8,width = 20,style = "Main.TMenubutton")
        self.game_mode_menubtn.pack(padx = 8,pady = 4)
        self.map_frame = ttk.Frame(self.game_frame,style = "Main.TFrame")
        self.map_frame.pack(expand = True,fill = "both",side = "right",padx = 12,pady = 12)
        self.map_title_label = ttk.Label(self.map_frame,text = "当前已选择地图",style = "Main.Info.TLabel")
        self.map_title_label.pack(fill = "x",padx = 8,pady = 4)
        self.map_file_frame = ttk.Frame(self.map_frame)
        self.map_file_frame.pack(fill = "x",padx = 8,pady = 4)
        self.map_file_btn = ttk.Button(self.map_file_frame,text = "选择地图",style = "Main.TButton",command = lambda:self.get_map(False))
        self.map_file_btn.pack(side = "right")
        self.map_file_entry = ttk.Entry(self.map_file_frame,width = 360,state = "read")
        self.map_file_entry.pack(side = "right")
        # 扩展窗口
        self.extension_frame = ttk.Frame(self)
        self.tabs.add(self.extension_frame,text = "扩展")
        self.i_extension_frame = ttk.Frame(self.extension_frame,style = "Main.TFrame")
        self.i_extension_frame.pack(expand = True,fill = "both",padx = 12,pady = 12)
        self.add_extension_btn = ttk.Button(self.i_extension_frame,padding = 4,text = "导入扩展",width = 36,style = "Main.TButton",command = self.add_extension)
        self.add_extension_btn.grid(row = 0,column = 0,columnspan = 2,padx = 8,pady = 4)
        self.extensions = list[list[tk.Button,ttk.Label,Extension]]()
        for i,j in enumerate(self.ext_manager.extensions):
            j.use = j.name in self.setting["used-extensions"]
            self.extensions.append([])
            self.extensions[-1].append(tk.Button(self.i_extension_frame,width = 3,command = self.change_extension(j)))
            self.extensions[-1][-1].grid(row = i + 1,column = 0,padx = 8,pady = 4)
            self.extensions[-1].append(ttk.Label(self.i_extension_frame,padding = 4,text = j.text(),width = 36,style = "Main.Ext.TLabel"))
            self.extensions[-1][-1].grid(row = i + 1,column = 1,pady = 4)
            self.extensions[-1].append(j)
        # 设置窗口
        self.setting_frame = ttk.Frame(self)
        self.tabs.add(self.setting_frame,text = "设置")
        self.i_setting_frame = ttk.Frame(self.setting_frame,style = "Main.TFrame")
        self.i_setting_frame.pack(expand = True,fill = "both",padx = 12,pady = 12)
        self.record_title_label = ttk.Label(self.i_setting_frame,text = "设置棋局记录文件",style = "Main.Info.TLabel")
        self.record_title_label.pack(fill = "x",padx = 8,pady = 4)
        self.record_file_frame = ttk.Frame(self.i_setting_frame)
        self.record_file_frame.pack(fill = "x",padx = 8,pady = 4)
        self.record_file_btn = ttk.Button(self.record_file_frame,text = "选择文件",style = "Main.TButton",command = self.choose_record)
        self.record_file_btn.pack(side = "right")
        self.record_file_entry = ttk.Entry(self.record_file_frame,width = 360)
        self.record_file_entry.insert(0,self.setting["record-path"])
        self.record_file_entry["state"] = "read"
        self.record_file_entry.pack(side = "right")
        self.color_title_label = ttk.Label(self.i_setting_frame,text = "设置颜色样式",style = "Main.Info.TLabel")
        self.color_title_label.pack(fill = "x",padx = 8,pady = 4)
        self.color_radiobtns = list[ttk.Radiobutton]()
        for i in COLOR_STYLES:
            self.color_radiobtns.append(ttk.Radiobutton(self.i_setting_frame,text = COLOR_STYLES[i]["name"],value = i,style = "Main.TRadiobutton",command = self.choose_color(i)))
            if i == self.setting["color-styles"]:
                self.color_radiobtns[-1].invoke()
            self.color_radiobtns[-1].pack(fill = "x",padx = 8,pady = 4)

    def start_game(self):
        if self.game_mode != 11:
            showinfo("提示","目前仅支持单人模式")
            return
        if not self.map_data:
            showinfo("提示","请选择地图")
            return
        self.withdraw()
        def wrapper():
            game = Game(self.map_data,self.ext_manager)
            game.start()
            red_window = GameWindow(1,game,self.debug)
            blue_window = GameWindow(2,game,self.debug)
            red_window.bind_window(blue_window)
            blue_window.bind_window(red_window)
            while game.running:
                red_window.update()
                blue_window.update()
            if game.stop_type == "red":
                showinfo("提示","红方胜利")
            elif game.stop_type == "blue":
                showinfo("提示","蓝方胜利")
            elif game.stop_type == "stalemate":
                showinfo("提示","和棋")
            red_window.destroy()
            blue_window.destroy()
            try:
                save_record(game.recorder.history,self.setting["record-path"]) # 记录棋局
            except PermissionError:
                showerror("错误","棋局记录文件被占用")
        if self.debug:
            wrapper()
        else:
            try:
                wrapper()
            except Exception as e:
                showerror("错误",f"游戏运行错误：{e}")
        self.deiconify()

    def set_game_mode(self,mode:int):
        self.game_mode_menubtn["text"] = {
            11:"单人模式",
            12:"残局模式",
            21:"联机模式"
        }[mode]
        self.game_mode = mode

    def get_map(self,from_record:bool):
        if from_record:
            path = self.setting["lastly-load-map"]
        else:
            path = askopenfilename(filetypes = [("Excel Files","*.xlsx"),("All Files","*.*")],title = "选择地图文件")
        if not path:
            return
        if self.debug:
            self.map_data = Map(*MapViewer.view(path))
        else:
            try:
                self.map_data = Map(*MapViewer.view(path))
            except:
                if not from_record:
                    showerror("错误","地图文件格式错误")
                return
        self.map_file_entry["state"] = "normal"
        self.map_file_entry.delete(0,"end")
        self.map_file_entry.insert(0,path)
        self.map_file_entry["state"] = "read"
        self.setting["lastly-load-map"] = path

    def refresh_extension_style(self):
        for i in self.extensions:
            if i[2].use:
                i[0]["bg"] = "lightgreen"
            else:
                i[0]["bg"] = "pink"

    def add_extension(self):
        path = askopenfilename(filetypes = [("Python Files","*.py")],title = "选择扩展文件")
        if (not path) or os.path.splitext(path)[1] != ".py":
            return
        copy_path = os.path.join(WindowApp.EXTENSION_PATH,os.path.split(path)[-1])
        try:
            shutil.copy(path,copy_path)
        except shutil.SameFileError:
            showerror("错误","该文件已被导入")
        extension = self.load_extension(copy_path)
        if extension:
            self.extensions.append([])
            self.extensions[-1].append(tk.Button(self.i_extension_frame,width = 3,command = self.change_extension(extension)))
            self.extensions[-1][-1].grid(row = len(self.extensions) + 1,column = 0,padx = 8,pady = 4)
            self.extensions[-1].append(ttk.Label(self.i_extension_frame,padding = 4,text = extension.text(),width = 36,style = "Main.Ext.TLabel"))
            self.extensions[-1][-1].grid(row = len(self.extensions) + 1,column = 1,pady = 4)
            self.extensions[-1].append(extension)
            self.refresh_extension_style()

    def change_extension(self,extension:Extension):
        def wrapper():
            extension.use = not extension.use
            used_ext = self.setting["used-extensions"]
            if extension.name in used_ext:
                used_ext.remove(extension.name)
            else:
                used_ext.append(extension.name)
            self.setting["used-extensions"] = used_ext
            self.refresh_extension_style()
        return wrapper

    def choose_record(self):
        path = asksaveasfilename(filetypes = [("CSV Files","*.csv"),("All Files","*.*")],initialfile = "游戏记录.csv",title = "选择棋局记录文件")
        self.record_file_entry["state"] = "normal"
        self.record_file_entry.delete(0,"end")
        self.record_file_entry.insert(0,path)
        self.record_file_entry["state"] = "read"
        self.setting["record-path"] = path

    def choose_color(self,color_styles_name:str):
        def wrapper():
            if self.setting["color-styles"] != color_styles_name:
                self.setting["color-styles"] = color_styles_name
        return wrapper

    def run(self):
        self.mainloop()
