#!/usr/bin/env python
# coding: utf-8

# In[135]:


import os
import telebot
import io
import csv
import time
import json
from datetime import date 
import re
from dotenv import load_dotenv

load_dotenv()
#Only needed for ver simplified version of the code
project_home_dir = os.getenv("TELEGRAMPA_PROJECT_HOME")




regex_config = {"remind":re.compile("remind ?me|RM|set reminder", flags=re.IGNORECASE),
                "amount":re.compile("(\$[0-9]?[0-9]\.?[0-9]?[0-9]?)|[0-9]?[0-9]\.[0-9][0-9]", flags=re.IGNORECASE)
                }


# In[136]:


def track_amounts(message):
    
    #find a model that will predict the date of the intended reminder from nlp
    #make sure it can handle "in five minutes" and "on tuesday"
    try:
        colheaders = ["date","unix_timestamp","category","full_text","label","amount"]
        dollar_amount = re.search(regex_config["amount"], message.text).group()
        
        float_dollar = float(dollar_amount.replace("$",""))
        label = str(message.text).replace(dollar_amount, "").strip().lower().title()
        csvdata = [date.today(),time.time(),"amount",message.text, label, float_dollar]

        fn = os.path.join(project_home_dir, "dash_app/data/spend.csv")
        if not os.path.exists(fn): 
            f = open(fn, mode='w')
            spend_writer = csv.writer(f, quoting=csv.QUOTE_NONNUMERIC)
            spend_writer.writerow(colheaders)
        else:
            f = open(fn, mode='a')
            spend_writer = csv.writer(f, quoting=csv.QUOTE_NONNUMERIC)

        spend_writer.writerow(csvdata)
        f.close()
        
    except Exception as e:
        print(e)


# In[137]:


example_msg = ""
bot = telebot.TeleBot(os.getenv("TELEGRAM_BOT_KEY"))

@bot.message_handler(func=lambda m: True)
def save_data(message):
    #save to the text file
    try:
        #in the dashboard we'll display it as just a list of notes
        
        colheaders = ["date","unix_timestamp","category","full_text"]

        if re.search(regex_config["amount"], message.text):
            track_amounts(message)
            bot.reply_to(message, f"Okay, I've logged that amount for you")
            
        elif re.search(regex_config["remind"],message.text):
            pass
        example_msg = message.text
        csvdata = [date.today(),time.time(),"all_logs",message.text]
        fn = os.path.join(project_home_dir, "dash_app/data/full_log.csv")

        if not os.path.exists(fn): 
            f = open(fn, mode='w')
            spend_writer = csv.writer(f, quoting=csv.QUOTE_NONNUMERIC)
            spend_writer.writerow(colheaders)
        else:
            f = open(fn, mode='a')
            spend_writer = csv.writer(f, quoting=csv.QUOTE_NONNUMERIC)


        #bot.reply_to(message, message.text)
    except Exception as e:
        print(e)

@bot.message_handler(regexp=regex_config["remind"])
def remind_me(message):
    
    #find a model that will predict the date of the intended reminder from nlp
    #make sure it can handle "in five minutes" and "on tuesday"
    try:
        pass
#         csvdata = [date.today(),time.time(),"reminder",message.text]

#         fn = os.path.join(project_home_dir, "dash_app/data/reminders.csv")
#         writer.writerow(csvdata)
#         with open(fn, mode='w') as f:
#             print(output.getvalue(), file=f)
        
    except Exception as e:
        print(e)
                
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, u"Hello, welcome to this bot!")
    
bot.polling()


# In[134]:


get_ipython().system("jupyter nbconvert --output-dir='/home/keshev/Repos/TelegramPA/telegram_listener/' --to script telegram_pa_scratchpad.ipynb")

