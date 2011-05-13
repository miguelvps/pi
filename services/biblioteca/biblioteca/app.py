# -*- coding: utf-8 -*-

import re
import urllib
import HTMLParser
import itertools
from BeautifulSoup import BeautifulSoup

from flask import Flask

unescape = HTMLParser.HTMLParser().unescape

app = Flask(__name__)


def normalize(kv):
    if (kv[0] == u'Autor'):
        return ('author', kv[1])
    if (kv[0] == u'Título'):
        return ('title', kv[1])
    if (kv[0] == u'Publicação'):
        return ('publish', kv[1])
    if (kv[0] == u'Notas gerais'):
        return ('notes', kv[1])
    if (kv[0] == u'ISBN'):
        match = re.search("([\d,-]+)", kv[1])
        return ('isbn', match.group(0) if match else None) #
    return None

# StartRec=0 -> start at this record
# RecPag=10 -> number of records per page
# Form=COMP -> display type {COMP, LISTA, ...}
def library_search(query, start=0, amount=20):
    url = "http://biblioteca.fct.unl.pt:8888/docbweb/pesqres.asp?Base=ISBD&Form=COMP&StartRec=%s&RecPag=%s&SearchTxt=%s" % (start, amount, urllib.quote(query))
    books = []
    page = urllib.urlopen(url).read()
    xml = BeautifulSoup(page)
    odd = xml.findAll('div', { 'class': "recordodd" })
    even = xml.findAll('div', { 'class': "record" })
    for record in itertools.chain(*zip(odd,even)):
        entries = record.find('table').find('table').findAll('tr')
        book = {}
        for entry in entries:
            kv = entry.findAll('td')
            if kv:
                key = unescape(kv[0].text).split(':')[0]
                value = unescape(kv[1].text)
                kv = normalize((key,value))
                if kv:
                    book[kv[0]] = kv[1]
        books.append(book)
    return books

@app.route("/search/<query>")
def search(query):
    books = library_search(query)
    return str(books)

