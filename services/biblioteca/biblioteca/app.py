# -*- coding: utf-8 -*-

import re
import urllib
import HTMLParser
import itertools
from BeautifulSoup import BeautifulSoup

from flask import Flask, Response

unescape = HTMLParser.HTMLParser().unescape

app = Flask(__name__)

class Book(object):
    def __init__(self, title, author=None, publisher=None, isbn=None, notes=None):
        self.title = title
        self.author = author
        self.publisher = publisher
        self.isbn = isbn
        self.notes = notes

    def xml(self):
        xml = ''
        xml += '<entity kind="book" type="list" representative="%s">' % self.title
        xml +=     '<entity kind="title" type="string">%s</entity>' % self.title
        xml +=     '<entity kind="author" type="string">%s</entity>' % self.author if self.author else ''
        xml +=     '<entity kind="publisher" type="string">%s</entity>' % self.publisher if self.publisher else ''
        xml +=     '<entity kind="isbn" type="string">%s</entity>' % self.isbn if self.isbn else ''
        xml +=     '<entity kind="notes" type="string">%s</entity>' % self.notes if self.notes else ''
        xml += '</entity>'
        return xml

def normalize(kv):
    if (kv[0] == u'Autor'):
        return ('author', kv[1])
    if (kv[0] == u'Título'):
        return ('title', kv[1])
    if (kv[0] == u'Publicação'):
        return ('publisher', kv[1])
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
        books.append(Book(**book))
    return books

@app.route("/search/<query>")
def search(query):
    books = library_search(query)
    xml =  '<entity type="list">'
    for book in books:
        xml += book.xml()
    xml += '</entity>'
    return Response(response=xml, mimetype="application/xml")
