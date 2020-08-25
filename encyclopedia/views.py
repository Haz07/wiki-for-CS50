import secrets

from django.shortcuts import render
from django import forms
from django.http import HttpResponseRedirect
from django.urls import reverse

from . import util

from markdown2 import Markdown

markdowner = Markdown()


class newForm(forms.Form):
    title = forms.CharField(label="Entry Title", widget=forms.TextInput)
    content = forms.CharField(widget=forms.Textarea)
    edit = forms.BooleanField(initial=False, widget=forms.HiddenInput(), required=False)



def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })


def entry(request, entry_name):
    entries = util.list_entries()
    if entry_name in entries:
        page = util.get_entry(entry_name)
        pagehtml = markdowner.convert(page)
        return render(request, "encyclopedia/page.html", {
            'page': pagehtml,
            'title': entry_name
        } )
    else:
        return render(request, "encyclopedia/error.html", {'title' : entry_name})

def search(request):
    value = request.GET.get('q','')
    if (util.get_entry(value)):
        return HttpResponseRedirect(reverse("entry", kwargs={'entry_name': value}))
    else:
        subEntries = []
        for entry in util.list_entries():
            if value.upper() in entry.upper():
                subEntries.append(entry)

        return render(request, "encyclopedia/index.html", {
            "entries": subEntries,
            "search": True,
            "value": value
        })

def newPage(request):
    if request.method == "POST":
        form = newForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            content = form.cleaned_data["content"]
            if (util.get_entry(title) is None or form.cleaned_data["edit"] is True):
                util.save_entry(title, content)
                return HttpResponseRedirect(reverse("entry", kwargs={'entry_name': title}))
            else:
                return render(request, "encyclopedia/newpage.html", {
                    "form": form,
                    "existing": True,
                    "entry": title
                })
        else:
            return render(request, "encyclopedia/newpage.html", {
                "existing": False,
                "form": form
            })

    else:
        return render(request, "encyclopedia/newpage.html", {
            "existing": False,
            "form": newForm()
        })

def edit(request, entry_name):
    page = util.get_entry(entry_name)
    if page is None:
        return render(request, "encyclopedia/error.html", {
            "title": entry_name
        })
    else:
        form = newForm()
        form.fields["title"].initial = entry_name
        form.fields["content"].initial = page
        form.fields["edit"].initial = True
        return render(request, "encyclopedia/newpage.html", {
            "form" : form,
            "title" : form.fields["title"].initial,
            "edit" : form.fields["edit"].initial
        })

def random(request):
    entries = util.list_entries()
    randomEntry = secrets.choice(entries)
    return HttpResponseRedirect(reverse("entry", kwargs={'entry_name': randomEntry}))