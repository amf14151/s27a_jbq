# 精班棋

![](https://img.shields.io/badge/release-1.0.3-blue)
![](https://img.shields.io/badge/last%20commit-may-yellow)
![](https://img.shields.io/badge/license-MIT-green)

精班棋是一款自由度很高的棋类游戏

这款游戏的最大特点就是地图的可自定义性以及对于扩展插件的高度支持

运用这些，你可以在精班棋中还原出一些经典的棋类游戏

# 目录

- [精班棋](#精班棋)
- [目录](#目录)
- [安装](#安装)
- [使用方法](#使用方法)
- [许可证](#许可证)

# 安装

[(返回目录)](#目录)

您可以在[精班棋官网](https://amf14151.github.io/JBQ/)下载exe版本并获取对应的地图、扩展包，也可以按照下面的步骤安装模块并使用

## 安装模块

*若想通过模块的方式运行精班棋，您需要Python解释器*

使用以下命令来安装模块

```
python.exe -m pip install s27a_jbq
```

在安装`s27a_jbq`模块后，使用以下命令来构建游戏文件夹

```
python.exe -m s27a_jbq generate_game {游戏文件夹路径} {游戏运行方式}
```

其中，游戏运行方式有以下选择：

- `window`：窗口模式

示例：

```
python.exe -m s27a_jbq generate_game C:/JBQ window
```

上方的代码在C盘根目录中创建名为`JBQ`的游戏文件夹

您也可以在建立文件夹后直接使用以下代码构建主文件（不推荐）

``` python
from s27a_jbq.game import App

def main():
   app = App()
   app.run()
```

在游戏文件夹中有`extensions`文件夹，该文件夹用于存储扩展，扩展具体使用方法请看[这里](#扩展)

# 使用方法

[(返回目录)](#目录)

## 游戏过程

在设置好地图及扩展（具体方法请参见下文）后，点击开始游戏即可

游戏中，以红方为先手，双方依次移动棋子并尝试吃掉对方棋子，以先吃掉对方的首领棋子（任意1个即可）为胜利条件

每个棋子上会有可移动方向标注，在己方回合单击棋子即可查看该棋子具体可移动格子，右键棋子可以查看该棋子详细信息

一些棋子在不同的位置会有不同的可移动格子，每个棋子的具体可移动格子根据地图、扩展决定

在对局结束后，如果在设置中设置了棋局记录路径，则会对棋局进行记录

## 地图

地图文件是`.xlsx`文件，其中包含至少3个表，分别对应棋子、棋盘与特殊规则

地图文件中可能会有其他名称的表，这些表不会被程序读取，但内部可能会有该地图的说明信息

您可以在[这里](https://github.com/amf14151/s27a_jbq/tree/main/map)下载地图，也可以自定义地图（[查看帮助文档](https://amf14151.github.io/JBQ/help.html)）

## 扩展

扩展是`.py`文件，是用`Python`语言按照一定规则编写的一段代码块，运用扩展可以实现一些独特的行走方法及游戏规则

您可以在[这里](https://github.com/amf14151/s27a_jbq/tree/main/extensions)获取扩展，也可以自行编写扩展（[查看帮助文档](https://amf14151.github.io/JBQ/help.html)）

在游戏设置中可以导入扩展，也可以手动将扩展文件添加到游戏文件夹下的`extensions`文件夹下。扩展默认为禁用状态，可以在游戏设置中启用或禁用扩展

# 许可证

[(返回目录)](#目录)

[MIT License](https://github.com/amf14151/s27a_jbq/blob/main/LICENSE)
