import os, sys
from django.shortcuts import render
from django.http import HttpResponse
import time
import shutil
import cv2
from PIL import Image
import time
import shutil
import xml.etree.ElementTree as elemTree

def preprocessForDMFont():
    start = time.time()
    print("preprocess for DM-Font start...")
    kor_characters = [ "가", "깩", "끼", "냐", "걔", "삯", "떤", "에", "앉", "며", "않", "예", "돋", "뽈", "와", "맑", "쐐", "앎", "외", "밟","죠",
    "곬", "쭉", "핥", "춰", "읊", "퀘", "앓", "튐", "퓨", "굽", "흐", "값", "긔", "귓", "러", "갔", "낭", "대", "맞", "땨", "옻","호", "칼","머",
    "같", "베", "갚", "뼈", "낳", "약", "산"]
    output_root_dir = "../attr2font_inference/"
    if not os.path.isdir(output_root_dir + "inference/"):
        os.mkdir(output_root_dir + "inference/")
    inference_dir = output_root_dir + "inference/"
    file_list = [_ for _ in os.listdir(output_root_dir) if _.endswith(".png")]
    #change file name (index to characters)    
    for file in file_list:
        idx = int(file.split("_")[1].split(".")[0])
        shutil.move(output_root_dir + file, inference_dir + kor_characters[idx] + ".png")
        
    #change 64x64 to 128x128 for DM-Font
    trans_target = inference_dir
    trans_list = os.listdir(trans_target)
    
    resizeHeight = 128
    resizeWidth = 128
    for trans_item in trans_list:
        img = cv2.imread(trans_target + trans_item, cv2.IMREAD_GRAYSCALE)    
        img_resize = cv2.resize(img, (resizeHeight, resizeWidth), interpolation = cv2.INTER_CUBIC)
        cv2.imwrite(trans_target + trans_item, img_resize)
    print("preprocess for DM-Font finish :", time.time() - start)
    
def attr2font_inference(attr_list):
    start = time.time()
    print("attr2font inference start")
    cmd = "python ../Attr2Font/main.py --phase inference --data_root ../data --check_path ../Attr2Font/bestModel/ --infer_path ../attr2font_inference"
    cmd += " --attr_list"
    for attr in attr_list:
        cmd += " " + str(attr)
    os.system(cmd)
    print("attr2font inference finish :", time.time() - start)
    
def dmfont_inference():
    start = time.time()
    print("dmfont inference start")
    cmd = "python ../fewshot-font-generation/inference.py ../dmfont_config/kor_eval.yaml ../dmfont_config/kor_ttf.yaml --model DM"
    cmd += " --weight ../result/best_dm.pth --result_dir ../dmfont_inference"
    os.system(cmd)
    print("dmfont inference finish :", time.time() - start)
    
def make_png_to_svg():
    start = time.time()
    print("make png to svg start")
    png_dir = "../dmfont_inference/inference/"
    file_list = [_ for _ in os.listdir(png_dir) if _.endswith(".png")]
    fileNames = file_list    
    svg_dir = "../svg_for_fontforge/"
    for fileName in file_list:
        cmd = ""
        cmd += "/home/ubuntu/.cargo/bin/vtracer"
        cmd += " --preset bw"
        cmd += " --mode pixel"
#         cmd += " -f 11 --hierarchical cutout --mode pixel"
        cmd += " --input " + png_dir + fileName
        cmd += " --output " + svg_dir + fileName.split(".")[0] + ".svg"
        os.system(cmd)
    print("make png to svg finish :", time.time() - start)
    
def edit_svg_view_box():
    start = time.time()
    print("edit svg start")
    svg_dir = "../svg_for_fontforge/"
    file_list = [_ for _ in os.listdir(svg_dir) if _.endswith(".svg")]
    for file in file_list:
        svg_dir + file.split(".")[0] + ".svg",'r'
        svg_file = svg_dir + file.split(".")[0] + ".svg"
        tree = elemTree.parse(svg_file)
        root = tree.getroot() 
        root.set("viewBox", "0 0 128 128")
        with open(svg_file, "wb") as file:
            tree.write(file, encoding='utf-8', xml_declaration=True)
    print("edit svg finish :", time.time() - start)    

def svg_to_ttf():
    start = time.time()
    print("svg to ttf start")
    
    print("svg to ttf finish :", time.time() - start)

def ganafont(request):
    test = ""
    if request.method == "POST":
        start = time.time()
        attr_list = []
        for x in range(1,38):
            target = "attr_"+str(x)
            attr_list.append(int(request.POST.get(target)))
        attr2font_inference(attr_list)
        preprocessForDMFont()
        dmfont_inference()
        make_png_to_svg()
        edit_svg_view_box()
        svg_to_ttf()
        
        print("font generation time :", time.time() - start)
    return render(request, "ganafont.html", {"test_sentence":test})