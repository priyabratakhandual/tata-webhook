from native_ai import get_answer, get_submodule
import json
import levels
import os
from typing import Dict


chat_data : Dict = {}

path = os.getcwd()
with open(f"{path}/cat.json", "r") as f:
    level_1_2_dict = json.load(f)
    

def get_multiple_suggestions(intent):
    chatid = str(intent['chatId'])
    query_user = intent['fulfillment']['parameters']['question']  
    module = intent['fulfillment']['parameters']['module']
    if chat_data.get(chatid):
        del chat_data[chatid]
    sim_answer = get_answer(module_name=module, question=query_user)
    if not sim_answer:
        intent = {
        "id": 20000,
        "message": "We couldn’t find an answer. Could you please rephrase your question?",
        "userInput": True,
        "trigger": 20001
            }
        return intent
    
    else:

        chat_data[chatid] = {
        "query": query_user,
        "similar": sim_answer,
        "module": module,
        "submodule": "",
        "issuecategory": ""
    }

    print(sim_answer)

    question_list = sim_answer.keys()

    payload = [{
                    "label": sim_answer[question_index]["Issue"],
                    "value": str(question_index),
                    "trigger": 20002
                }
            for question_index in question_list[:5]]
    if len(question_list) > 5:    
        payload.append({"label": "🔍➡️ See More Suggestions", "value": "See More Suggestions", "trigger": 20003})
    else:
        payload.append({"label": "Rephrase query", "value": "Rephrase query", "trigger": 20000})
        payload.append({"label": "Select Sub-Module", "value": "Select Sub-Module", "trigger": 20005})
    
    metadata = {"metadata": {"payload": payload, "templateId": 6 }}

    intent.update(metadata)
      
    return intent

def get_multiple_suggestions_more(intent):
    chatid = str(intent['chatId'])
    sim_answer = chat_data[chatid]["similar"]

    payload = [{
                    "label": sim_answer[question_index]["Issue"],
                    "value": str(question_index),
                    "trigger": 20002
                }
            for question_index in sim_answer.keys()[5:]]
    payload .append({"label": "Rephrase query", "value": "Rephrase query", "trigger": 20000})
    payload.append({"label": "Select Sub-Module", "value": "Select Sub-Module", "trigger": 20005})
    
    metadata = {"metadata": {"payload": payload, "templateId": 6 }}

    intent.update(metadata)
      
    return intent

def get_intent_response_multiple(intent):
    chatid = str(intent['chatId'])
    query_user = intent['fulfillment']['parameters']['question']
    query_index = query_user
    answer_list = chat_data[chatid]["similar"][query_index]["Resolution/Escalation"]
    message = {"message": "<b>Solution :</b></br>"+answer_list[query_index]}
    intent.update(message)
    return intent

def get_level_3(intent):
    chatid = str(intent['chatId'])
    details = intent['fulfillment']['parameters']['details']
    response_list = []
    options = level_1_2_dict[details]
    for i in options:
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
    details = intent['fulfillment']['parameters']['details']['level3']
    cat_list = [(i,levels.issue_dictionary.get(i)) for i in levels.issue_category.get(details)]
    response_list = []
    for i,j in cat_list:
        response_list.append({"label": j, "value": str(i)})

    inputOption = { "inputOptions": {
            "type": "auto-suggest",
            "options": response_list,
            "multiple": False,
            "optional": False
        }}
    intent.update(inputOption)
    return intent

def get_level_response(intent):
    details = intent['fulfillment']['parameters']['details'][0]["value"]
    message = {"message": "<b>Solution :</b></br>"+levels.res_dict.get(int(details))}
    intent.update(message)
    return intent

def get_select_submodule(intent):
    chatid = str(intent['chatId'])
    query = intent['fulfillment']['parameters']['question']
    module = intent['fulfillment']['parameters']['module']

    cat_list = get_submodule(module=module,submodule=None, issuecategory=None)


    payload = [
        {
        "label": i,
        "value": i,
        "trigger": 20006} for i in cat_list]

    payload.append({"label": "Rephrase query", "value": "Rephrase query", "trigger": 20000})
    payload.append({"label": "Select Sub-Module", "value": "Select Sub-Module", "trigger": 20005})

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
    sim_answer = get_answer(module_name=module, question=query_user,submodule=submodule)
    if not sim_answer:
        intent = {
        "id": 20007,
        "message": "We couldn’t find any suggestions. Could you please rephrase your question?",
        "userInput": True,
        "trigger": 20009
            }
        return intent
    
    else:

        chat_data[chatid]["similar"] = sim_answer
        chat_data[chatid]["module"] = module
        chat_data[chatid]["submodule"] = submodule


    print(sim_answer)

    question_list = sim_answer.keys()

    payload = [{
                    "label": sim_answer[question_index]["Issue"],
                    "value": str(question_index),
                    "trigger": 20011
                }
            for question_index in question_list[:5]]
    if len(question_list) > 5:    
        payload.append({"label": "🔍➡️ See More Suggestions", "value": "See More Suggestions", "trigger": 20010})
    else:
        payload.append({"label": "Rephrase query", "value": "Rephrase query", "trigger": 20007})
        payload.append({"label": "SelectIssue Category", "value": "Select Issue Category", "trigger": 20012})
    
    metadata = {"metadata": {"payload": payload, "templateId": 6 }}

    intent.update(metadata)
      
    return intent

def action_get_issue_category(intent):
    chatid = str(intent['chatId'])
    query = intent['fulfillment']['parameters']['question']
    module = intent['fulfillment']['parameters']['module']
    submodule = intent['fulfillment']['parameters']['submodule']
    cat_list = get_submodule(module=module,submodule=submodule)

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
    issue_category = intent['fulfillment']['parameters']['issue_category']
    sim_answer = get_answer(module_name=module, question=query,submodule=submodule,issue_category=issue_category)
    if not sim_answer:
        intent = {
        "id": 20000,
        "message": "We couldn’t find any suggestions. Could you please rephrase your question?",
        "userInput": True,
        "trigger": 20001
            }
        return intent
    
    else:
        chat_data[chatid]["similar"] = sim_answer
        chat_data[chatid]["issue_category"] = issue_category


        print(sim_answer)

        question_list = sim_answer.keys()

        payload = [{
                        "label": sim_answer[question_index]["Issue"],
                        "value": str(question_index),
                        "trigger": 20011
                    }
                for question_index in question_list[:5]]
        
        payload.append({"label": "Rephrase query", "value": "Rephrase query", "trigger": 20007})
        
        metadata = {"metadata": {"payload": payload, "templateId": 6 }}

        intent.update(metadata)
        
        return intent

