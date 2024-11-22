from native_ai import get_answer,get_answers_list
import json
import levels
import os


path = os.getcwd()



with open(f"{path}/cat.json", "r") as f:
    level_1_2_dict = json.load(f)
    
answer = ""
answer_list = []
question_list = []


def get_suggestions(intent):
    chatid = str(intent['chatId'])
    query_user = intent['fulfillment']['parameters']['question']
    global answer  
    question,answer = get_answers_list(query_user)
    if not answer:
        intent = {
        "id": 20000,
        "message": "Unable to find answer, can you please rephrase your question?.",
        "userInput": True,
        "trigger": 20001
            }
        return intent

    print(answer)

    payload = [{
                    "label": question,
                    "value": question,
                    "trigger": 20002
                }
            ]
    
    metadata = {"metadata": {"payload": payload, "templateId": 6 }}

    intent.update(metadata)
      
    return intent

def get_intent_response(intent):
    print(intent)
    message = {"message": answer}
    print(message)
    intent.update(message)
    print(intent)
    return intent


def get_multiple_suggestions(intent):
    chatid = str(intent['chatId'])
    query_user = intent['fulfillment']['parameters']['question']
    # clear list
    global answer_list, question_list
    if answer_list:
        answer_list.clear()
    if question_list:
        question_list.clear()  

    answer_list,question_list = get_answers_list(query_user)
    if not answer_list:
        intent = {
        "id": 20000,
        "message": "We couldn’t find an answer. Could you please rephrase your question?",
        "userInput": True,
        "trigger": 20001
            }
        return intent

    print(answer)

    payload = [{
                    "label": i,
                    "value": str(j),
                    "trigger": 20002
                }
            for j,i in enumerate(question_list[:5])]
    payload .append({"label": "🔍➡️ See More Suggestions", "value": "See More Suggestions", "trigger": 20003})
    
    metadata = {"metadata": {"payload": payload, "templateId": 6 }}

    intent.update(metadata)
      
    return intent

def get_multiple_suggestions_more(intent):
    payload = [{
                    "label": i,
                    "value": str(j),
                    "trigger": 20004
                }
            for j,i in enumerate(question_list[5:],start=5)]
    payload .append({"label": "Rephrase query", "value": "Rephrase query", "trigger": 20000})
    
    metadata = {"metadata": {"payload": payload, "templateId": 6 }}

    intent.update(metadata)
      
    return intent

def get_intent_response_multiple(intent):
    chatid = str(intent['chatId'])
    query_user = intent['fulfillment']['parameters']['question']
    query_index = int(query_user)
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

