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

'''

# Custom Prompts

def prompt_chains(prompt):
    title_template = PromptTemplate( 
        input_variables=["prompt"],
        template=From the dictionary given  which indicates the name of a csv files and for each and corresponding 
        names of columns, in simple_words that are clear explain what dataset we should use to answer the prompt : 
        {prompt}, where you are sure also specify the columns. Always provide answers dont advice what should be done. Always 
        use Units where needed and provide the response as raw text
        .  :
    )

    
    script_template = PromptTemplate( 
        input_variables=["simple_words"],
        template= Now from the above simple_words: , {simple_words} construct a prompt that will help answer my prompt.
        use the same tone as my prompt. Where thre are no specific objectives you need to decide what to do. If the question
        is too general, example generate summaries or something like that, decide what to focus on so as to answer the prompt
          
    )
    


#    llm = OpenAI( modelName = "gpt-4",temperature=0.9)
    llm = ChatOpenAI(model='gpt-4',temperature=0)

    title_chain = LLMChain(llm=llm, prompt=title_template, verbose=True)
#   script_chain = LLMChain(llm=llm, prompt=script_template, verbose=True)

    sequential_chain = SimpleSequentialChain(chains=[title_chain], verbose=True)
    response = sequential_chain.run(prompt)
    #print("pre response prompt: ", response)
    return response
'''
