# app/ai_analysis.py
import os
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


def analyze_garden(plants, water, costs):
    model = ChatOpenAI(model="gpt-4",
                       temperature=0,
                       openai_api_key=OPENAI_API_KEY)

    template = """
    Analyze this garden data:
    Plants grown: {plants}
    Water used: {water} liters
    Garden costs: ${costs}

    Suggest eco-improvements and estimate CO2 savings.
    Assume: 1 kg vegetables = 2 kg CO2 saved.
    Estimate plant weight as plants * 0.5 kg.
    """
    prompt = PromptTemplate.from_template(template)
    chain = prompt | model
    result = chain.invoke({"plants": plants, "water": water, "costs": costs})

    return result.content
