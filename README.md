# 自动扫雷

记录一个自动模拟扫雷demo。在此项目基础上可以延申为物理模拟的自动化脚本控制。

## 功能

通过视觉对扫雷游戏中的单元进行识别，然后整合逻辑，通过模拟鼠标的移动与点击实现自动扫雷的效果。

[扫雷游戏的链接URL](https://saolei.pages.dev/) :point_left:

<font color=blue>效果如下:</font>(Here is a gif) :point_down::relaxed:

<img src="https://github.com/ZHOU-HN/Automatic-Minesweeper/blob/main/scanMine.gif" width="600px">

## 待优化

+ 可以加入多线程
+ 为了实现功能简单用了模板匹配来做的识别，想要程序更加健壮的话，可以用网络来做识别

## 环境

+ python 3.7.16
+ PyAutoGUI 0.9.54
+ keyboard 0.13.5
+ opencv-python 4.10.0.84
