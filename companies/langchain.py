import os
from apikey import apikey

os.environ['OPENAI_API_KEY'] = apikey

from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain, SimpleSequentialChain

prompt= "Incoming prompt"

#Prompt Templates
title_template = PromptTemplate( 
    input_variables= ["topic"],
    template = "Write me a youtube video title about {topic}."
)

script_template = PromptTemplate( 
    input_variables= ["title"],
    template = "Write me a youtube video script based on this  title: {title}."
)

llm = OpenAI(temparature = 0.9)

title_chain = LLMChain(llm=llm, prompt = title_template, verbose = True)
script_chain = LLMChain(llm=llm, prompt = script_template, verbose = True)


sequential_chain = SimpleSequentialChain(chains= [title_chain, script_chain], verbose = True)
response = sequential_chain.run(prompt)
