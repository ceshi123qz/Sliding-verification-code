# coding=utf-8
from PIL import Image

from selenium.webdriver.common.action_chains import ActionChains
from selenium import webdriver
import time
import random


def get_track(distance):
    """
    拿到移动轨迹，模仿人的滑动行为，先匀加速后匀减速
    匀变速运动基本公式：
    distance: 需要移动的距离
    """
    print("distance", distance)
    # 初速度
    v = 0
    # 单位时间为0.2s来统计轨迹，轨迹即0.2内的位移
    t = 2
    # 位移/轨迹列表，列表内的一个元素代表0.2s的位移
    tracks = []
    # 当前的位移
    current = 0
    # 到达 mid 值开始减速(中点)
    mid = distance * 7 / 8
    # 多划出去 10 像素
    distance += 5  # 先滑过一点，最后再反着滑动回来
    # a = random.randint(1,3)
    while current < distance:
        # 设置速度
        if current < mid:
            # 加速度越小，单位时间的位移越小,模拟的轨迹就越多越详细
            a = random.randint(2, 4)  # 加速运动
        else:
            a = -random.randint(3, 5)  # 减速运动

        # 初速度
        v0 = v
        # 0.2 秒时间内的位移
        s = v0 * t + 0.5 * a * (t ** 2)
        # 当前的位置
        current += s
        # 添加到轨迹列表
        tracks.append(round(s))

        # 速度已经达到v,该速度作为下次的初速度
        v = v0 + a * t

    print(tracks)
    total = sum(tracks)
    # 对超出的移动的内容进行修正
    while (total - distance) > -13:
        # 反着滑动到大概准确位置
        tracks.append(-random.randint(2, 3))
        total = sum(tracks)

    print('tracks', tracks)
    print('sumtracks', sum(tracks))
    return tracks


def get_distance(image1, image2):
    """
    滑动验证码需要移动的距离
    image1:没有缺口的图片对象
    image2:带缺口的图片对象
    """
    # print('size', image1.size)
    # rgb的差值不超过这一个范围 误差范围
    threshold = 50
    for i in range(0, image1.size[0]):  # 260
        for j in range(0, image1.size[1]):  # 160
            pixel1 = image1.getpixel((i, j))
            pixel2 = image2.getpixel((i, j))
            res_R = abs(pixel1[0] - pixel2[0])  # 计算RGB差
            res_G = abs(pixel1[1] - pixel2[1])  # 计算RGB差
            res_B = abs(pixel1[2] - pixel2[2])  # 计算RGB差
            if res_R > threshold and res_G > threshold and res_B > threshold:
                return i  # 需要移动的距离


driver = webdriver.Chrome(executable_path='D:\webdriver\chromedriver_win32\chromedriver.exe')
url = 'http://www.cnbaowen.net/api/geetest/'

driver.get(url)
time.sleep(2)

time.sleep(2)

xuanting_ele = driver.find_element_by_class_name('gt_slider_knob')

# 鼠标悬停
actions = ActionChains(driver)
actions.move_to_element(xuanting_ele).perform()
time.sleep(1)
# 截取原图
full = driver.find_element_by_class_name('gt_fullbg')
full.screenshot('full.png')

# driver.save_screenshot('before.png')
# 隐藏滑块
script1 = """
var one = document.getElementsByClassName(\"gt_slice\");
one[0].style['display'] = 'none';
"""
driver.execute_script(script1)
# 隐藏全图
script2 = """
var two = document.getElementsByClassName(\"gt_fullbg\");
two[0].style['display'] = 'none';
"""
driver.execute_script(script2)
time.sleep(1)
# 截取缺图
cut = driver.find_element_by_class_name('gt_cut_bg.gt_show')

cut.screenshot('cut.png')
"""获取移动的距离"""
image1 = Image.open('full.png')
image2 = Image.open('cut.png')
# 距离
distance = get_distance(image1, image2)
print(distance)
# 移动轨迹
tracks = get_track(distance)
# driver.save_screenshot('after.png')

# 滑动
action = webdriver.ActionChains(driver)

action.click_and_hold().perform()
# 移动 多次移动
for track in tracks:
    action.move_by_offset(track, 0)
# 释放
action.release().perform()
time.sleep(5)
