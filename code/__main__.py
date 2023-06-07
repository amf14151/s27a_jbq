import os

from .__constants__ import __version__

def generate_game(game_path:str,display:str):
    import os
    if os.path.exists(game_path):
        return False
    os.mkdir(game_path)
    if display == "code":
        code = """from s27a_jbq.game import Game,MapViewer,Map,ExtensionManager

def main():
    map = Map(*MapViewer.view("[此处填写地图路径]"))
    ext_manager = ExtensionManager()
    ext_manager.load_extension("[此处填写扩展路径]")
    ext_manager.load_extension("[此处填写扩展路径]") # 可导入多次
    game = Game(map,ext_manager)
    game.start()
    while True:
        game.click(arr) # arr由代码决定

if __name__ == "__main__":
    main()
"""
    elif display == "window":
        code = """from s27a_jbq.window import WindowApp

def main():
    app = WindowApp()
    app.run()

if __name__ == "__main__":
    main()
"""
    else:
        return False
    with open(os.path.join(game_path,"JBQ.py"),"w",encoding = "utf-8") as wfile:
        wfile.write(code)
    return True

commands = ["生成游戏","帮助文档","关于精班棋","退出面板"]

def main():
    print("-" * 10 + "精班棋命令行面板" + "-" * 10)
    for i,j in enumerate(commands):
        print(f"{i + 1} {j}")
    while True:
        ans = input("请输入指令:")
        if ans == "1":
            game_path = os.path.abspath(input("请输入游戏文件夹路径:"))
            display = input("请输入游戏运行方式:")
            if display not in ["code","window"]:
                print("游戏运行方式需要为以下值中的一个：")
                print(" code")
                print(" window")
                print("具体内容请查看帮助文档")
                continue
            print(f"游戏文件夹路径:{game_path}")
            print(f"游戏运行方式:{display}")
            ans = input("是否确认创建文件夹？(y/n)").lower()
            if ans == "y":
                ok = generate_game(game_path,display)
                if ok:
                    print("创建成功")
                else:
                    print("创建失败")
            else:
                print("已取消创建")
        elif ans == "2":
            print("联网帮助请查看https://github.com/amf14151/s27a_jbq/blob/main/README.md")
        elif ans == "3":
            print("关于精班棋")
            print(f" 版本:{__version__}")
            print(f" 发布日期:2023.6.7")
        elif ans == "4":
            break

# 当被命令行调用时运行
if __name__ == "__main__":
    main()
