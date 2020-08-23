#!/usr/bin/env python
# coding: utf-8

import os, io, time
import telebot
import re, csv, hashlib, json
import operator

import pandas as pd
import hashlib
import datetime
from datetime import date
import jellyfish
from dotenv import load_dotenv

import firebase_admin
from firebase_admin import auth
from firebase_admin import credentials
from firebase_admin import db
from pdb import set_trace

import google.auth
import logging
import httplib2
from googleapiclient.discovery import build


sheet_credentials, project = google.auth.default(scopes=['https://www.googleapis.com/auth/spreadsheets'])
service = build('sheets', 'v4', cache_discovery=False)
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
CHAT_ID = os.getenv("CHAT_ID")

#service_credentials, project_id = google.auth.default()

creds = credentials.ApplicationDefault()
#Only needed for ver simplified version of the code
logging.error(creds)
tracker_message = {}

bot = telebot.TeleBot(os.getenv("TELEGRAM_BOT_KEY"))

# Initialize the app with a service account, granting admin privileges
#cred = credentials.Certificate(os.getenv("GOOGLE_APPLICATION_CREDENTIALS"))
#creds = credentials.Certificate(service_credentials)

# Initialize the app with a service account, granting admin privileges
# firebase_admin.initialize_app(cred, {
#   'databaseURL': 'https://{}.firebaseio.com/'.format(os.getenv("PROJECT_NAME"))
#   })

firebase_admin.initialize_app(creds,{'databaseURL': 'https://{}.firebaseio.com/'.format(creds.project_id)})

# As an admin, the app has access to read and write all data, regradless of Security Rules
ref = db.reference('/')

distinct_message_bins = ref.child("tracker_messages/titles").get()
distinct_message_bins = [v for k,v in distinct_message_bins.items()]


def update_firebase_with_message(latest_tracker_message): 
    # Fetch the service account key JSON file contents
    
    #structuring for firebase structure as a child of the user id
    try:
        user_id = latest_tracker_message["user_id"] 
        users_ref = ref.child('user_notes/{}'.format(user_id))


        message_id = latest_tracker_message["message_id"] 
        message_ref = ref.child('message_attributes/{}'.format(message_id))

        attributes = latest_tracker_message.pop("attributes")

        message_ref.set(attributes)
        users_ref.set(latest_tracker_message)

        return True
    except Exception as e:
        set_trace()

def update_google_sheet_tracker(latest_tracker_message):
    tracker_message_arr = [[v for k,v in latest_tracker_message.items() if k!="attributes"]]
    range_name = "Sheet1"
    update_google_sheet_with_message(tracker_message_arr, range_name)

def update_google_sheet_with_message(values_as_arr, range_name): 
    # values = [
    # [
    #     # Cell values ...
    # ],
    # # Additional rows ...
    # ]
    body = {
        'values': values_as_arr
    }
    SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
    result = service.spreadsheets().values().append(
        spreadsheetId=SPREADSHEET_ID, range=range_name,
        valueInputOption="USER_ENTERED",
        body=body).execute()
    print('{0} cells appended.'.format(result \
                                        .get('updates') \
                                        .get('updatedCells')))
        
def confirm_new_tracker(message,latest_tracker_message): 
    
    unique_tracker_statuses = ref.child('tracker_messages/statuses')
    unique_tracker_titles = ref.child('tracker_messages/titles')

    
    yes_regex = re.compile(r"\bY\b|\byes\b|\bya\b", flags=re.IGNORECASE)
    if yes_regex.search(message.text):
        #insert into the pandas dataframe 
        unique_tracker_statuses.push(latest_tracker_message["status"])
        unique_tracker_titles.push(latest_tracker_message["title"])
        distinct_message_bins.append(latest_tracker_message["title"])


#@bot.message_handler(regexp=command_regex_config["tracker"])
@bot.message_handler(commands=["t","track","tracker"])
def tracker_message_handler(message):
    
    tracker_magnitude_regexes = [{"label":"Spend","units":"$","regex":re.compile(r"(\$[0-9]?[0-9]\.?[0-9]?[0-9]?)|[0-9]?[0-9]\.[0-9][0-9]", flags=re.IGNORECASE)}, 
                             {"label":"Calories","units":"Cal", "regex":re.compile(r"[0-9][0-9]+ ?cal|calo?r?i?e?s? ?[0-9][0-9]",flags=re.IGNORECASE)},
                             {"label":"Distance", "units":"km", "regex":re.compile(r"[0-9][0-9]* ?(k.?m?|m.?i?)",flags=re.IGNORECASE)}                            
                            ]

    from_user = message.from_user
    chat_info = message.chat
    
    dash_message_id = str(datetime.datetime.now()) + str(from_user.id)
    dash_message_id = hashlib.md5(dash_message_id.encode('utf-8')).hexdigest()
    
    latest_tracker_message =   {
                        "message_id": dash_message_id,
                        "chat_id":chat_info.id,
                        "type": "tracker",
                        "status": "Unassigned",
                        "title": "Unassigned",
                        "user_id":from_user.id,
                        "user_name":"{} {}".format(from_user.first_name,from_user.last_name),
                        "datetime_logged":str(datetime.datetime.now()),
                        "message_date":message.date,
                        "input_datetime":str(datetime.datetime.now()), 
                        "content": "Unassigned",
                        "magnitude":30, 
                        "units":"$",
                        "attributes":{
                            "example_attribute_1":"example_attribute_value"
                        },
                        "estimate": "NA"
                      }

    
    
    for search_logic in tracker_magnitude_regexes:
        regexp = search_logic["regex"]
        label = search_logic["label"]
        regex_search_result = regexp.search(message.text) 
        #look for the magnitude

        if regex_search_result:
            #figured out what type of magnitude it is

            latest_tracker_message["status"] = label
            magnitude = regex_search_result.group(1)
            try:
                latest_tracker_message["magnitude"] = float(re.sub("[a-z]|[A-Z]|\\$","",magnitude))
                latest_tracker_message["estimate"] = "{} {}".format(re.sub("[a-z]|[A-Z]|\\$","",magnitude),search_logic["units"])

            except Exception as e:
                print(e)
                #set_trace()
            description = message.text.replace(magnitude, "").replace("/t",'').strip()
            message_distance_arr = [(x, jellyfish.jaro_winkler(description,x)) for x in distinct_message_bins if jellyfish.jaro_winkler(description,x) > 0.91] 

            #assign it accordingly
            
            #TODO 
            #handle the exact match case better
            
            #TODO NEXT
            ##his is also writing empty stuff in when it doesn't know
            if len(message_distance_arr)>=1:
                most_likely_title, dist = max(message_distance_arr,key=operator.itemgetter(1))
                latest_tracker_message["title"] = most_likely_title
                latest_tracker_message["content"] = most_likely_title
                
                #update_firebase_with_message(latest_tracker_message)
                update_google_sheet_tracker(latest_tracker_message)
#                 with open("{}/dash_app/data/tracker_data/{}.json".format(TELEGRAMPA_PROJECT_HOME,dash_message_id),"w") as f:
#                     json.dump(latest_tracker_message, f, indent= 2)
            else:
                #if it is unrecognized ask user if they want to create a new list
                latest_tracker_message["title"] = description
                latest_tracker_message["content"] = description
                
                msg = bot.reply_to(message, 'Would you like to create a new tracker list?')
                try:
                    bot.register_next_step_handler(msg, lambda x: confirm_new_tracker(x, latest_tracker_message))
                    update_google_sheet_tracker(latest_tracker_message)

                except Exception as e:
                    print(e)
                    #set_trace()
            
            ###try to match the description to an existing ###
            
            
    #If they say no, put it into the random list

    
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    print(message)
    bot.reply_to(message, u"Hello, welcome to this bot!")

@bot.message_handler(commands=['newlist'])
def list_message_handler(message):

    #create the new list, send a message telling them to make sure to write end when they're done
    #then pass it to a handler which takes the existing list name and the message and writes to it
    pass

@bot.message_handler(commands=['newlist'])
def existing_list_message_handler(message):

    #create the new list, send a message telling them to make sure to write end when they're done
    #then pass it to a handler which takes the existing list name and the message and writes to it
    pass

def follow_up_note_handler(message, message_list):
    #short bursts indicate a list
    message_text = message.text.replace("\\\l|\\\list","")
    end_commands = ["/l","end","done","quit","q","stop"]
    if any([message_text==x for x in end_commands]):
        pass
        #dump the list to a firebase db

    #lenthier statements


def process_telegram_messages(req):
    #bot.set_webhook(url=WEBHOOK)
    request_body_dict = req.get_json()
    update = telebot.types.Update.de_json(request_body_dict)
    bot.process_new_messages([update.message])