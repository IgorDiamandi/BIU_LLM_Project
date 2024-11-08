#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os
print("Current working directory:", os.getcwd())


# In[2]:


import json5
from  tqdm import tqdm
import boto3
import yaml
from botocore.exceptions import NoCredentialsError, ClientError


# In[3]:


def load_config(config_file):
    # Load configuration from the YAML file
    with open(config_file, 'r') as file:
        config = yaml.safe_load(file)
    return config


# In[4]:


def upload_file_to_s3(file_name, config):
    # Extract parameters from the configuration
    region_name = config['aws']['region_name']
    upload_bucket_name = config['aws']['upload_bucket_name']
    upload_path = config['aws']['upload_path']
    aws_access_key_id = config['aws']['aws_access_key_id']
    aws_secret_access_key = config['aws']['aws_secret_access_key']
    
    # Create an S3 client with the specified credentials
    s3_client = boto3.client(
        's3',
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        region_name=region_name
    )

    try:
        # Upload the file
        response = s3_client.upload_file(file_name, upload_bucket_name, upload_path + file_name.split('/')[-1])
        print(f"File {file_name} uploaded to {upload_bucket_name}/{upload_path}")
    except FileNotFoundError:
        print("The file was not found")
    except NoCredentialsError:
        print("Credentials not available")
    except ClientError as e:
        print(f"Failed to upload {file_name} to {upload_bucket_name}/{upload_path}: {e}")


# In[5]:


# Load configuration
config_file = 'config/config.yaml'
config = load_config(config_file)


# In[6]:


# Example usage
file_name = 'lior_test.txt'  # Replace with your file path
upload_file_to_s3(file_name, config)

