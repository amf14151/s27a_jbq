import os
import sys

from .__constants__ import __version__

def generate_game(game_path:str,display:str):
    import os
    if os.path.exists(game_path):
        return False
    os.mkdir(game_path)
    if display == "window":
        os.mkdir(os.path.join(game_path,"map"))
        os.mkdir(os.path.join(game_path,"extensions"))
        with open(os.path.join(game_path,"JBQ.py"),"w",encoding = "utf-8") as wfile:
            wfile.write("from s27a_jbq.game import App\n")
            wfile.write("\n")
            wfile.write("""def main():
    app = App()
    app.run()

if __name__ == "__main__":
    main()
""")
    else:
        return False
    return True

def main():
    try:
        command = sys.argv[1]
        args = sys.argv[2:]
        if command == "help":
            print("联网帮助请查看https://github.com/amf14151/s27a_jbq/blob/main/README.md")
            print("")
            print("可使用命令：")
            print("\thelp\t\t获取帮助")
            print("\tversion\t\t获取当前游戏版本")
            print("\tgenerate_game\t生成游戏文件夹（详情见联网帮助）")
        elif command == "version":
            print(f"精班棋游戏版本：{__version__}")
        elif command == "generate_game":
            game_path = os.path.abspath(args[0])
            display = args[1]
            if display != "window":
                print("display选项需要为以下值中的一个：")
                print("\twindow")
                return
            print(f"游戏文件夹路径：{game_path}")
            print(f"游戏运行方式：{display}")
            ans = input("是否确认创建文件夹？(y/n)").lower()
            if ans == "y":
                ok = generate_game(game_path,display)
                if ok:
                    print("创建成功")
                else:
                    print("创建失败")
            else:
                print("已取消创建")
        else:
            raise
    except:
        print("请输入'help'来获取帮助")

# 当被命令行调用时运行
if __name__ == "__main__":
    main()
