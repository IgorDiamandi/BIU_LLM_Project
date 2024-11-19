import yaml
import os

# Get the absolute path of the directory where the current script resides
current_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(current_dir, 'config.yaml')

# Load the YAML configuration
with open(config_path, 'r') as file:
    config = yaml.safe_load(file)

pinecone_api_key = config['pinecone']['pinecone_api_key']
openai_api_key = config['openai']['chat_gpt_key']
