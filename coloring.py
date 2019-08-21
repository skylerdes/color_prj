# -*- coding: utf-8 -*-
"""
Created on Mon Aug 19 09:43:23 2019

@author: User
"""

img = None
grey_img = None
color_img = None
palImg = None
grey_mode = 0
paint_mode = 0
#temp_set = set()

areas_arr = {}
pix_array = {}
colors_array = {}
new_areas = {}
palette_array = {}

selected_color = None
selected_pos = None

palette_dims = {"r":15, "left":20, "right":20, "up":20, "down":20, "between":10}

from PyQt5 import QtWidgets
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
import sys
from PyQt5.QtWidgets import QFileDialog

from PIL import Image, ImageDraw
from PyQt5.QtGui import QPixmap

def start():
    load_img_from_csv()
    merge_colors()
    confirm_changes()
    create_palette()

def load_img_from_csv():
    global color_img
    global img
    global areas_arr
    global pix_array
    global grey_mode
    global paint_mode
    global selected_color
    
    fName = QFileDialog.getOpenFileName(None, "Select image", \
                                                  "D:\\_python\coloring", "Csv fike (*.csv)")
    if fName[0] == "":
        return
    num = 0
    with open(fName[0], "r") as f:
        img_seq = f.read().split("\n")[:-1]
    img_size = img_seq[0].split(";")
    img_size = (int(img_size[0]), int(img_size[1]))
    img_seq = img_seq[1:]
    color_img = Image.new("RGB", img_size)
    img_data = color_img.getdata()
    for area in img_seq:
        area = area.split(";")
        color = area[1].strip("()").split(",")
        color = (int(color[0]), int(color[1]), int(color[2]))
        areas_arr[int(area[0])] = {}
        areas_arr[int(area[0])]["color"] = color
        areas_arr[int(area[0])]["pixels"] = []
        pixels = area[2].split("$")
        for pix in pixels:
            pix = pix.strip("()").split(",")
            pix = (int(pix[0]), int(pix[1]))
            areas_arr[int(area[0])]["pixels"].append(pix)
            pix_array[pix] = int(area[0])
            img_data.putpixel(pix, color)
#            temp_set.add(pix)
            num += 1
    color_img.putdata(img_data)
    img = color_img.copy()
    update_ImgView(img, Img_lbl)
    Info_tedit.append("Area by size: " + str(img.width * img.height))
#    Info_tedit.append("Area real: " + str(num))
#    Info_tedit.append("Area by set (diff pixels): " + str(len(temp_set)))
    grey_mode = 0
    paint_mode = 0
    Grey_btn.setEnabled(True)
    ColMerge_btn.setEnabled(True)
    PaletteCreate_btn.setEnabled(False)
    selected_color = None

def greyscale_switch():
    global img
    global grey_img
    global color_img
    global grey_mode
    if img == None:
        return
    if grey_img == None:
        grey_img = img.convert("L")
        grey_img = grey_img.convert("RGB")
    
    if grey_mode:
        img = color_img.copy()
        grey_mode = 0
    else:
        img = grey_img.copy()
        grey_mode = 1

    update_ImgView(img, Img_lbl)
    
def merge_area_colors(color1, color2, size1, size2):
    sum_size = size1 + size2
    del1 = size1 / sum_size
    del2 = size2 / sum_size
    r = int(color1[0] * del1 + color2[0] * del2)
    g = int(color1[1] * del1 + color2[1] * del2)
    b = int(color1[2] * del1 + color2[2] * del2)
    return (r, g, b)

def color_diff(color1, color2):
    return abs(color1[0] - color2[0]) + abs(color1[1] - color2[1]) + abs(color1[2] - color2[2])    
    
def merge_colors():
    
    import time
    start = time.time()
    
    global areas_arr
    global color_img
    global grey_img
    global grey_mode
    global new_areas
    global img
    global colors_array
    
    if grey_mode:
        return
    
    if color_img == None:
        return
    
    colors_array = {}
        
    for area in areas_arr:
        new_areas[area] = areas_arr[area].copy()
    
    for area in new_areas:
        c = new_areas[area]["color"]
        if not c in colors_array:
            colors_array[c] = []
        if not area in colors_array[c]:
            colors_array[c].append(area)
        
    for i in new_areas:
        for j in new_areas:
            if i == j:
                continue
            col1 = new_areas[i]["color"]
            col2 = new_areas[j]["color"]
            if col1 == col2:
                continue
            if color_diff(col1, col2) < ColMerge_scroll.value():
                size1 = len(areas_arr[i]["pixels"])
                size2 = len(areas_arr[j]["pixels"])
                new_col = merge_area_colors(col1, col2, size1, size2)
                colors_array[new_col] = colors_array.get(new_col, [])
                for area in colors_array[col1]:
                    new_areas[area]["color"] = new_col
                    if not area in colors_array[new_col]:
                        colors_array[new_col].append(area)
                for area in colors_array[col2]:
                    new_areas[area]["color"] = new_col
                    if not area in colors_array[new_col]:
                        colors_array[new_col].append(area)
                if new_col != col1:
                    colors_array.pop(col1)
                if new_col  != col2:
                    colors_array.pop(col2)
                
                new_areas[i]["color"] = new_col
                new_areas[j]["color"] = new_col
                
    img_data = color_img.getdata()
    
    for area in new_areas:
        c = new_areas[area]["color"]
        if not c in colors_array:
            colors_array[c] = []
        if not area in colors_array[c]:
            colors_array[c].append(area)
        for pix in new_areas[area]["pixels"]:
            img_data.putpixel(pix, new_areas[area]["color"])
    
    grey_img = None
    
    img = color_img.copy()
    
    update_ImgView(img, Img_lbl)
    
    finish = time.time() - start
    
    Info_tedit.append("Max diff: " + str(ColMerge_scroll.value()))
    Info_tedit.append("Worked for " + str(finish) + " seconds")
    Info_tedit.append("Total: " + str(len(colors_array)) + " colors")
    
    Confirm_btn.setEnabled(True)
        
def confirm_changes():
    global areas_arr
    global new_areas
    
    for area in new_areas:
        areas_arr[area] = new_areas[area].copy()
        
    PaletteCreate_btn.setEnabled(True)
    
    
    
def create_palette():
    global colors_array
    global img
    global areas_arr
    global paint_mode
    global palette_dims
    global palette_array
    global palImg
    
    if paint_mode:
        return
    
    r = palette_dims["r"]
    left = palette_dims["left"]
    right = palette_dims["right"]
    up = palette_dims["up"]
    down = palette_dims["down"]
    between = palette_dims["between"]
    size = (left + ((r * 2) + between) * len(colors_array) - between + right, up + r * 2 + down)
    palImg = Image.new("RGB", size, "#FFFFFF")
    draw = ImageDraw.Draw(palImg)
    n = 0
    for col in colors_array:
        x0 = left + (r * 2 + between) * n
        y0 = up
        x1 = x0 + r * 2
        y1 = y0 + r * 2
        draw.ellipse([x0, y0, x1, y1], col, "#000000")
        palette_array[n] = col
        n += 1
    
    update_ImgView(palImg, Palette_lbl)
    
    paint_mode = 1
    greyscale_switch()       
    
def img_click(e):
    global grey_mode
    global color_img
    global img
    global pix_array
    global areas_arr
    global paint_mode
    global colors_array
    global selected_color
    global selected_pos
    global palImg
    
    if not paint_mode:
        return
    
    if not selected_color:
        return
    
    Grey_btn.setEnabled(False)
    
    data = img.getdata()
    color_data = color_img.getdata()
    
    pix = (e.pos().x(), e.pos().y())
    
    if not pix_array[pix] in colors_array[selected_color]:
        return
    
    area = areas_arr[pix_array[pix]]["pixels"]
    
    for pix in area:
        if data.getpixel(pix) == color_data.getpixel(pix):
            return
        color = color_data.getpixel(pix)
        img.putpixel(pix, color)
        
#    print(colors_array[selected_color])
    colors_array[selected_color].remove(pix_array[pix])
#    print(colors_array[selected_color])
    
    if colors_array[selected_color] == []:
        draw = ImageDraw.Draw(palImg)
        draw.ellipse(selected_pos, "#888888", "#000000")
        update_ImgView(palImg, Palette_lbl)
    
    del(areas_arr[pix_array[pix]])
        
    update_ImgView(img, Img_lbl)
    
    Info_tedit.append(str(pix_array[(e.pos().x(), e.pos().y())]))
        
def palette_click(e):
    global colors_array
    global img
    global areas_arr
    global paint_mode
    global selected_color
    global palette_array
    global grey_img
    
    if not paint_mode:
        return
    
    if selected_color:
        img_data = img.getdata()
        grey_data = grey_img.getdata()
        for area in colors_array[selected_color]:
            for pix in areas_arr[area]["pixels"]:
                img_data.putpixel(pix, grey_data.getpixel(pix))
    
    x = e.pos().x()
    selected_color = palette_array[get_color_by_pos(x)]
    
    data = img.getdata()
    
    if colors_array[selected_color] == []:
        return
    
    col = (255, 0, 255)
    for area in colors_array[selected_color]:
        for pix in areas_arr[area]["pixels"]:
            data.putpixel(pix, col)
    
    update_ImgView(img, Img_lbl)

def get_color_by_pos(x):
    
    global palette_dims
    global selected_pos
    
    r = palette_dims["r"]
    left = palette_dims["left"]
    between = palette_dims["between"]
    
    n = (x - left) // (r * 2 + between)
    
    x0 = left + n * (r * 2  + between)
    y0 = palette_dims["up"]
    x1 = x0 + r * 2
    y1 = y0 + r * 2
    selected_pos = [x0, y0, x1, y1]
    
    return n

def update_ImgView(img, widget):
    """
    transform img to qt type and show it in corresponding widget
    img - Image from python PIL library
    widget - QWidget, preferrably QLabel, not tested with other types
    at least widget should have methods:
        setText(str)
        setPixmap(QPixmap)
        resize(QSize)
    """
    pixmap = img.toqpixmap()
    widget.setText("")
    widget.setPixmap(pixmap)
    widget.resize(pixmap.size())
    
app = QtWidgets.QApplication(sys.argv)
window = QtWidgets.QWidget()
window.setWindowTitle("Coloring test")
window.resize(1500, 900)

font = QFont()
font.setFamily("Arial")
font.setPointSize(14)

Main_hlay = QtWidgets.QHBoxLayout()

Main_vlay = QtWidgets.QVBoxLayout()

Btn_hlay = QtWidgets.QHBoxLayout()

Load_btn = QtWidgets.QPushButton("&Open image")
Load_btn.setFont(font)
Load_btn.clicked.connect(load_img_from_csv)

Btn_hlay.addWidget(Load_btn)

Grey_btn = QtWidgets.QPushButton("Greyscale")
Grey_btn.setFont(font)
Grey_btn.clicked.connect(greyscale_switch)
Grey_btn.setEnabled(False)

Btn_hlay.addWidget(Grey_btn)

ColMerge_scroll = QtWidgets.QSlider(Qt.Horizontal)
ColMerge_scroll.setMinimum(10)
ColMerge_scroll.setMaximum(100)
ColMerge_scroll.setValue(25)

Btn_hlay.addWidget(ColMerge_scroll)

ColMerge_btn = QtWidgets.QPushButton("Merge colors")
ColMerge_btn.setFont(font)
ColMerge_btn.setEnabled(False)
ColMerge_btn.clicked.connect(merge_colors)

Btn_hlay.addWidget(ColMerge_btn)

Confirm_btn = QtWidgets.QPushButton("Confirm changes")
Confirm_btn.setFont(font)
Confirm_btn.setEnabled(False)
Confirm_btn.clicked.connect(confirm_changes)

Btn_hlay.addWidget(Confirm_btn)

PaletteCreate_btn = QtWidgets.QPushButton("Create colors")
PaletteCreate_btn.setFont(font)
PaletteCreate_btn.setEnabled(False)
PaletteCreate_btn.clicked.connect(create_palette)

Btn_hlay.addWidget(PaletteCreate_btn)

Main_vlay.addLayout(Btn_hlay)

#scroll area for image scroll availability
Img_scroll = QtWidgets.QScrollArea()

#Label for actual image showing
Img_lbl = QtWidgets.QLabel("Here will be your image, I promise")
Img_lbl.setFont(font)
Img_lbl.setScaledContents(True)
Img_lbl.mouseReleaseEvent = img_click

Img_scroll.setWidget(Img_lbl)

Main_vlay.addWidget(Img_scroll, 20)

Palette_scroll = QtWidgets.QScrollArea()

Palette_lbl = QtWidgets.QLabel("")
Palette_lbl.setFont(font)
Palette_lbl.setScaledContents(True)
Palette_lbl.mouseReleaseEvent = palette_click

Palette_scroll.setWidget(Palette_lbl)

Main_vlay.addWidget(Palette_scroll, 1)

Info_tedit = QtWidgets.QTextEdit()
Info_tedit.setFont(font)

Main_hlay.addLayout(Main_vlay, 5)
Main_hlay.addWidget(Info_tedit, 1)

window.setLayout(Main_hlay)

window.show()
start()

sys.exit(app.exec_())