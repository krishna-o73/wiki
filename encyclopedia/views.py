from random import random, randrange
from django import forms
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
import markdown2
from . import util

class SearchForm(forms.Form): # lhs search form
    search = forms.CharField(label='', 
    widget=forms.TextInput(attrs={'placeholder':'Search Encyclopedia'}))


class CreateForm(forms.Form):
    title = forms.CharField(
        label="Title of your wiki page",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    content = forms.CharField(
        label="Content of the page",
        widget=forms.Textarea(attrs={'class': 'form-control'})
    )

def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def wiki(request, query):
    result = util.get_entry(query)
    if result == None:
        return render(request, "encyclopedia/error.html", {
            "error_message": (f"Query {query} not found!")
        })
    else:
        return render(request, "encyclopedia/display.html", {
            "query": query.capitalize(),
            "query_title": query,
            "query_result": markdown2.markdown(util.get_entry(query))
        })

def create_page(request):
    if request.method == "POST":
        form = CreateForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            content = form.cleaned_data["content"]
            exists = util.get_entry(title)

            if exists == None:
                util.save_entry(title, content)
                return HttpResponseRedirect(f"wiki/{title}")
            else:
                return render(request, "encyclopedia/create.html", {
                    "create_form": form,
                    "error": f"Page with the title of {title} already exists!"
                })

    return render(request, "encyclopedia/create.html", {
        "create_form": CreateForm()
    })

def search(request):
    if request.method == "GET":
        query = request.GET["q"]

        if util.get_entry(query):
            return HttpResponseRedirect(f'wiki/{query}')
        else:
            results = [e for e in util.list_entries() if query.lower() in e.lower() ]

            return render(request, "encyclopedia/search.html", {
                "results": results
            })

def edit(request, entry):
    if request.method == "POST":
        title = request.POST["entry_title"]
        if(util.get_entry(title)):
            content = request.POST["edited_content"]
            util.save_entry(title,content)
            return HttpResponseRedirect(f"../wiki/{title}")
        else:
            return render(request, "encyclopedia/error.html", {
                "error_message": (f"Query {title} not found!")
            })

    return render(request, "encyclopedia/edit.html", {
        "entry_title": entry,
        "entry_content": util.get_entry(entry)
    })

def random_wiki(request):
    index = randrange(len(util.list_entries()))
    return wiki(request, util.list_entries()[index])