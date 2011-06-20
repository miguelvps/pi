# -*- coding: utf-8 -*-

import re
import urllib
import urllib2
import socket
import HTMLParser
import itertools
from BeautifulSoup import BeautifulSoup

from flask import Flask, Response, request

unescape = HTMLParser.HTMLParser().unescape
socket.setdefaulttimeout(10)

app = Flask(__name__)
app.config.from_envvar('SETTINGS', silent=True)

class Book(object):
    def __init__(self, title, author=None, publisher=None, isbn=None, notes=None, url=None):
        self.title = title
        self.author = author
        self.publisher = publisher
        self.isbn = isbn
        self.notes = notes

    def to_xml_shallow(self, url):
        return '<entity type="string" service="Biblioteca" url="/book/%s">%s</entity>' % (url, self.title)

    def to_xml(self):
        xml = '<entity type="record">'
        xml +=     '<entity kind="title" type="string">%s</entity>' % self.title
        xml +=     '<entity kind="pessoa" name="Author" type="string">%s</entity>' % self.author if self.author else ''
        xml +=     '<entity kind="publisher" name="Publisher" type="string">%s</entity>' % self.publisher if self.publisher else ''
        xml +=     '<entity kind="isbn" name="ISBN" type="string">%s</entity>' % self.isbn if self.isbn else ''
        xml +=     '<entity name="Notes" type="string">%s</entity>' % self.notes if self.notes else ''
        xml += '</entity>'
        return xml

def normalize(kv):
    if (kv[0] == u'Autor'):
        return ('author', kv[1].replace('&', '&amp;'))
    if (kv[0] == u'Título'):
        return ('title', kv[1].replace('&', '&amp;'))
    if (kv[0] == u'Publicação'):
        return ('publisher', kv[1].replace('&', '&amp;'))
    if (kv[0] == u'Notas gerais'):
        return ('notes', kv[1].replace('&', '&amp;'))
    if (kv[0] == u'ISBN'):
        match = re.search("([\d,-]+)", kv[1])
        return ('isbn', match.group(0) if match else None) #
    return None

BASE_URL = "http://biblioteca.fct.unl.pt:8888/docbweb/"
# StartRec=0 -> start at this record
# RecPag=10 -> number of records per page
# Form=COMP -> display type {COMP, LISTA, ...}
def library_search(query, start=0, amount=20):
    url = BASE_URL + "pesqres.asp?Base=ISBD&Form=COMP&StartRec=%s&RecPag=%s&SearchTxt=%s" % (start, amount, urllib.quote(query.replace(' ', '+')))
    books = []
    page = urllib2.urlopen(url).read()
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
                entry = normalize((key,value))
                if entry:
                    book[entry[0]] = entry[1]
        books.append(Book(**book))
    return books

keywords = [ u'biblioteca', u'livro', u'livros', u'catalogo', u'catálogo',
             u'catalogos', u'catálogos' ]

@app.route("/")
def search():
    query = urllib.unquote_plus(request.args.get('query', ''))
    query = ' '.join([q for q in query.split(' ') if q not in keywords])
    books = library_search(query, amount=2)
    xml =  '<entity type="list">'
    if books:
        xml += books[0].to_xml_shallow(query)
    xml += '</entity>'
    return Response(response=xml, mimetype="application/xml")

@app.route("/book/<path:url>")
def book(url):
    books = library_search(url, amount=2)
    xml = books[0].to_xml()
    return Response(response=xml, mimetype="application/xml")
