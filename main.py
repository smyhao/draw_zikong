import re
import sys
import matplotlib.pyplot as plt
import numpy as np
import os
import matplotlib.ticker as ticker
import time
from mplcursors import cursor
from colors import red, blue, cyan, magenta, yellow

# 初始化变量
i = 1
flag = 0
datalist = []
name = ''
second_data = 0
# 定义一个颜色列表，用于图中点的着色
color_list = ["#FF0050", "#F31040", "#FF7F03", "#70FF00", "#90F2FF", "#0A00FF", "#8B04FF", "#6F00FF", "#F2540D",
              "#0F7000", "#FF2F00", "#30FF00", "#04F9FF", "#0800FF", "#8B90FF", "#FF007F", "#F80000", "#FF7FA0",
              "#FFAA00", "#04FF30", "#10F5FF", "#D020FF", "#8B00DF", "#F30FF9"]

# 用于存储点击的点的字典，键为子图索引，值为点击的点的坐标列表
clicked_points_dict = {}


def click_write(ax_index, event, radius):
    """
    处理鼠标点击事件，根据点击类型添加或移除点击的点。

    :param ax_index: 子图索引
    :param event: 鼠标事件对象
    :param radius: 点的搜索半径，用于确定点击的点是否接近已存在的点
    """
    if event.button == 3:  # 右键点击

        # 获取点击坐标
        x, y = event.xdata, event.ydata
        print("点击了子图:", filelist[ax_index][:-4], ",点击位置为：", yellow(event.xdata), yellow(event.ydata))
        if x is not None and y is not None:  # 确保点击在图内
            # 如果字典中还没有这个子图的键，则初始化一个空列表
            if ax_index not in clicked_points_dict:
                clicked_points_dict[ax_index] = []

            # 查找点击附近的点
            nearby_points = [p for p in clicked_points_dict[ax_index] if
                             np.sqrt((p[0] - event.xdata) ** 2 + (p[1] - event.ydata) ** 2) <= radius]

            # 如果有附近的点，移除这些点
            if nearby_points:
                for point in nearby_points:
                    clicked_points_dict[ax_index].remove(point)
                    print("移除点2：", blue(point))
            # 否则，记录这个点击点
            else:
                clicked_points_dict[ax_index].append((x, y))

            # 清除子图上的旧文本和点
            for txt in event.inaxes.texts:
                txt.remove()
            for point in event.inaxes.lines:
                if point.get_color() == 'k':
                    point.remove()

            # 绘制新的点击点和对应的文本
            if clicked_points_dict[ax_index]:
                for x, y in clicked_points_dict[ax_index]:
                    event.inaxes.plot(x, y, 'ko', markersize=3)  # 在当前子图上绘制红点
                    event.inaxes.text(x, y, f'({x:.2f}, {y:.2f})', fontsize=8, color='blue')  # 添加坐标标签

            # 更新子图显示
            event.canvas.draw_idle()


def onclick(ax_index, event):
    """
    鼠标点击事件的处理函数。

    :param ax_index: 子图索引
    :param event: 鼠标事件对象
    """
    radius = 0.35
    global clicked_points_dict
    if event.inaxes is axs.flat[ax_index]:
        click_write(ax_index, event, radius)
    else:
        pass


def onclick_one(ax_index, event):
    """
    单击事件处理函数，用于单个子图。

    :param ax_index: 子图索引
    :param event: 鼠标事件对象
    """
    radius = 0.35
    global clicked_points_dict
    click_write(ax_index, event, radius)


# 如果datas文件夹不存在，则创建它
if not (os.path.isdir(".\\datas")):
    os.makedirs(".\\datas", exist_ok=True)
    print("检测到无datas文件夹，现已创建datas文件夹，请将数据文件夹放入")
# 获取数据文件列表
filename = os.listdir(".//datas")
while not len(filename):
    print("检测到无datas文件夹，请将数据文件夹放入")
    filename = os.listdir(".//datas")
    time.sleep(2)

# 根据用户输入决定处理单个还是多个文件
decide = input("处理数据为单文件(1)还是多文件(2)?\n")
if decide == "2":
    while True:
        try:
            print("当前datas下有：")
            print(magenta(filename))
            path = "//" + input("请输入要使用的文件夹名：\n")
            filelist = os.listdir(".//datas" + path)
            address = ".//datas" + path + "//" + filelist[0]
            break
        except FileNotFoundError:
            print("文件夹不存在，请检查路径")

elif decide == "1":
    while True:
        try:
            print("当前datas下有：")
            print(magenta(filename))
            path = "//" + input("请输入要使用的文件名：\n")
            address = ".//datas" + path
            filelist = ['']
        except FileNotFoundError:
            print("文件不存在，请检查路径")
else:
    sys.exit("您的程序已裂开")

# 读取数据文件的标题
with open(address, 'r', encoding='utf-8') as file:
    first_line: str = file.readline()
    line_first_title = list(map(str, re.split(r"\s+", first_line.strip())))
    max_length = max(len(s) for s in line_first_title)
    adjusted_str_list = [s.ljust(max_length) for s in line_first_title]
    print("数据标题为：")
    j = 0
    for title in adjusted_str_list:
        print('| '+cyan(str(j) + '.' + title), end='')
        if (j + 1) % 4 == 0:
            print("")
        j = j + 1

# 用户选择要使用的数据列
option = int(input("\n请输入要使用的数据编号：\n"))
# 用户选择是否使用副标题
if_subhead = input("是否使用副曲线（y/n）：\n")
if if_subhead == "y":
    subhead = int(input("请输入副曲线编号：\n"))
else:
    subhead = 0

# 用户输入缩放比例
change = float(input("请输入缩放比例(主曲线)：\n"))
if if_subhead == "y":
    change_sub = float(input("请输入缩放比例(副曲线)：\n"))
# 计算需要处理的文件数量
file_num = len(filelist)
if decide == "2":
    b = 2
    if file_num % 2 == 0:
        a = file_num // 2
    else:
        a = (file_num + 1) // 2
else:
    a = 1
    b = 1

# 读取并处理每个数据文件
for data in filelist:
    if decide == "2":
        address = ".//datas" + path + "//" + data
    else:
        address = ".//datas" + path
    name = path[2:]
    with open(address, 'r', encoding='utf-8') as file:
        file.readline()
        line = file.readline()
        data_array = []
        while line:
            num = list(map(float, re.split(r'\s+', line.strip())))
            data_array.append(num)
            line = file.readline()
        data_array = np.array(data_array)
    datalist.append(data_array)

# 创建子图并绘制数据
fig, axs = plt.subplots(a, b)

for data_array in datalist:
    main_data = data_array[:, option] * change
    if if_subhead == "y":
        second_data = data_array[:, subhead]*change_sub
    length = main_data.shape[0]
    time_start = data_array[0, 1]
    time_end = data_array[length - 1, 1]
    step = (time_end - time_start) / length
    time = np.arange(0, (step * length + 1), step, dtype=float)
    time = time[:length]
    ax = plt.subplot(a, b, i)
    ax.plot(time, main_data, color=color_list[i - 1])
    if if_subhead == "y":
        ax.plot(time, second_data, color=color_list[20 - i])
    ax.xaxis.set_minor_locator(ticker.AutoMinorLocator())
    ax.yaxis.set_minor_locator(ticker.AutoMinorLocator())
    ax.grid(True)
    ax.set_title(filelist[i - 1][:-4], fontsize=6, color=color_list[i - 1])
    i = i + 1

# 启用光标悬停功能
cursor(hover=True)
if decide == "2":
    for i, ax in enumerate(axs.flatten()):
        cid = fig.canvas.mpl_connect('button_press_event', lambda event, index=i: onclick(index, event))
else:
    cid1 = fig.canvas.mpl_connect('button_press_event', lambda event, index=0: onclick_one(index, event))

plt.suptitle(name, fontsize=20, color='red')
plt.subplots_adjust(left=0.035, bottom=0.04, right=0.965, top=0.960, wspace=0.165, hspace=0.6)

plt.show()
