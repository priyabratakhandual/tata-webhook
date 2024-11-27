from fastapi import FastAPI, Form
from typing import Annotated
import handler_func 
import uvicorn
import json
import logging

app = FastAPI()

logging.basicConfig(level=logging.INFO,filename='logs.log',filemode='w',format='%(asctime)s - %(levelname)s - %(message)s')

fallback_ = {
        "id": 11,
        "message": "Your chat session has been refreshed. Please click on 'Refresh' to restart the conversation.",
        "userInput": False,
        "metadata": {
            "payload": [
                {
                    "label": "Refresh",
                    "value": "Refresh",
                    "trigger": 20
                }
            ],
            "templateId": 6
        }
        }

@app.get("/tata-webhook/ping")
def root():   
    return {"message": "Pong"}

@app.post("/tata-webhook/webhook")
def webhook(intent : Annotated[str, Form()]):
    intent_dict = json.loads(intent)
    logging.info(f"Received intent: {intent_dict}")
    print(intent_dict)
    action = intent_dict.get("fulfillment").get("action")
    handler_functions = {
        "action-level-2": handler_func.get_level_2,
        "action-level-3": handler_func.get_level_3,
        "action-level-4" : handler_func.get_level_4,
        "action_suggestions": handler_func.get_multiple_suggestions,
        "action_ask_query": handler_func.get_intent_response_multiple,
        "action-level-response": handler_func.get_level_response,
        "action_suggestions_more": handler_func.get_multiple_suggestions_more,
        "action_select_submodule" : handler_func.get_select_submodule,
        "action_submodule_suggestions": handler_func.get_submodule_suggestions,
        "action_submodule_suggestions_more": handler_func.action_submodule_suggestions_more,
        "action-get-issue-category": handler_func.action_get_issue_category,
        "action_rulebased_issue_suggestions": handler_func.action_rulebased_issue_suggestions,
        "action_get_intent_response_multiple": handler_func.get_ai_last_intent_response_multiple
        
    }

    handler = handler_functions.get(action, None)
    if handler:
        try:
            response_intent = json.dumps(handler(intent_dict))
        except Exception as e:
            logging.error(f"Error processing webhook: {e}")
            response_intent = fallback_
        response_intent = handler(intent_dict)
        print("++++++++++++++Response++++++++")
        print(response_intent)
        logging.info("-------------------------------------------")
        logging.info(f"Response intent: {response_intent}")
        return response_intent


if __name__ == "__main__":
    uvicorn.run("main:app", host='0.0.0.0')
