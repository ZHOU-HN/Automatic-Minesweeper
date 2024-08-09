import pyautogui
import time
import keyboard
import cv2
import numpy as np
import os

# 初始化全局变量
game_area_top_left = None
game_area_bottom_right = None
cell_top_left = None
cell_bottom_right = None
cell_size = None
num_columns = 9  # 根据用户输入调整
num_rows = 9  # 根据用户输入调整
marked_mines = set()  # 存储已标记的雷的格子坐标
done_grid = set()   # 存储已经扫雷完成的格子坐标
do_nothing_flag = 1 # 如果为1，说明这一圈什么都没做
scanside_x = 0 # x扫描边界
scanside_y = 0 # y扫描边界

# 用于存储模板的字典
templates = {}

def get_mouse_click(prompt):
    """等待用户按下 's' 键并返回当前鼠标位置"""
    print(prompt)
    while True:
        if keyboard.is_pressed('s'):
            x, y = pyautogui.position()
            print(f"Mouse clicked at ({x}, {y})")
            time.sleep(1)  # 防止误触连续检测
            return (x, y)
        time.sleep(0.1)

def capture_template(name):
    """采集模板图片"""
    position = get_mouse_click(f"请将鼠标移动到{name}的格子，然后按下 's' 键")
    img = pyautogui.screenshot(region=(position[0], position[1], cell_size, cell_size))
    if not os.path.exists('templates'):
        os.makedirs('templates')
    img.save(f'templates/{name}.png')
    templates[name] = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    templates[name] = img
    print(f"{name} 模板已保存")

def load_templates():
    """加载模板图片"""
    template_names = ['0', '1', '2', '3', '4', '5', '6', '7', '8', 'mine', 'pushed', 'no-push']
    for name in template_names:
        if os.path.exists(f'templates/{name}.png'):
            templates[name] = cv2.imread(f'templates/{name}.png')

def click_cell(x, y, right_click=False):
    """点击指定的格子"""
    global do_nothing_flag
    global scanside_x
    global scanside_y

    do_nothing_flag = 0
    if right_click:
        pyautogui.click(game_area_top_left[0] + x * cell_size + cell_size // 2,
                        game_area_top_left[1] + y * cell_size + cell_size // 2,
                        button='right',
                        duration=0.1)
    else:
        pyautogui.click(game_area_top_left[0] + x * cell_size + cell_size // 2,
                        game_area_top_left[1] + y * cell_size + cell_size // 2,
                        duration=0.1)


def get_cell_image(x, y):
    """获取指定格子的截图"""
    return pyautogui.screenshot(region=(
        game_area_top_left[0] + x * cell_size - 5,
        game_area_top_left[1] + y * cell_size - 5,
        cell_size + 10, cell_size + 10))

def preprocess_image(image):
    """预处理图像，转换为灰度并调整大小"""
    # gray_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
    gray_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    resized_image = gray_image
    # resized_image = cv2.resize(gray_image, (cell_size, cell_size))
    return resized_image

def match_template(cell_image, template):
    """使用模板匹配识别格子内容"""
    cell_processed = preprocess_image(cell_image)
    # cell_processed = cell_processed[2:cell_processed.shape[0] - 2, 2:cell_processed.shape[1] - 2]
    # cell_processed = cv2.resize(cell_processed, (cell_size, cell_size))

    template_processed = template
    # template_processed = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)

    # template_processed = template_processed[ss2:template_processed.shape[0]-2, 2:template_processed.shape[1]-2]
    # template_processed = cv2.resize(template_processed, (cell_size, cell_size))
    result = cv2.matchTemplate(cell_processed, template_processed, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, _ = cv2.minMaxLoc(result)
    return max_val

def recognize_cell(x, y):
    if (x, y) in marked_mines:
        return 'mine'

    """识别指定格子的内容"""
    cell_image = get_cell_image(x, y)
    max_val = 0
    for name, template in templates.items():
        val = match_template(cell_image, template)
        if val > max_val:  # 记录匹配阈值
            final_name = name
            max_val = val
    if max_val > 0.5:
        return final_name
    return None

def get_neighbors(x, y):
    """获取指定格子周围的格子"""
    neighbors = []
    for dx in [-1, 0, 1]:
        for dy in [-1, 0, 1]:
            if dx == 0 and dy == 0:
                continue
            nx, ny = x + dx, y + dy
            if 0 <= nx < num_columns and 0 <= ny < num_rows:
                neighbors.append((nx, ny))
    return neighbors

def mark_mine(x, y):
    """标记地雷"""
    click_cell(x, y, right_click=True)
    marked_mines.add((x, y))

def recognize_and_mark_or_click(x, y):
    global scanside_x
    global scanside_y

    cell_content = recognize_cell(x, y)
    print("(" + str(x) + "," + str(y) + ")")
    if cell_content and cell_content.isdigit() and int(cell_content) > 0:
        scanside_x = max(scanside_x, x)
        scanside_y = max(scanside_y, y)

        number = int(cell_content)
        neighbors = get_neighbors(x, y)
        no_push_neighbors = [n for n in neighbors if (n not in marked_mines and recognize_cell(*n) == 'no-push')]
        mine_neighbors = [n for n in neighbors if n in marked_mines]

        if len(mine_neighbors) + len(no_push_neighbors) == number:
            done_grid.add((x, y))
            for nx, ny in no_push_neighbors:
                mark_mine(nx, ny)
        elif len(mine_neighbors) == number:
            done_grid.add((x, y))
            for nx, ny in no_push_neighbors:
                click_cell(nx, ny)
                recognize_and_mark_or_click(nx, ny)

def auto_play():
    """自动玩扫雷的主要逻辑"""
    global do_nothing_flag
    global scanside_x
    global scanside_y

    do_nothing_flag = 1
    for x in range(num_columns):
        for y in range(num_rows):
            if (x, y) in marked_mines:
                continue
            if (x, y) in done_grid:
                continue
            cell_content = recognize_cell(x, y)
            print("(" + str(x) + "," + str(y) + ")")
            if cell_content and cell_content.isdigit() and int(cell_content) > 0:
                scanside_x = max(scanside_x, x)
                scanside_y = max(scanside_y, y)

                number = int(cell_content)
                neighbors = get_neighbors(x, y)
                no_push_neighbors = [n for n in neighbors if (n not in marked_mines and recognize_cell(*n) == 'no-push')]
                mine_neighbors = [n for n in neighbors if n in marked_mines]

                if len(mine_neighbors) + len(no_push_neighbors) == number:
                    done_grid.add((x, y))
                    for nx, ny in no_push_neighbors:
                        mark_mine(nx, ny)
                elif len(mine_neighbors) == number:
                    done_grid.add((x, y))
                    for nx, ny in no_push_neighbors:
                        click_cell(nx, ny)
                        recognize_and_mark_or_click(nx, ny)



    # 如果绕了一圈什么都没做，就随机点一个格子
    double_break_flag = 0
    if do_nothing_flag == 1:
        for x in range(num_columns):
            for y in range(num_rows):
                if (x, y) in marked_mines:
                    continue
                if (x, y) in done_grid:
                    continue
                cell_content = recognize_cell(x, y)
                print("(" + str(x) + "," + str(y) + ")")
                if cell_content == 'no-push':
                    print("random")
                    click_cell(x, y)
                    recognize_and_mark_or_click(x, y)
                    double_break_flag = 1
                    break
            if double_break_flag == 1:
                break

if __name__ == "__main__":
    # 等待用户点击以获取游戏区域ss的左上和右下角坐标
    game_area_top_left = get_mouse_click("请将鼠标移动到游戏区域的左上角，然后按下 's' 键")
    game_area_bottom_right = get_mouse_click("请将鼠标移动到游戏区域的右下角，然后按下 's' 键")

    # 等待用户点击以获取格子的左上和右下角坐标
    # cell_top_left = get_mouse_click("请将鼠标移动到一个格子的左上角，然后按下 's' 键")
    # cell_bottom_right = get_mouse_click("请将鼠标移动到同一个格子的右下角，然后按下 's' 键")

    # 用户输入扫雷区域的横向和纵向列数
    num_columns = int(input("请输入扫雷区域的横向的列数: "))
    num_rows = int(input("请输入扫雷区域的纵向的行数: "))

    # 计算格子的大小
    # cell_width = cell_bottom_right[0] - cell_top_left[0]
    # cell_height = cell_bottom_right[1] - cell_top_left[1]
    # cell_size = (cell_width + cell_height) // 2  # 取平均值作为格子大小
    cell_width = (game_area_bottom_right[0] - game_area_top_left[0]) // num_columns
    cell_height = (game_area_bottom_right[1] - game_area_top_left[1]) // num_rows
    cell_size = (cell_width + cell_height) // 2  # 取平均值作为格子大小

    # 采集模板图片
    # template_names = ['1','2','3','4','mine','empty']
    # for name in template_names:
    #     capture_template(name)

    # 加载模板图片
    load_templates()

    # 等待几秒以便切换到游戏窗口
    print("即将开始自动扫雷...")
    # time.sleep(3)

    # 开始时随机点2个格子
    random_start = int(input("开始时左右各随机点几次: "))
    for i in range(random_start):
        click_cell(np.random.randint(0, num_columns // 2), np.random.randint(0, num_rows))
        click_cell(np.random.randint(num_columns // 2, num_columns - 1), np.random.randint(0, num_rows))

    while True:
        auto_play()
