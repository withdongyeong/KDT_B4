from django.http import HttpResponse
from django.shortcuts import render

from typing import Optional
import torch
import transformers
from transformers import GPT2LMHeadModel, AutoModelWithLMHead, PreTrainedTokenizerFast
from fastai.text.all import *
import fastai
import re
import os
import pickle
from django.conf import settings

MODEL_PATH = 'skt/kogpt2-base-v2'
model = GPT2LMHeadModel.from_pretrained(MODEL_PATH)
tokenizer = PreTrainedTokenizerFast.from_pretrained(MODEL_PATH,
                                                    bos_token='<s>',
                                                    eos_token='</s>',
                                                    unk_token='<unk>',
                                                    pad_token='<pad>',
                                                    mask_token='<mask>')
device = torch.device('cpu')
model.load_state_dict(torch.load("kbbong.pt", map_location=device))

def generate_title(model, tokenizer, text: str, max_length, temperature) -> str:
    device = 'cuda:0' if torch.cuda.is_available() else 'cpu'

    model.eval()
    count = 0
    sent = text[:]
    text = tokenizer.bos_token + text
    generated_token = ''

    with torch.no_grad():
        model = model.to(device)
        while generated_token != '</s>':

            if count > max_length:
                break

            input_ids = tokenizer.encode(text, return_tensors='pt')
            input_ids = input_ids.to(device)

            predicted = model(input_ids)
            pred = predicted[0]

            # temperature 적용
            logit = pred[:, -1, :] / temperature
            logit = F.softmax(logit, dim=-1)
            prev = torch.multinomial(logit, num_samples=1)
            generated_token = tokenizer.convert_ids_to_tokens(prev.squeeze().tolist())

            sent += generated_token.replace('▁', ' ')
            text += generated_token.replace('▁', ' ')
            count += 1

        sent = sent.replace('</s>', '')

        return sent

def ktube(request):
    generated_text = "국뽕스러운 문장을 생성합니다."
    keyword = "텍스트를입력하세요"
    length = "30"
    temperature = "0.5"
    if request.method == "POST":
        keyword = request.POST.get("keyword")
        length = int(request.POST.get("length"))
        temperature = float(request.POST.get("temperature"))
        generated_text = generate_title(model, tokenizer, text=keyword, max_length=length, temperature=temperature)
    return render(request, 'generate_page.html', {"generated_text" : generated_text, "before_keyword":keyword, "before_length":length, "before_temperature":temperature})

if __name__ == "__main__":
    "test"