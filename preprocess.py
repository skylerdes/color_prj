# -*- coding: utf-8 -*-
"""
Created on Thu Aug 15 08:54:55 2019

@author: User
"""

img = None
areas_arr = {}
area_grow = 0
etalon_img = None
count_img = None
new_areas = None

from PyQt5 import QtWidgets
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
import sys
from PyQt5.QtWidgets import QFileDialog

from PIL import Image, ImageDraw
from PyQt5.QtGui import QPixmap

from PIL import ImageFilter

filtersDic = { "BLUR":ImageFilter.BLUR, "CONTOUR":ImageFilter.CONTOUR, \
               "DETAIL":ImageFilter.DETAIL, "EDGE_ENHANCE":ImageFilter.EDGE_ENHANCE, \
               "EDGE_ENHANCE_MORE":ImageFilter.EDGE_ENHANCE_MORE, "EMBOSS":ImageFilter.EMBOSS, \
               "FIND_EDGES":ImageFilter.FIND_EDGES, "SMOOTH":ImageFilter.SMOOTH, \
               "SMOOTH_MORE":ImageFilter.SMOOTH_MORE, "SHARPEN":ImageFilter.SHARPEN }

#loading image for future use
def load_image():
    """
    prompt to user to select image to load, 
    if one selected loading it to global variable img,
    and showing it in Img_lbl widget
    type of img - Image from python PIL library,
    also activates widgets, unavailable without image loaded
    """
    global img
    fName = QFileDialog.getOpenFileName(None, "Select image", \
                                                  "D:\\_python\coloring", "Image files (*.jpg *.png *.bmp)")
    if fName[0] != "":
        img = Image.open(fName[0])
        update_ImgView(img, Img_lbl)
        activate_widgets()
        global areas_arr
        global areas_grow
        global etalon_img
        global count_img
        global new_areas
        areas_arr = {}
        areas_grow = 0
        etalon_img = None
        count_img = None
        new_areas = None
        
        
def save_image():
    """
    prompt to user to select where to save new pic
    """
    global img
    fName = QFileDialog.getSaveFileName(None, "Save image", "D:\\_python\coloring", "Image files (*.jpg *.png *.bmp)")
    if fName[0] != "":
        img.save(fName[0], "BMP")
        
        fName = fName[0] + "_areas.csv"
        
        global areas_arr
        global new_areas
        if new_areas != None:
            arr = new_areas
        else:
            arr = areas_arr
        with open(fName, "w") as f:
            f.write(str(img.width) + ";" + str(img.height) + "\n")
            for area in arr:
                s = str(area) + ";" + str(arr[area]["color"]) + ";"
                for pix in arr[area]["pixels"][:-1]:
                    s += str(pix.get_coords()) + "$"
                    
                s += str(arr[area]["pixels"][-1].get_coords()) + "\n"
                f.write(s)
        
def filter_image():
    """
    image filtering func
    """        
    global img
    global etalon_img
    if img == None:
        return
    if etalon_img == None:
        etalon_img = img.copy()
    filt = filtersDic[Filter_cbox.currentText()]
    img = etalon_img.filter(filt)
    update_ImgView(img, Img_lbl)
    
#def filter_image():
#    """
#    image filtering func
#    """
#    global img
#    
#    img_seq = img.getdata()
#    for i in range(img.width):
#        for j in range(img.height):
#            r, g, b = img_seq.getpixel((i, j))
#            r *= 5
#            g *= 5
#            b *= 5
#            delim = 5
#            for n in range(i - 1, i + 2):
#                for m in range(j - 1, j + 2):
#                    if n < 0 or m < 0 or n >= img.width or m >= img.height:
#                        continue
#                    delim += 1
#                    p = img_seq.getpixel((n, m))
#                    r += p[0]
#                    g += p[1]
#                    b += p[2]
#            r //= delim
#            g //= delim
#            b //= delim
#            img_seq.putpixel((i, j), (r, g, b))
#    img.putdata(img_seq)
#    update_ImgView(img, Img_lbl)s

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
        
def activate_widgets():
    """
    activating widgets, unavailable before image is loaded
    """
    Action_btn.setEnabled(True)
    PixDiff_sbox.setEnabled(True)
    Save_btn.setEnabled(True)
    Filter_btn.setEnabled(True)
    Merge_btn.setEnabled(False)
    
def color_count(img):
    """
    counts distinct colors in img variable and returning it
    img - Image from python PIL library or None
    if img == None returns 0
    else going around all pixels, counting distinct colors
    and returning this number
    """
    if img == None:
        return 0
    ret = {}
    for i in range(img.width):
        for j in range(img.height):
            pix = img.getpixel((i, j))
            col = pix[0] * 256 * 256 + pix[1] * 256 + pix[2]
            ret[col] = ret.get(col, 0) + 1
    return len(ret)

def process_img():
    """
    actions with image by button click
    count distinct colors number
    """
    
    global count_img
    global img
    if count_img != None:
        img = count_img.copy()
    else:
        get_areas(img, PixDiff_sbox.value())
        count_img = img.copy()
    
    Merge_btn.setEnabled(True)
    update_ImgView(img, Img_lbl)
    
    
def merge_areas():
    import time
    start = time.time()
    
    global areas_arr
    global img
    global new_areas
    
    new_areas = areas_arr.copy()
    
    br_area = len(new_areas)
    
    data = img.getdata()
    i = 0
    while True:
        if i >= br_area:
            break
        if new_areas.get(i, -1) == -1:
            i += 1
            continue
        area = new_areas[i]
        size = len(area["pixels"])
        if size > Merge_sbox.value():
            i += 1
            continue
        near_areas = {}
        for pix in area["pixels"]:
            pix.get_near_areas(near_areas)
        max_area = -1
        max_size = 0
        for a in near_areas:
            if near_areas[a] > max_size:
                max_size = near_areas[a]
                max_area = a
        
        color1 = new_areas[max_area]["pixels"][0].get_rgb()
        color2 = area["pixels"][0].get_rgb()
        size1 = len(new_areas[max_area]["pixels"])
        size2 = len(area["pixels"])
        
        r, g, b = merge_colors(color1, color2, size1, size2)
        
        new_areas[max_area]["pixels"] += area["pixels"]
        
        for pix in area["pixels"]:
            pix.area = max_area
            pix.set_rgb(r, g, b)
            pix.area_pix = new_areas[max_area]["pixels"]
            data.putpixel(pix.get_coords(), pix.get_rgb())
            
        new_areas.pop(i)
        
    end = time.time() - start
    Info_tedit.append("Total areas after merge: " + str(len(new_areas)))
    Info_tedit.append("Worked for " + str(end))
    update_ImgView(img, Img_lbl)
    
def merge_colors(color1, color2, size1, size2):
    sum_size = size1 + size2
    del1 = size1 / sum_size
    del2 = size2 / sum_size
    r = int(color1[0] * del1 + color2[0] * del2)
    g = int(color1[1] * del1 + color2[1] * del2)
    b = int(color1[2] * del1 + color2[2] * del2)
    return (r, g, b)

def color_diff(color1, color2):
    return abs(color1[0] - color2[0]) + abs(color1[1] - color2[1]) + abs(color1[2] - color2[2])

def get_areas(img, max_diff):
    """
    breaking img into some areas 
    with diff between pixels less than max_diff
    img - Image from python PIL library or None
    max_diff - int
    """
    import time
    start = time.time()
    pix_array = {}
    curr_area = 0;
    img_seq = img.getdata()
    for i in range(img.width):
        for j in range(img.height):
            if pix_array.get((i, j), -1) != -1 and pix_array[(i, j)].get_area() != -1:
                continue
            pix_array[(i, j)] = Custom_pixel((i, j), img_seq.getpixel((i, j)), img.width, img.height, pix_array, max_diff, curr_area)
            curr_area += 1
            grow_area(img_seq, max_diff, pix_array[(i, j)])
#        img.putdata(img_seq)
#        update_ImgView(img, Img_lbl)
#        window.repaint()
    Info_tedit.append("Total areas: " + str(curr_area))
    
    end = time.time() - start
    Info_tedit.append("Worked for " + str(end))
    img.putdata(img_seq)
    update_ImgView(img, Img_lbl)
    
    global area_grow
    Info_tedit.append("Area by size: " + str(img.width * img.height))
    Info_tedit.append("Area real: " + str(area_grow))
                
            
def grow_area(img, max_diff, pix):
    """
    growing area around pixel(i, j) from img
    with difference between pixels less than max_diff
    img - Image sequence from python PIL library or None
    max_diff - int
    pix - (i, j): coordinates of pixel in img
    """
        
    if img == None:
        return
    to_check = pix.get_near([])
    area_color = pix.get_rgb()
    while len(to_check) != 0:
        if not to_check[0] in pix.pix_array:
            pix.pix_array[to_check[0]] = Custom_pixel(to_check[0], img.getpixel(to_check[0]), pix.img_width, pix.img_height, pix.pix_array, max_diff, -1)
        
        test_pix = pix.pix_array[to_check[0]]
        to_check = to_check[1:]
        if test_pix.get_area() != -1:
            continue
        if not pix.is_similiar(test_pix):
            continue
        pix.pix_array[test_pix.get_coords()].set_area(pix.get_area())
        col1 = area_color
        col2 = test_pix.get_rgb()
        size1 = len(pix.area_pix)
        size2 = 1
        area_color = merge_colors(col1, col2, size1, size2)
        pix.area_pix.append(test_pix)
        to_check = test_pix.get_near(to_check)
        
        
    r, g, b = pix.get_rgb()
    for i in pix.area_pix:
        i.area_pix = pix.area_pix
        rgb = i.get_rgb()
        r += rgb[0]
        g += rgb[1]
        b += rgb[2]
    
    r //= len(pix.area_pix)
    g //= len(pix.area_pix)
    b //= len(pix.area_pix)
    
    global areas_arr
    areas_arr[pix.area] = {}
    areas_arr[pix.area]["color"] = (r, g, b)
    areas_arr[pix.area]["pixels"] = pix.area_pix

    for i in pix.area_pix:
        i.set_rgb(r, g, b)    
        img.putpixel(i.get_coords(), i.get_rgb())
    
    global area_grow
    area_grow += len(pix.area_pix)
#    Info_tedit.append(str(pix.area) + ":" + str(len(pix.area_pix))) 
    
class Custom_pixel(object):
    def __init__(self, coords, rgb, w, h, pix_array, max_diff, area = -1):
        self.x = coords[0]
        self.y = coords[1]
        self.r = rgb[0]
        self.g = rgb[1]
        self.b = rgb[2]
        self.area = area
        self.img_width = w
        self.img_height = h
        self.pix_array = pix_array
        self.max_diff = max_diff
        self.area_pix = [self]
    
    def get_coords(self):
        return (self.x, self.y)
    
    def set_area(self, area):
        self.area = area
        
    def get_area(self):
        return self.area
    
    def get_rgb(self):
        return (self.r, self.g, self.b)
    
    def set_rgb(self, r, g, b):
        self.r = r
        self.g = g
        self.b = b
        
    def get_near(self, near):
        for i in range(self.x - 1, self.x + 2):
            for j in range(self.y - 1, self.y + 2):
                if (i, j) in near:
                    continue
                if i < 0 or j < 0 or i >= self.img_width or j >= self.img_height:
                    continue
                if (i, j) in self.pix_array and self.pix_array[(i, j)].get_area() != -1:
                    continue
                near.append((i, j))
        return near
    
    def get_near_areas(self, near_areas):
        
        for i in range(self.x - 1, self.x + 2):
            for j in range(self.y - 1, self.y + 2):
                if i < 0 or j < 0 or i >= self.img_width or j >= self.img_height:
                    continue
                p = self.pix_array[(i, j)]
                if p.get_area() == self.get_area():
                    continue
                else:
                    near_areas[p.get_area()] = near_areas.get(p.get_area(), 0) + 1
    
    def is_similiar(self, other):
        return (abs(self.r - other.r) + abs(self.g - other.g) + abs(self.b - other.b)) < self.max_diff

app = QtWidgets.QApplication(sys.argv)
window = QtWidgets.QWidget()
window.setWindowTitle("Preprocessing")
window.resize(1500, 900)

font = QFont()
font.setFamily("Arial")
font.setPointSize(14)

Main_hlay = QtWidgets.QHBoxLayout()

Main_vlay = QtWidgets.QVBoxLayout()

Btn_hlay = QtWidgets.QHBoxLayout()

Load_btn = QtWidgets.QPushButton("&Open image")
Load_btn.setFont(font)
Load_btn.clicked.connect(load_image)

Btn_hlay.addWidget(Load_btn)

PixDiff_sbox = QtWidgets.QSpinBox()
PixDiff_sbox.setMinimum(1)
PixDiff_sbox.setMaximum(1000)
PixDiff_sbox.setValue(60)
PixDiff_sbox.setEnabled(False)
PixDiff_sbox.setFont(font)

Btn_hlay.addWidget(PixDiff_sbox)

Action_btn = QtWidgets.QPushButton("Count colors")
Action_btn.setFont(font)
Action_btn.setEnabled(False)
Action_btn.clicked.connect(process_img)

Btn_hlay.addWidget(Action_btn)

Save_btn = QtWidgets.QPushButton("Save result")
Save_btn.setFont(font)
Save_btn.setEnabled(False)
Save_btn.clicked.connect(save_image)

Btn_hlay.addWidget(Save_btn)

Main_vlay.addLayout(Btn_hlay)

Filter_hlay = QtWidgets.QHBoxLayout()

filters = ["BLUR", "CONTOUR", "DETAIL", "EDGE_ENCHANCE", \
           "EDGE_ENCHANCE_MORE", "EMBOSS", "FIND_EDGES", \
           "SMOOTH", "SMOOTH_MORE", "SHARPEN"]

Filter_cbox = QtWidgets.QComboBox()
Filter_cbox.setFont(font)
Filter_cbox.addItems(filtersDic.keys())

Filter_hlay.addWidget(Filter_cbox)

Filter_btn = QtWidgets.QPushButton("Filter image")
Filter_btn.setFont(font)
Filter_btn.setEnabled(False)
Filter_btn.clicked.connect(filter_image)

Filter_hlay.addWidget(Filter_btn)

Merge_sbox = QtWidgets.QSpinBox()
Merge_sbox.setFont(font)
Merge_sbox.setMinimum(10)
Merge_sbox.setMaximum(1000)
Merge_sbox.setValue(50)

Filter_hlay.addWidget(Merge_sbox)

Merge_btn = QtWidgets.QPushButton("Merge areas")
Merge_btn.setFont(font)
Merge_btn.setEnabled(False)
Merge_btn.clicked.connect(merge_areas)

Filter_hlay.addWidget(Merge_btn)

Main_vlay.addLayout(Filter_hlay)

#scroll area for image scroll availability
Img_scroll = QtWidgets.QScrollArea()

#Label for actual image showing
Img_lbl = QtWidgets.QLabel("Here will be your image, I promise")
Img_lbl.setFont(font)
Img_lbl.setScaledContents(True)

Img_scroll.setWidget(Img_lbl)

Main_vlay.addWidget(Img_scroll)

Info_tedit = QtWidgets.QTextEdit()
Info_tedit.setFont(font)

Main_hlay.addLayout(Main_vlay, 5)
Main_hlay.addWidget(Info_tedit, 1)

window.setLayout(Main_hlay)

window.show()

sys.exit(app.exec_())