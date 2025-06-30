#!/usr/bin/env python
# coding: utf-8

# In[3]:


pip install PyPDF2


# In[1]:


get_ipython().system('pip install -U ibm-watsonx-ai')


# In[5]:


import getpass
import os
from ibm_watsonx_ai import Credentials
from ibm_watsonx_ai.foundation_models import ModelInference
from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams
from ibm_watsonx_ai.foundation_models.utils.enums import DecodingMethods
import re

# Securely input API key and set service URL/project ID (assumes environment variable PROJECT_ID or manual input)
api_key = getpass.getpass("Enter your IBM Cloud API key: ")
service_url = "https://us-south.ml.cloud.ibm.com"  # Adjust if needed
credentials = Credentials(url=service_url, api_key=api_key)

project_id = os.environ.get("PROJECT_ID")
if not project_id:
    project_id = input("Enter your watsonx.ai project ID: ")


# In[7]:


import getpass
import os
from ibm_watsonx_ai import Credentials
from ibm_watsonx_ai.foundation_models import ModelInference
from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams
from ibm_watsonx_ai.foundation_models.utils.enums import DecodingMethods
import re
from datetime import datetime, timedelta

# Securely input API key and set service URL/project ID
api_key = getpass.getpass("Enter your IBM Cloud API key: ")
service_url = "https://us-south.ml.cloud.ibm.com"  # Adjust if needed

credentials = Credentials(url=service_url, api_key=api_key)

project_id = os.environ.get("PROJECT_ID")
if not project_id:
    project_id = input("Enter your watsonx.ai project ID: ")


# In[11]:


from ibm_watsonx_ai import APIClient, Credentials

credentials = Credentials(api_key="h5DkLRw8iv1RkLSQa0tbHJx5ZS3JGcOBEkvV4KAlvOe7", url="https://au-syd.ml.cloud.ibm.com")
client = APIClient(credentials)

client.set.default_project("63b184fe-8534-45e6-b9e0-2d9ce55b6285")


# In[20]:


model_id = "ibm/granite-3-8b-instruct"  # ✅ Pick supported model

parameters = {
    GenParams.DECODING_METHOD: DecodingMethods.SAMPLE,
    GenParams.MAX_NEW_TOKENS: 512,
    GenParams.MIN_NEW_TOKENS: 1,
    GenParams.TEMPERATURE: 0.7,
    GenParams.TOP_P: 1,
    GenParams.TOP_K: 50,
    GenParams.REPETITION_PENALTY: 1.05,
    GenParams.STOP_SEQUENCES: ["\n\n"]
}

model = ModelInference(
    model_id=model_id,
    params=parameters,
    credentials=credentials,
    project_id=project_id
)


# In[21]:


def generate_text(prompt: str) -> str:
    response = model.generate_text(prompt)
    if isinstance(response, dict):
        if "generated_text" in response:
            return response["generated_text"].strip()
        elif "text" in response:
            return response["text"].strip()
        elif "choices" in response and len(response["choices"]) > 0:
            return response["choices"][0].get("text", "").strip()
        else:
            return str(response).strip()
    elif isinstance(response, str):
        return response.strip()
    else:
        return str(response).strip()

def summarize_transcript(transcript: str) -> str:
    prompt = (
        "You are an expert meeting summarizer.\n"
        "Summarize the following meeting transcript into concise bullet points capturing key decisions, topics discussed, outcomes, "
        "and include sentiment highlights:\n\n"
        f"{transcript}\n\nSummary:"
    )
    return generate_text(prompt)

def extract_action_items(summary: str) -> list[str]:
    prompt = (
        "You are an AI assistant specialized in identifying actionable tasks from meeting summaries.\n"
        "Extract all action items with responsible parties and deadlines if mentioned, format as a numbered list:\n\n"
        f"{summary}\n\nAction Items:"
    )
    raw_output = generate_text(prompt)
    
    items = re.findall(r'\d+\.\s*(.*)', raw_output)
    
    if not items:
        lines = [line.strip("-* \t") for line in raw_output.splitlines() if line.strip()]
        keywords = ['action', 'task', 'follow up', 'deadline', 'due', 'assign', 'responsible']
        items = [line for line in lines if any(k in line.lower() for k in keywords)]
    
    return items if items else ["No clear action items detected."]

def create_ics_event(action_item: str, start_datetime: datetime, duration_minutes=60) -> str:
    dtstamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    dtstart = start_datetime.strftime("%Y%m%dT%H%M%S")
    dtend = (start_datetime + timedelta(minutes=duration_minutes)).strftime("%Y%m%dT%H%M%S")
    
    uid = f"{dtstamp}-{hash(action_item)}@example.com"
    
    ics_event = (
        "BEGIN:VCALENDAR\n"
        "VERSION:2.0\n"
        "PRODID:-//AI Automation Hackathon//EN\n"
        "BEGIN:VEVENT\n"
        f"UID:{uid}\n"
        f"DTSTAMP:{dtstamp}\n"
        f"DTSTART:{dtstart}\n"
        f"DTEND:{dtend}\n"
        f"SUMMARY:{action_item}\n"
        "DESCRIPTION:Action item generated from meeting summary.\n"
        "END:VEVENT\n"
        "END:VCALENDAR"
    )
    
    return ics_event


# In[22]:


sample_meeting_transcript = """
Today’s meeting covered the Q3 product launch timeline and marketing strategy.
Marketing team will finalize campaign assets by next Friday.
John is assigned to coordinate with the design team on packaging options.
We agreed to schedule a review meeting on Monday at 10 AM.
Sarah will prepare the budget report by end of this week.
"""

print("=== Original Transcript ===\n")
print(sample_meeting_transcript)

print("\n=== Generated Summary ===\n")
summary_text = summarize_transcript(sample_meeting_transcript)
print(summary_text)

print("\n=== Extracted Action Items ===\n")
actions = extract_action_items(summary_text)
for idx, item in enumerate(actions, start=1):
    print(f"{idx}. {item}")

print("\n=== Exporting Action Items as Calendar Events ===")
now = datetime.now()
for idx, item in enumerate(actions):
    event_start_time = now.replace(hour=9, minute=0, second=0, microsecond=0) + timedelta(days=idx)
    ics_content = create_ics_event(item, event_start_time)
    
    filename = f"action_item_{idx+1}.ics"
    
    with open(filename, 'w') as f:
        f.write(ics_content)
    
    print(f"Created calendar event file: {filename}")


# In[ ]:




