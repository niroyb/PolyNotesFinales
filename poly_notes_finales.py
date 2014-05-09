#!/usr/bin/python
# -*- coding: utf-8 -*-

import ConfigParser
import gmail
import requests
from lxml import etree, cssselect
import os
import time

SESSION = None
SKELETON = """<!DOCTYPE html><html><head><meta charset="UTF-8"><title>Results</title></head><body></body></html>"""
SAVE_LOC = 'results.html'
CONFIG_LOC = 'Login.cfg'

def get_config(section, values):
    assert os.path.exists(CONFIG_LOC), "Missing login info file"
    config = ConfigParser.ConfigParser()
    config.read(CONFIG_LOC)
    return [config.get(section, x) for x in values]

def dossier_login():
    global SESSION
    SESSION = requests.Session()
    url = '''https://www4.polymtl.ca/servlet/ValidationServlet'''
    code, nip, naissance = get_config('Poly', ['code', 'nip', 'naissance'])
    login_info = {'code': code, 'nip': nip, 'naissance': naissance}
    response = SESSION.post(url, data=login_info)
    assert "invalide" not in response.text, 'Login to dossier etudiant failed'
    return response

def select_elements(dom, css_selector):
    selector = cssselect.CSSSelector(css_selector)
    elements = selector(dom)
    return elements

def extract_result_html(html):
    dom = etree.HTML(html)
    table_notes = select_elements(dom, 'table')[2]
    for e in select_elements(table_notes, 'font'):
        e.attrib.clear()
    mini_dom = etree.HTML(SKELETON)
    body = select_elements(mini_dom, 'body')[0]
    body.append(table_notes)
    return etree.tostring(mini_dom, pretty_print=True)

def send_mail(html):
    user, password = get_config('Gmail', ['email', 'password'])
    g = gmail.Gmail(user, password)
    g.send_message_to_self('Update notes finales', html)

def update_result(html):
    old = None
    if os.path.exists(SAVE_LOC):
        with open(SAVE_LOC) as f:
            old = f.read()
    if old != html:
        print time.ctime(), '|| Update!!! saved in', SAVE_LOC
        with open(SAVE_LOC, 'w') as f:
            f.write(html)
        send_mail(html)
    else:
        print time.ctime(), '|| No new results'

def get_hidden_inputs(html):
    dom_result_page = etree.HTML(html)
    hidden_inputs = select_elements(dom_result_page, 'input[type=hidden]')
    input_data = {i.get("name"): i.get("value") for i in hidden_inputs}
    return input_data

def check_final_grades():
    r = dossier_login()
    hidden_input_data = get_hidden_inputs(r.text)
    r = SESSION.post('https://www4.polymtl.ca/servlet/PresentationResultatsTrimServlet', data=hidden_input_data)
    result_html = extract_result_html(r.text)
    update_result(result_html)

def main_loop():
    while True:
        print time.ctime(), '|| Checking final grades for updates...'
        check_final_grades()
        # Wait one hour
        time.sleep(3600)

if __name__ == '__main__':
    main_loop()