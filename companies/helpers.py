from dotenv import load_dotenv
from langchain.agents import create_csv_agent
from langchain.llms import OpenAI
from langchain.memory import ConversationBufferMemory

load_dotenv()

'''
class CSVAgent:
    def __init__(self, openai_api_key, file_paths, verbose=True):
        self.openai_api_key = openai_api_key
        self.file_paths = file_paths
        self.verbose = verbose

    def create_agent(self, temperature, memory):
        openai_instance = OpenAI(openai_api_key=self.openai_api_key, temperature=temperature)
        return create_csv_agent(openai_instance, self.file_paths, memory, verbose=self.verbose)

    def run(self, user_question, temperature=0.5, memory=None):
        if memory is None:
            memory = ConversationBufferMemory()
        agent = self.create_agent(temperature, memory)
        return agent.run(user_question)
'''

class CSV_Agent:
    def __init__(self, openai_api_key, temperature=0, file_paths=None, verbose=False):
        self.openai = OpenAI(openai_api_key=openai_api_key, temperature=temperature)
        self.file_paths = file_paths
        self.verbose = verbose
        self.csv_memory = ConversationBufferMemory()

    def change_temperature(self, new_temperature):
        self.openai.temperature = new_temperature

    def change_csv_memory(self, new_csv_memory):
        self.csv_memory = new_csv_memory

    def create_csv_agent(self):
        return create_csv_agent(self.openai, self.file_paths, self.verbose, self.csv_memory)


