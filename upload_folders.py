#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import os
import json5
from tqdm import tqdm
import boto3
import yaml
from datetime import datetime
from botocore.exceptions import NoCredentialsError, ClientError


# In[ ]:


print("Current working directory:", os.getcwd())


# In[ ]:


def load_config(config_file):
    # Load configuration from the YAML file
    with open(config_file, 'r') as file:
        config = yaml.safe_load(file)
    return config


# In[ ]:


# Load configuration
config_file = 'config/config.yaml'
config = load_config(config_file)


# In[ ]:


def write_log(log_file_name, log_text, config):
    # Extract parameters from the configuration
    region_name = config['aws']['region_name']
    log_bucket_name = config['aws']['log_bucket_name']
    log_path = config['aws']['log_path']
    aws_access_key_id = config['aws']['aws_access_key_id']
    aws_secret_access_key = config['aws']['aws_secret_access_key']

    # Create an S3 client with the specified credentials
    s3_client = boto3.client(
        's3',
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        region_name=region_name
    )

    # Construct the S3 key for the log file
    s3_key = f"{log_path}/{log_file_name}"

    # Get the current system time
    current_time = datetime.now().strftime("%Y/%m/%d %H:%M:%S")

    # Create a CSV row with the current time and log text
    log_row = [current_time, log_text]
    
    # Try to download the existing log file, if it exists
    try:
        # Read the existing log file from S3
        response = s3_client.get_object(Bucket=log_bucket_name, Key=s3_key)
        existing_log = response['Body'].read().decode('utf-8')
        
        # Append the new log row to the existing log content
        log_content = existing_log + "\n" + ",".join(log_row)

    except s3_client.exceptions.NoSuchKey:
        # If the file does not exist, create a new log content with headers
        log_content = "Start Log\n" + ",".join(log_row)

    # Write the updated log content back to S3
    try:
        # Convert log content to bytes and upload it
        s3_client.put_object(Bucket=log_bucket_name, Key=s3_key, Body=log_content.encode('utf-8'))
        #print(f"Log entry added to {log_bucket_name}/{s3_key}")
    except (NoCredentialsError, ClientError) as e:
        print(f"Failed to write log entry to {log_bucket_name}/{s3_key}: {e}") 


# In[ ]:


def upload_folders_to_s3(folder_name, config):
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

    # Progress bar class for tracking each file
    class ProgressPercentage(object):
        def __init__(self, filename):
            self._filename = filename
            self._seen_so_far = 0
            self._total = os.path.getsize(filename)
            # Initialize the tqdm progress bar for the current file
            print(f"Uploading {filename}:")
            self._pbar = tqdm(total=self._total, unit='B', unit_scale=True)

        def __call__(self, bytes_amount):
            # Update progress
            self._seen_so_far += bytes_amount
            self._pbar.update(bytes_amount)
            # Close the progress bar when done
            if self._seen_so_far >= self._total:
                self._pbar.close()

    # Traverse through all files and subfolders in the given folder
    for root, dirs, files in os.walk(folder_name):
        for file in files:
            # Full path of the file
            local_file_path = os.path.join(root, file)
            
            # Construct the S3 key by replacing the base folder path with the upload_path in S3
            relative_path = os.path.relpath(local_file_path, folder_name)
            s3_key = os.path.join(upload_path, relative_path).replace("\\", "/")
            try:
                # Upload the file with progress callback
                s3_client.upload_file(
                    local_file_path,
                    upload_bucket_name,
                    s3_key,
                    Callback=ProgressPercentage(local_file_path)
                )
                # Log the successful upload
                log_text = f"{upload_bucket_name},{s3_key},{file},Success"
                write_log("upload.csv", log_text, config)
            except FileNotFoundError:
                print(f"The file {local_file_path} was not found")
                # Log the failure
                log_text = f"{upload_bucket_name},{s3_key},{file},FileNotFoundError"
                write_log("upload.csv", log_text, config)
            except NoCredentialsError:
                print("Credentials not available")
                # Log the failure
                log_text = f"{upload_bucket_name},{s3_key},{file},NoCredentialsError"
                write_log("upload.csv", log_text, config)
            except ClientError as e:
                print(f"Failed to upload {local_file_path} to {upload_bucket_name}/{s3_key}: {e}")
                # Log the failure with error message
                log_text = f"{upload_bucket_name},{s3_key},{file},ClientError: {e}"
                write_log("upload.csv", log_text, config)
            print()


# In[ ]:


# Load configuration
config_file = 'config/config.yaml'
config = load_config(config_file)


# In[ ]:


# call the folder upload function
folder_name = 'L:/My Drive/# Computers/קורסים וחומרי לימוד/! BIU/02. Junior Data Science/20. RAG Project/03_Source_Files' 
upload_folders_to_s3(folder_name, config)

