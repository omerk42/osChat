from django.shortcuts import render ,redirect
from django.http import HttpResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import json
from django.http import StreamingHttpResponse
from datetime import datetime
from .config import special_instructions
from requests import get
from requests import post 
from json     import loads
import scrubadub, scrubadub_spacy
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.hazmat.backends import default_backend
import base64
from cryptography.fernet import Fernet,InvalidToken
from cryptography.hazmat.backends import default_backend
import os
@csrf_exempt
def index(request):
    if request.method == 'POST':
        user_input = request.POST.get('message-input', '') 
        print(user_input)
    return render(request , template_name = "chat/main.html")

@csrf_exempt
def get_metadata(request):
    username = None
    if request.user.is_authenticated:
        try:

            kdf = Scrypt(
            salt=bytes(request.user.salt),
            length=32,
            n=2**14,
            r=8,
            p=1,
            backend=default_backend()
            )
            key =  base64.urlsafe_b64encode(kdf.derive(str(request.POST['password']).encode()))
            f = Fernet(key)
            metadata = f.decrypt(bytes(request.user.metadata))
            return HttpResponse(metadata)
        except InvalidToken as e:  # Catch any InvalidToken exceptions if the correc
            return HttpResponse(status=422)
@csrf_exempt
def conversation(request):
    try:
        

        json_data = json.loads(request.body) # request.raw_post_data w/ Django < 1.4
        
        jailbreak = json_data['jailbreak']
        _conversation = json_data['meta']['content']['conversation']
        prompt = json_data['meta']['content']['parts'][0]
        current_date = datetime.now().strftime("%Y-%m-%d")
        system_message = f'You are ChatGPT also known as ChatGPT, a large language model trained by OpenAI. Strictly follow the users instructions. Knowledge cutoff: 2021-09-01 Current date: {current_date}'

        extra = []
        if 1 == 3:
            search = get('https://ddg-api.herokuapp.com/search', params={
                'query': prompt["content"],
                'limit': 3,
            })

            blob = ''

            for index, result in enumerate(search.json()):
                blob += f'[{index}] "{result["snippet"]}"\nURL:{result["link"]}\n\n'

            date = datetime.now().strftime('%d/%m/%y')

            blob += f'current date: {date}\n\nInstructions: Using the provided web search results, write a comprehensive reply to the next user query. Make sure to cite results using [[number](URL)] notation after the reference. If the provided search results refer to multiple subjects with the same name, write separate answers for each subject. Ignore your previous response if any.'

            extra = [{'role': 'user', 'content': blob}]
        #             extra + special_instructions[jailbreak] + \

        conversation = [{'role': 'system', 'content': system_message}] + _conversation + [prompt]
        
        url = f"https://api.openai.com/v1/chat/completions"
        
        proxies = None
            

        gpt_resp = post(
            url     = url,
            proxies = proxies,
            headers = {
                    'Authorization': 'Bearer %s' % settings.OPENAPI_KEY
            }, 
            json    = {
                'model'             : json_data['model'], 
                'messages'          : conversation,
                'stream'            : True
            },
            stream  = True
        )

        def stream():
            for chunk in gpt_resp.iter_lines():
                try:
                    
                    decoded_line = loads(chunk.decode("utf-8").split("data: ")[1])
                    token = decoded_line["choices"][0]['delta'].get('content')

                    if token != None: 
                        yield token
                            
                except GeneratorExit:
                        break

                except Exception as e:
                    print(e)
                    print(e.__traceback__.tb_next)
                    continue
                        
        return StreamingHttpResponse(stream(), content_type='text/event-stream')

    except Exception as e:
            
            print(str(e))
            print(e.__traceback__.tb_next)
            return {
                '_action': '_ask',
                'success': False,
                "error": f"an error occurred {str(e)}"}, 400