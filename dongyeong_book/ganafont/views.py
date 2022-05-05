import os, sys
from django.shortcuts import render
from django.http import HttpResponse
import time
import shutil
import cv2
from PIL import ImageFont, ImageDraw, Image
import time
import shutil
import xml.etree.ElementTree as elemTree
from django.http import FileResponse
import mimetypes
import sys
import fontforge
import subprocess

# sys.path.append((os.path.dirname(os.path.abspath(os.path.dirname(os.path.abspath(os.path.dirname(__file__)))))))

# from Attr2Font import main as attr2font
# from Attr2Font import *

def preprocessForDMFont():
    start = time.time()
    print("preprocess for DM-Font start...")
    kor_characters = ['값', '같', '곬', '곶', '깎', '넋', '늪', '닫', '닭', '닻', '됩', '뗌', '략', '몃', '밟', '볘',
    '뺐', '뽈', '솩', '쐐', '앉', '않', '얘', '얾', '엌', '옳', '읊', '죡', '쮜', '춰', '츄', '퀭', '틔', '핀', '핥',
    '후']
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
    trans_list = [x for x in os.listdir(trans_target) if x.endswith(".png")]
    
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
    cmd = "source /home/ubuntu/fontvenv/bin/activate && python ../Attr2Font/main.py --phase inference --data_root ../data_new --check_path ../Attr2Font/bestModel/ --infer_path ../attr2font_inference"
    cmd += " --attr_list"
    for attr in attr_list:
        cmd += " " + str(attr)
    sp = subprocess.call('/bin/bash -c "$GREPDB"', shell=True, env={'GREPDB': cmd})
    print("attr2font inference finish :", time.time() - start)
    
def dmfont_inference():
    start = time.time()
    print("dmfont inference start")
    cmd = "source /home/ubuntu/fontvenv/bin/activate && python ../fewshot-font-generation/inference.py ../dmfont_config/kor_eval.yaml ../dmfont_config/kor_ttf.yaml --model DM"
    cmd += " --weight ../dmfont_checkpoint/best_dm.pth --result_dir ../dmfont_inference"
    sp = subprocess.call('/bin/bash -c "$GREPDB"', shell=True, env={'GREPDB': cmd})
    print("dmfont inference finish :", time.time() - start)
    
def make_png_to_svg():
    start = time.time()
    print("make png to svg start")
    png_dir = "../dmfont_inference/inference/"
    file_list = [_ for _ in os.listdir(png_dir) if _.endswith(".png")]
    fileNames = file_list    
    svg_dir = "../svg_for_fontforge/"
    # 가상환경 적용하면 너무 오래걸리는 문제가 있음(subprocess를 너무많이 호출해서)
    # 그렇다고 한줄 호출하기에는 argument가 너무 길며
    # python module이 아니기에 import 할수도없음
    # 임시적으로 local os.system으로 cmd 실행
    for fileName in file_list[:len(file_list)//2]:
#         cmd = "source /home/ubuntu/fontvenv/bin/activate"
        cmd = ""
#         base_cmd = " && /home/ubuntu/.cargo/bin/vtracer"
        base_cmd = "/home/ubuntu/.cargo/bin/vtracer"
        base_opt = " --preset bw --mode pixel"
        cmd += base_cmd + base_opt 
        cmd += " --input " + png_dir + fileName
        cmd += " --output " + svg_dir + fileName.split(".")[0] + ".svg"
        os.system(cmd)
#     sp = subprocess.call('/bin/bash -c "$GREPDB"', shell=True, env={'GREPDB': cmd})

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
    font = fontforge.font() # new font
    font.encoding = 'UnicodeFull'
    font.version = '1.0'
    font.weight = 'Regular'
    font.fontname = "Ganafont"
    font.familyname = "Ganafont"
    font.fullname = "Ganafont"
    
    svgFilePaths = "../svg_for_fontforge/"
    svg_list = os.listdir(svgFilePaths)
    
    char_list = os.listdir(svgFilePaths)
    for char in char_list:
        current_char = char.split(".")[0]
        glyph = font.createChar(ord(current_char), current_char)
        glyph.importOutlines(svgFilePaths + char)
        
    result_path = "../result_ttf/"
    if not os.path.isdir(result_path):
        os.mkdir(result_path)
    font.generate(result_path + font.fontname + ".ttf")
    print("svg to ttf finish :", time.time() - start)
    
def change_sample(sample_text):
    sample_path = "/srv/KDT_B4/dongyeong_book/static/sample/"
    image_name = "sample.png"
    source_ttf = "../result_ttf/Ganafont.ttf"
    
    # 폰트 크기
    font_size = 40
    
    # 줄 수
    line = (len(sample_text)//10) + 1 if len(sample_text) != 10 else 1
    
    # 배경 이미지 크기
    W, H = (len(sample_text) * font_size, font_size * line)
    
    # 흰색 배경
    image = Image.new('RGB', (W, H), (255, 255, 255))
    
    font = ImageFont.truetype(source_ttf, font_size)
    # 이미지 생성
    draw = ImageDraw.Draw(image)

    split_text = [sample_text[i:i+10] for i in range(0, len(sample_text), 10)]
    for i in range(0, line):
        # 배경 중간에 글자 배치
        draw.text((0, (i*font_size)), split_text[i], fill="black", font=font)
    image.save(sample_path + image_name)
    return sample_text
    
def downloadFile(request):
    download_dir = "../result_ttf/"
    file_name = "Ganafont.ttf"
    file = open(download_dir + file_name, 'rb')
    response = FileResponse(file)
    return response

def readServerState():
    serverStateFilePath = "../server_state/server_state"
    f = open(serverStateFilePath, 'r')
    line = f.readline()
    f.close()
    return line

def setServerState(state):
    serverStateFilePath = "../server_state/server_state"
    f = open(serverStateFilePath, 'w')
    line = f.write(state)
    f.close()

def ganafont(request):
    test = ""
    attr_list = [50, 50, 50, 50, 50, 50, 50, 50, 50, 50]
    sample_text = "가나폰트"
    # 현재 로컬에 데이터가 저장되기 때문에 이렇게 안하면 이전에 한 사람이 남긴걸 봐버림(지금도 여러 사람이 동시에 하면 봐버릴듯)
    sample_text = change_sample(sample_text)
    downloadable = False
    serverState = readServerState()
    if request.method == "POST":
        if request.POST.get("_method") == "generate":
            if serverState != "available":
                serverState = "not available"
            else:
                setServerState("not available")
                start = time.time()
                attr_list = []
                for x in range(1,11):
                    target = "attr_"+str(x)
                    attr_list.append(int(request.POST.get(target)))
                attr2font_inference(attr_list)
                preprocessForDMFont()
                dmfont_inference()
                make_png_to_svg()
                edit_svg_view_box()
                svg_to_ttf()
                sample_text = change_sample(request.POST.get("keyword"))
                setServerState("available")
                downloadable = True
                print("font generation time :", time.time() - start)
        elif request.POST.get("_method") == "sample":
            attr_list = []
            for x in range(1,11):
                target = "attr_"+str(x)
                attr_list.append(int(request.POST.get(target)))
            sample_text = change_sample(request.POST.get("keyword"))
    return render(request, "ganafont.html", {"attr_list":attr_list, "sample_text":sample_text, "serverState":serverState, "downloadable":downloadable})