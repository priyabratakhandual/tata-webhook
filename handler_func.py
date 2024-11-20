from native_ai import get_answer
answer = ""


def get_suggestions(intent):
    chatid = str(intent['chatId'])
    query_user = intent['fulfillment']['parameters']['question']
    global answer  
    question,answer = get_answer(query_user)

    payload = [{
                    "label": question,
                    "value": question,
                    "trigger": 204
                }
            ]
    
    metadata = {"metadata": {"payload": payload, "templateId": 6 }}

    intent.update(metadata)
      
    return intent

def get_intent_response(intent):
    message = {"message": answer}
    intent.update(message)
    return intent
