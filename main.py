from fastapi import FastAPI, Form
from typing import Annotated
import handler_func 
import uvicorn
import json

app = FastAPI()

@app.get("/")
def root():   
    return {"message": "Hello World"}

@app.post("/tata-webhook/webhook")
def webhook(intent : Annotated[str, Form()]):
    intent_dict = json.loads(intent)
    print(intent_dict)
    action = intent_dict.get("fulfillment").get("action")
    handler_functions = {
        "action_suggestions": handler_func.get_suggestions,
        "action_ask_query": handler_func.get_intent_response,
        
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
        return response_intent


if __name__ == "__main__":
    uvicorn.run("main:app", host='0.0.0.0')
