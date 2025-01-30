import os

from pprint import pprint
import csv
import requests
from bs4 import BeautifulSoup
import openpyxl


import django
# Django setup
os.environ['DJANGO_SETTINGS_MODULE'] = 'verbalvoyager.settings'
django.setup()

new_words = []
genus_key = {
    'м.р.': 'm',
    'ж.р.': 'f',
    'ср.р.': 'n'
    }


def load_words():
    wb = openpyxl.load_workbook("/home/peka97/Verbal-Voyager/verbalvoyager/French Words (edit).xlsx")
    ws = wb.active
    word = None
    translate = None
    genus = None
    row_num = 1
    
    for idx, row in enumerate(ws.iter_rows(values_only=True)):
        text = row[0]
        
        if word is None:
            word = text
            if row[1]:
                try:
                    genus = genus_key[row[1]]
                except KeyError:
                    genus = None
            
        else:
            translate = text
            
        if word and translate:
            # print(f'Word: {word} ({genus}). Translate: {translate}')
            new_words.append(
                FrenchWord(word=word, genus=genus, translate=translate)
            )
            
            word = None
            translate = None
            genus = None
            
        # row_num += 1
        
        # if row_num > 20:
        #     break
    
    # wb.save('/home/peka97/Verbal-Voyager/verbalvoyager/French Words (edit).xlsx')
        
        
def create_words():
    from django.db import transaction
    
    with transaction.atomic():
        FrenchWord.objects.bulk_create(new_words)    
        
def update_words():
    from django.db import transaction
    
    with transaction.atomic():
        FrenchWord.objects.bulk_update(new_words, 'genus')
            
def delete_words():
    FrenchWord.objects.all().delete()


def get_genus(word):
    url = f'https://www.translate.ru/перевод/французский-русский/{word}'
    resp = requests.get(url, timeout=10)
    
    if resp.status_code != 200:
        return None
    
    soup = BeautifulSoup(resp.text, "html.parser")
    
    try:
        return soup.find('span', {'class': 'ref_info'}).text
    except AttributeError:
        return None


if __name__ ==  '__main__':
    # get_genus('abeille')
    from exercises.models import FrenchWord

    load_words()
    # # pprint(new_words)
    create_words()
    # update_words()
    # delete_words()