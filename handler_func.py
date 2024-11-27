from native_ai import get_answer, get_submodule
from df_data import get_basic_submodule
import json
import os
from typing import Dict
import random
import threading


chat_data_lock = threading.Lock()
chat_data : Dict = {}

path = os.getcwd()

last_message = None

def random_fallback():
    global last_message
    while True:
        message = random.choice(fallback_messages)
        if message != last_message:
            last_message = message
            return message
        
fallback_messages = [
    "Sorry, I couldn't find an answer to your query. Could you please try rephrasing your question?",
    "Apologies, I couldn’t find the information you’re looking for. Could you rephrase or provide more details?",
    "I'm sorry, I don't have an answer for that. Could you try asking in a different way?",
    "I couldn’t find a matching response. Can you rephrase your query for better results?",
    "Sorry, I couldn’t understand your question. Could you please try rephrasing it?",
    "I’m unable to provide an answer right now. Could you rephrase or clarify your question?"
]
    

def get_multiple_suggestions(intent):
    chatid = str(intent['chatId'])
    query_user = intent['fulfillment']['parameters']['question']  
    module = intent['fulfillment']['parameters']['module']
    
    sim_answer ,indices,best_match = get_answer(module_name=module, question=query_user)
    if not sim_answer:
        intent = {
        "id": 20000,
        "message": random_fallback(),
        "userInput": True,
        "trigger": 20001
            }
        return intent
    
    else:
        with threading.Lock():
            if chat_data.get(chatid):
                del chat_data[chatid]            
            chat_data[chatid] = {
            "query": query_user,
            "similar": sim_answer,
            "indices": indices,
            "module": module,
            "submodule": "",
            "issuecategory": ""
        }

    print(sim_answer)
    if best_match:
        best_match_index = str(indices[0])
        payload = [{
                        "label": sim_answer[best_match_index]["Issue"],
                        "value": best_match_index,
                        "trigger": 20002
                    }
                ]
    else:
        payload = []
        message = {"message": "I couldn't find an exact match for your query. However, I do have some relevant suggestions. Please select 'Suggestions' to view them, or you can choose a different module by clicking below.<br>You are in module:<b> {previousValue:21}"}

        intent.update(message)   
        payload.append({"label": "🔍➡️ See Suggestions", "value": "See Suggestions", "trigger": 20003})
        payload.append({"label": "Select Sub-Module", "value": "Select Sub-Module", "trigger": 20005})
    payload.append({"label": "Rephrase query", "value": "Rephrase query","trigger": 20000})
    payload.append({"label": "Change module", "value": "Change module", "trigger": 21})

    
    metadata = {"metadata": {"payload": payload, "templateId": 6 }}

    intent.update(metadata)
      
    return intent

def get_multiple_suggestions_more(intent):
    chatid = str(intent['chatId'])
    sim_answer = chat_data[chatid]["similar"]

    payload = [{
                    "label": sim_answer[question_index]["Issue"],
                    "value": str(question_index),
                    "trigger": 20004
                }
            for question_index in list(sim_answer.keys())]
    payload.append({"label": "Go Back", "value": "Go Back","image": "https://i.ibb.co/RSJ9szb/back.png", "trigger": 20000})
    payload .append({"label": "Rephrase query", "value": "Rephrase query", "trigger": 20000})
    payload.append({"label": "Select Sub-Module", "value": "Select Sub-Module", "trigger": 20005})
    
    metadata = {"metadata": {"payload": payload, "templateId": 6 }}

    intent.update(metadata)
      
    return intent

def get_intent_response_multiple(intent):
    chatid = str(intent['chatId'])
    query_user = intent['fulfillment']['parameters']['question']
    answer_list = chat_data[chatid]["similar"][query_user]["Resolution/Escalation"]
    message = {"message": "<b>Solution :</b></br>"+answer_list}
    intent.update(message)
    return intent



def get_level_2(intent):
    chatid = str(intent['chatId'])
    module = intent['fulfillment']['parameters']['module']
    cat_list = get_basic_submodule(module=module)


    payload = [
        {
        "label": i,
        "value": i,
        "trigger": 2000} for i in cat_list]

    payload.append({"label": "Go Back", "value": "Go Back","image": "https://i.ibb.co/RSJ9szb/back.png", "trigger": 20})
    payload.append({"label": "Main menu", "value": "Main menu", "trigger": 2})

    metadata = {"metadata": {
            "payload": payload,
            "templateId": 6
        }}

    intent.update(metadata)
    return intent
    
    
def get_level_3(intent):
    chatid = str(intent['chatId'])
    module = intent['fulfillment']['parameters']['module']
    submodule = intent['fulfillment']['parameters']['submodule']
    cat_list = get_basic_submodule(module=module, submodule=submodule)

    response_list = []
    for i in cat_list:
        response_list.append({"label": i, "value": i})
    
    metadata = {"metadata": {
          "message": "something went wrong. Submit details again",
          "payload": [
            {
              "data": {
                "title": "Issue Category",
                "options": response_list,
                "optional": False
              },
              "name": "level3",
              "type": "dropdown"
            },
            {
              "type": "submit",
              "label": "Next",
              "message": "Next",
              "trigger": 2001,
              "formAction": "/",
              "requestType": "POST"
            },
            {
              "type": "cancel",
              "label": "Cancel",
              "message": "Cancelled",
              "trigger": 200
            }
          ],
          "trigger": 6,
          "templateId": 13,
          "contentType": "300"
        }
    }
    intent.update(metadata)
    return intent

def get_level_4(intent):
    chatid = str(intent['chatId'])
    module = intent['fulfillment']['parameters']['module']
    submodule = intent['fulfillment']['parameters']['submodule']
    issuecategory = intent['fulfillment']['parameters']['issuecategory']['level3']
    result_dict_list = get_basic_submodule(module=module, submodule=submodule, issuecategory=issuecategory)

    with chat_data_lock:
        if chatid not in chat_data:
            chat_data[chatid] = {}
        chat_data[chatid]["result_dict_list"] = result_dict_list

    response_list = []
    for i,j in enumerate(result_dict_list):
        response_list.append({"label": j["Issue"], "value": str(i)})

    inputOption = { "inputOptions": {
            "type": "auto-suggest",
            "options": response_list,
            "multiple": False,
            "optional": False
        }}
    intent.update(inputOption)
    return intent

def get_level_response(intent):
    chatid = str(intent['chatId'])

    details = int(intent['fulfillment']['parameters']['details'][0]["value"])

    ## Get QnA data from the chat_data dictionary
    query_response = chat_data[chatid]["result_dict_list"][details]["Resolution/Escalation"]

    message = {"message": "<b>Solution :</b></br>"+ query_response}
    intent.update(message)
    return intent

def get_select_submodule(intent):
    chatid = str(intent['chatId'])
    query = intent['fulfillment']['parameters']['question']
    module = intent['fulfillment']['parameters']['module']

    sim_indices = chat_data[chatid]["indices"]
    chat_sim = chat_data[chatid]["similar"]

    cat_list = list(set([chat_sim[i]["Sub-Module"] for i in sim_indices]))


    payload = [
        {
        "label": i,
        "value": i,
        "trigger": 20006} for i in cat_list]

    payload.append({"label": "Rephrase query", "value": "Rephrase query", "trigger": 20000})
    payload.append({"label": "Go Back", "value": "Go Back","image": "https://i.ibb.co/RSJ9szb/back.png", "trigger": 20001})


    metadata = {"metadata": {
            "payload": payload,
            "templateId": 6
        }}

    intent.update(metadata)
    return intent

def get_submodule_suggestions(intent):
    chatid = str(intent['chatId'])
    query_user = intent['fulfillment']['parameters']['question']  
    module = intent['fulfillment']['parameters']['module']
    submodule = intent['fulfillment']['parameters'].get('submodule')
    chat_data[chatid]["submodule"] = submodule  

    sim_indices = chat_data[chatid]["indices"]
    chat_sim = chat_data[chatid]["similar"]

    sim_answer = [(i,chat_sim[i]['Issue']) for i in sim_indices if chat_sim[i]['Sub-Module'] == submodule]
    print(sim_answer)
    payload = [{
                    "label": question,
                    "value": str(question_index),
                    "trigger": 20007
                }
            for question_index,question in sim_answer[:5]]
    if len(sim_answer) > 5:    
        payload.append({"label": "🔍➡️ See More Suggestions", "value": "See More Suggestions", "trigger": 20010})
    else:
        payload.append({"label": "Rephrase query", "value": "Rephrase query", "trigger": 20000})
        payload.append({"label": "Select Issue Category", "value": "Select Issue Category", "trigger": 20012})
        payload.append({"label": "Go Back", "value": "Go Back","image": "https://i.ibb.co/RSJ9szb/back.png", "trigger": 20005})

    
    metadata = {"metadata": {"payload": payload, "templateId": 6 }}

    intent.update(metadata)
      
    return intent
def action_submodule_suggestions_more(intent):
    chatid = str(intent['chatId'])
    submodule = intent['fulfillment']['parameters'].get('submodule')
    sim_indices = chat_data[chatid]["indices"]
    chat_sim = chat_data[chatid]["similar"]

    sim_answer = [(i,chat_sim[i]['Issue']) for i in sim_indices if chat_sim[i]['Sub-Module'] == submodule]
    print(sim_answer)
    payload = [{
                    "label": question,
                    "value": str(question_index),
                    "trigger": 20011
                }
            for question_index,question in sim_answer[5:]]
    payload .append({"label": "Rephrase query", "value": "Rephrase query", "trigger": 20000})
    payload.append({"label": "Select Issue Category", "value": "Select Issue Category", "trigger": 20012})
    payload.append({"label": "Go Back", "value": "Go Back","image": "https://i.ibb.co/RSJ9szb/back.png", "trigger": 20001})

    
    metadata = {"metadata": {"payload": payload, "templateId": 6 }}

    intent.update(metadata)
      
    return intent

def action_get_issue_category(intent):
    chatid = str(intent['chatId'])
    query = intent['fulfillment']['parameters']['question']
    module = intent['fulfillment']['parameters']['module']
    submodule = intent['fulfillment']['parameters']['submodule']

    sim_indices = chat_data[chatid]["indices"]
    chat_sim = chat_data[chatid]["similar"]

    cat_list = list(set([chat_sim[i]['Issue Category'] for i in sim_indices if chat_sim[i]['Sub-Module'] == submodule]))

    options_list = []
    for i in cat_list:
        options_list.append({"label": i, "value": i})
    metadata = {"metadata": {
          "message": "something went wrong. Submit details again",
          "payload": [
            {
              "data": {
                "title": "Issue Category",
                "options": options_list,
                "optional": False
              },
              "name": "level3",
              "type": "dropdown"
            },
            {
              "type": "submit",
              "label": "Next",
              "message": "Next",
              "trigger": 20013,
              "formAction": "/",
              "requestType": "POST"
            },
            {
              "type": "cancel",
              "label": "Cancel",
              "message": "Cancelled",
              "trigger": 20009
            }
          ],
          "trigger": 6,
          "templateId": 13,
          "contentType": "300"
        }
    }
    intent.update(metadata)
    return intent

 
def action_rulebased_issue_suggestions(intent):
    chatid = str(intent['chatId'])
    query = intent['fulfillment']['parameters']['question']
    module = intent['fulfillment']['parameters']['module']
    submodule = intent['fulfillment']['parameters']['submodule']
    issue_category = intent['fulfillment']['parameters']['issue_category']['level3']

    sim_indices = chat_data[chatid]["indices"]
    chat_sim = chat_data[chatid]["similar"]

    sim_answer = [(i,chat_sim[i]['Issue']) for i in sim_indices if chat_sim[i]['Sub-Module'] == submodule and chat_sim[i]['Issue Category'] == issue_category]

    response_list = []
    for i,j in sim_answer:
        response_list.append({"label": j, "value": i})

    inputOption = { "inputOptions": {
            "type": "auto-suggest",
            "options": response_list,
            "multiple": False,
            "optional": False
        }}
    intent.update(inputOption)
    return intent


def get_ai_last_intent_response_multiple(intent):
    chatid = str(intent['chatId'])
    query_user = intent['fulfillment']['parameters']['question'][0]['value']
    answer_list = chat_data[chatid]["similar"][query_user]["Resolution/Escalation"]
    message = {"message": "<b>Solution :</b></br>"+answer_list}
    intent.update(message)
    return intent

