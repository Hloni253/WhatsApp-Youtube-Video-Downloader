from django.shortcuts import render, redirect
from django.http import HttpResponse, FileResponse
from django.views.decorators.csrf import csrf_exempt
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
from youtube_search import YoutubeSearch
import youtube_dl
import os
import re

tube_file_url = ""
file_title = ""
search_name = ""
num = ""

def HomePage(request):
    global tube_file_url
    if request.method == "POST":
        message = request.POST.get("Search")
        mess_to_string = str(message)
        verify_url = "https://www.youtube.com/watch?v="
        second_verify_url = "https://youtu.be/"
        print("First")
        if mess_to_string.startswith(verify_url) or mess_to_string.startswith(second_verify_url):
            tube_file_url = mess_to_string
            return redirect("/Down/D")
        else:
            return redirect("/")
    else:
        pass
    
    return render(request, "Home/Home.html")


@csrf_exempt
def Webhook(request):
    global tube_file_url
    global search_name
    global num
    response = MessagingResponse()
    msg = response.message()
    if request.method == "POST":
        message = request.POST.get("Body")
        from_num = request.POST.get("From")
        verify_url = "https://www.youtube.com/watch?v="
        second_verify_url = "https://youtu.be/"
        try:
            int(message)
            num = int(message)
            results = YoutubeSearch(search_name, max_results=10).to_dict()
            num = num - 1
            result = results[num]['url_suffix']
            tube_file_url = 'https://www.youtube.com{}'.format(result)
            msg.body("https://e430639017e5.ngrok.io/Down/D")

        except ValueError:
            mess_to_string = str(message)
            if mess_to_string.startswith(verify_url) or mess_to_string.startswith(second_verify_url):
                try:
                    YouTube(message)
                    tube_file_url = message
                    msg.body("https://e430639017e5.ngrok.io/Down/D")
                except:
                    msg.body("Couldn't Find File")
            else:
                results = YoutubeSearch(message, max_results=10).to_dict()
                search_name = message
                for i in range(10):
                    r = results[i]['title']
                    msg.body('--\n{0} {1}\n--'.format(i+1,r))
    
    return HttpResponse(response.to_xml(), content_type='text/xml')

def Choose_Format(request):
    global tube_file_url
    global file_title
    
    ydl_opts = {}
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        vid = ydl.extract_info(
            '{}'.format(tube_file_url),
            download=False
            )
        
    file_title = vid['title']
    
    
    context = {
        "file":vid['title'],
        }
    
    return render(request, "Home/Download.html", context)

def replace_all(replace, file_string):
    return re.sub('[!@#$%^&*()-_=+:;<>?/\|]', replace, file_title)

def Download(request, file_type):
    global tube_file_url
    global file_title
    
    if file_type == "v":
        
        replace = ' '
        file_name = replace_all(replace, file_title)
        ydl_opts = {'outtmpl': 'media/{}.mp4'.format(file_name)}
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([tube_file_url])
        
        return FileResponse(open('media/{}.mp4'.format(file_name),'rb'),as_attachment=True)
    elif file_type == "a":
        replace = ' '
        file_name = replace_all(replace, file_title)
        ydl_opts = {'outtmpl': 'media/{}.mp4'.format(file_name),
                    'format':'bestaudio'}
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([tube_file_url])
        return FileResponse(open('media/{}.mp4'.format(file_name),'rb'),as_attachment=True)
    else:
        return redirect("/")
