import yaml

with open('config\config.yaml', 'r') as file:
    config = yaml.safe_load(file)

pinecone_api_key = config['pinecone']['pinecone_api_key']
openai_api_key = config['openai']['chat_gpt_key']
