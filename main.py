from fastapi import FastAPI, Form
from typing import Annotated
import handler_func 
import uvicorn
import json

app = FastAPI()

@app.get("/tata-webhook/ping")
def root():   
    return {"message": "Pong"}

@app.post("/tata-webhook/webhook")
def webhook(intent : Annotated[str, Form()]):
    intent_dict = json.loads(intent)
    print(intent_dict)
    action = intent_dict.get("fulfillment").get("action")
    handler_functions = {
        "action_suggestions": handler_func.get_multiple_suggestions,
        "action_ask_query": handler_func.get_intent_response_multiple,
        "action-level-3": handler_func.get_level_3,
        "action-level-4" : handler_func.get_level_4,
        "action-level-response": handler_func.get_level_response,
        "action_suggestions_more": handler_func.get_multiple_suggestions_more
        
    }

    handler = handler_functions.get(action, None)
    if handler:
        # try:
        #     response_intent = json.dumps(handler(intent_dict))
        # except Exception as e:
        #     logging.error(f"Error processing webhook: {e}")
        #     response_intent = fallback_
        # return response_intent

        response_intent = handler(intent_dict)
        print("++++++++++++++Response++++++++")
        print(response_intent)
        return response_intent


if __name__ == "__main__":
    uvicorn.run("main:app", host='0.0.0.0')
