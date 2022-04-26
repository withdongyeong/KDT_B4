import os
from django.shortcuts import render
from django.http import HttpResponse

def attr2font_inference(attr_list):
    cmd = "python ../Attr2Font/main.py --phase inference --data_root ../data --check_path ../Attr2Font/bestModel/ --infer_path ../inference"
    cmd += " --attr_list"
    for attr in attr_list:
        cmd += " " + str(attr)
    os.system(cmd)

def ganafont(request):
    test = ""
    if request.method == "POST":
        attr_list = []
        for x in range(1,38):
            target = "attr_"+str(x)
            attr_list.append(int(request.POST.get(target)))
        attr2font_inference(attr_list)
    return render(request, "ganafont.html", {"test_sentence":test})