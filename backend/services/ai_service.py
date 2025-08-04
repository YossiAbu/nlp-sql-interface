from langchain_community.chat_models import ChatOpenAI
from langchain_experimental.sql import SQLDatabaseChain
from .db_service import get_db
import os
from dotenv import load_dotenv

load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

# Create the LLM and chain
llm = ChatOpenAI(
    temperature=0,
    model="gpt-3.5-turbo",
    openai_api_key=openai_api_key
)

db_chain = SQLDatabaseChain.from_llm(
    llm, get_db(), verbose=True, return_intermediate_steps=True
)

def get_db_chain():
    return db_chain
