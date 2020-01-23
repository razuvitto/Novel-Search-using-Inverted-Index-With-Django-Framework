# Coded with <3 Razuvitto
# location : retrieval/views.py
# April 2018

from django.shortcuts import render
from retrieval import main

def result(request):
    return render(request, 'hasil.html')


def import_csv(request):                                                    
    if request.method == 'POST':
        text = request.POST['input_text']
        result, query, execute_time, idnya, scorenya, judulnya, isinya, authornya, attrs, proximity, query, queries = main.main(text)
        content = {'result': result, 'query': query, 'execute_time': execute_time, 'idnya': idnya, 'scorenya': scorenya, 'judulnya': judulnya, 'isinya': isinya, 'authornya': authornya, 'attrs':attrs, 'proximity': proximity, 'query': query, 'queries': queries}
        return render(request, 'hasil.html', content)
    return render(request, 'index.html')

def novel_page(request, id):
    dict_title, dict_author, dict_text, dict_cover = main.detail()
    contentnya = {'id': id, 'dict_title' : dict_title, 'dict_author': dict_author, 'dict_text': dict_text, 'dict_cover': dict_cover}
    return render(request, 'novel.html', contentnya)

