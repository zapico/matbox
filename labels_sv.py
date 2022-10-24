#!/usr/bin/env python3
# Copyright 2017 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
import locale
import logging
import os
import mysql.connector
from datetime import date
from aiy.board import Board, Led
from aiy.cloudspeech import CloudSpeechClient
from fpdf import FPDF


def get_hints(language_code):
    if language_code.startswith('sv_'):
        return ('spara',
                'frysa')
    return None

def locale_language():
    language = 'sv_SE'
    return language

def text2int(textnum, numwords={}):
    if not numwords:
      units = [
        "noll", "ett", "två", "tre", "fyra", "fem", "sex", "sju", "åtta",
        "nio", "tio", "elva", "tolv", "tretton", "fjorton", "femton",
        "sexton", "sjutton", "arton", "nitton",
      ]

      tens = ["", "", "tjugo", "treti", "fyrtio", "femtio", "sixtio", "sjutio", "åttio", "nittio"]

      scales = ["hundra", "tusen", "million", "billion", "trillion"]

      numwords["and"] = (1, 0)
      for idx, word in enumerate(units):    numwords[word] = (1, idx)
      for idx, word in enumerate(tens):     numwords[word] = (1, idx * 10)
      for idx, word in enumerate(scales):   numwords[word] = (10 ** (idx * 3 or 2), 0)

    current = result = 0
    for word in textnum.split():
        if word not in numwords:
          raise Exception("Illegal word: " + word)

        scale, increment = numwords[word]
        current = current * scale + increment
        if scale > 100:
            result += current
            current = 0

    return result + current

def main():
    logging.basicConfig(level=logging.DEBUG)

    parser = argparse.ArgumentParser(description='Assistant service example.')
    parser.add_argument('--language', default=locale_language())
    args = parser.parse_args()

    logging.info('Initializing for language %s...', args.language)
    hints = get_hints(args.language)
    client = CloudSpeechClient()
    
    mydb = mysql.connector.connect(
        host='.org',
        user='',
        password='',
        database=''
    )
    
    with Board() as board:
        while True:
            if hints:
                logging.info('Say something, e.g. %s.' % ', '.join(hints))
            else:
                logging.info('Say something.')
            text = client.recognize(language_code=args.language,
                                    hint_phrases=hints)
            if text is None:
                logging.info('You said nothing.')
                continue

            logging.info('You said: "%s"' % text)
            text = text.lower()
            if 'spara' in text:
                food = text.replace('spara', '', 1)
                location = 'kyl'
                date_saved = date.today()
                #Save in database
                mycursor = mydb.cursor()
                val = [food,location,date_saved,1,1]
                sql = "INSERT INTO boxes (name,location,date,user_id,active) VALUES (%s,%s,%s,%s,%s)"
                mycursor.execute(sql,val)
                mydb.commit()
                #Get back id              
                food_id = mycursor.lastrowid
                #Print label
                pdf= FPDF(orientation='L',unit='mm', format= (28,89))
                pdf.set_auto_page_break(0)
                pdf.add_page()
                pdf.set_xy(5,5)
                pdf.set_font('Arial','B',22)
                pdf.cell(0,10, txt= food.upper())
                pdf.set_font('Arial','',11)
                pdf.set_xy(8,16)
                pdf.cell(0,10, txt= str(date_saved))
                pdf.set_xy(65,16)
                pdf.cell(0,10, txt= 'ID:' + str(food_id))
                                
                pdf.output('label.pdf','F')
                os.system('lp label.pdf')


                logging.info('Sparat %s i kylen' %food)
            elif 'frysa' in text:
                food = text.replace('frysa', '', 1)
                location = 'frys'
                date_saved = date.today()
                #Save in database
                mycursor = mydb.cursor()
                val = [food,location,date_saved,1,1]
                sql = "INSERT INTO boxes (name,location,date,user_id,active) VALUES (%s,%s,%s,%s,%s)"
                mycursor.execute(sql,val)
                mydb.commit()
                #Get back id              
                food_id = mycursor.lastrowid
                #Print label
                pdf= FPDF(orientation='L',unit='mm', format= (28,89))
                pdf.set_auto_page_break(0)
                pdf.add_page()
                pdf.set_xy(5,5)
                pdf.set_font('Arial','B',22)
                pdf.cell(0,10, txt= food.upper())
                pdf.set_font('Arial','',11)
                pdf.set_xy(8,16)
                pdf.cell(0,10, txt= str(date_saved))
                pdf.set_xy(65,16)
                pdf.cell(0,10, txt= 'ID:' + str(food_id))
                #os.system('lp label.pdf')


                logging.info('Sparat %s i kylen' %food)
            elif 'ta bort' in text:
                foodid = text.replace('ta bort','',1)
                if type(foodid) != int: foodid = text2int(foodid)
                logging.info(foodid)
                mycursor = mydb.cursor()
                val = [foodid]
                sql = "UPDATE boxes SET active = 0 WHERE id = %s"
                mycursor.execute(sql,val)
                mydb.commit()
            elif 'disco' in text:
                board.led.state = Led.BLINK
            elif 'stopp' in text:
                board.led.state = Led.OFF
            elif 'ljus' in text:
                board.led.state = Led.OFF               
            elif 'goodbye' in text:
                break

if __name__ == '__main__':
    main()
