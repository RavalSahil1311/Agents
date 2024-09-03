from utils.workflow_manager import graph
from langchain_core.messages import BaseMessage, HumanMessage

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

app = FastAPI()

class UserInput(BaseModel):
    messages: List[str]

@app.post("/interact/")
async def interact(user_input: UserInput):
    config = {"configurable": {"thread_id": "1"}}
    responses = []
    
    for s in graph.stream({"messages": [HumanMessage(content=msg) for msg in user_input.messages]}, config):
        if 'supervisor' in s:
            # Supervisor detected, skipping...
            continue
        
        res = None  # Initialize `res` to handle cases where it might not be set
        
        # Try to access content and print it
        for key, value in s.items():
            if isinstance(value, dict) and 'messages' in value:
                for message in value['messages']:
                    res = message.content
                    print(res)  # Debug print

        if res:  # Only append if `res` was set
            responses.append(res)
    
    if not responses:
        raise HTTPException(status_code=400, detail="No response generated.")
    
    return {"response": responses}

@app.get("/")
def read_root():
    return {"message": "Welcome to the LangChain API!"}




# config = {"configurable": {"thread_id": "1"}}

# while True:
#     user_input = input("User: ")
#     if user_input.lower() in ["quit", "exit", "q"]:
#         print("Goodbye!")
#         break
#     for s in graph.stream(
#         {"messages": [HumanMessage(content=user_input)]},
#         config,
#     ):
#         # print("Raw Response: ", s)  # Print the raw response for debugging
        
#         # Check if 'supervisor' is in the response
#         if 'supervisor' in s:
#             # print("Supervisor detected, skipping...")
#             continue
        
#         # Try to access content and print it
#         for key, value in s.items():
#             if isinstance(value, dict) and 'messages' in value:
#                 # print(f"value: {value}")
#                 for message in value['messages']:
#                     found_content = False

#                     # print("Input: ", user_input)
#                     print(f"msg: {message.content}")
#                     # if 'content' in message:
#                     #     print("AI: ", message)
        
#         print("----")
