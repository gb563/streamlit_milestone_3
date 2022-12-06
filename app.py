
import streamlit as st
import pandas as pd
import numpy as np
#import boto3
import requests
import json
from collections import Counter
import regex as re
import nltk
from nltk import sent_tokenize
nltk.download('stopwords')
nltk.download('punkt')
from nltk.corpus import stopwords
#import lime
#from lime import lime_text
#from lime.lime_text import LimeTextExplainer
#import fasttext

gate_endpt = 'https://i64nm5r412.execute-api.us-east-1.amazonaws.com/gb-milestone-gateway-2/gb-milestone-gateway-resource-1'



def process_input(sent):
    review_sent0 = sent_tokenize(sent)
    
    #remove numbers and punctuation
    review_sent1=[]
    for line in review_sent0:
      review_sent1.append(re.sub(r'[^\w\s]',' ',line)) #remove punctuation
    print(review_sent1)
    
    review_sent=[]
    for line in review_sent1:
      review_sent.append(re.sub(r'[^A-Za-z]',' ',line)) #remove numbers
    print(review_sent)
    
    #do some pre-processing
    #stopwords
    stp = stopwords.words('english')
    stp.append('throughout')
    stop_words=stp.copy()
    
    #remove the stop words
    def remove_stop(line):
      words = nltk.word_tokenize(line)
      holder = []
      index1=0
      for word in words:
          if word not in stop_words:
              holder.append(word.lower())
      return ' '.join(holder)
    
    review_sent3=[remove_stop(x) for x in review_sent]
    review_sent4=[re.sub(r'[^\w\s]',' ',line) for line in review_sent3]
    return (review_sent0,review_sent4)



def exp_list():
	st.session_state['exp_list'] = ['1','2']




milestone_map = {'PC1':'Pre-Anesthetic Evaluation','PC2':'Peri-Operative Care and Management','PC3': 'Application and Interpretation of Monitors','PC4':'Intra-Operative Care','PC5':'Airway Management','PC7':'Situational Awareness and Crisis Management','PC8':'Post-Operative Care','PC9':'Critical Care','PC10': 'Regional (Peripheral and Neuraxial) Anesthesia','MK1':'Foundational Knowledge','MK2':'Clinical Reasoning','ICS':'Interpersonal and Communication Skills','P':'Professionalism','PBLI':'Practice-Based Learning and Improvement','SBP':'Systems-Based Practice','D':'Demographic/Descriptive','N':'Not related to competencies'}



st.title("Natural Language Processing with Anesthesiology Trainee Evaluations")

st.header("Welcome!")

st.caption("This tool is designed to organize narrative feedback on anesthesiology residents in the United States. It is not designed to make decisions on progress through training or achievement of specific competencies. The algorithm built into this tool was developed at Naval Medical Center Portsmouth. It learned from more than 10,000 free-text sentences across three different anesthesiology training programs. This web application is a testing environment to gain insight into how the natural language processing algorithm makes predictions. Since this is a testing environment, compute time takes a few seconds. When built into a dedicated system, this algorithm was shown to read and process several hundred narrative comments in approximately 1 minute.")

st.caption("This work was published in Academic Medicine in December 2022. [You can read the paper here.](https://pubmed.ncbi.nlm.nih.gov/)")


#st.sidebar.subheader("Learn more")
add_selectbox = st.sidebar.selectbox(
    "Learn More",
    options = ["Make a selection","Read the paper", "Contact research team"],key='first_sb', on_change=exp_list
    )

if add_selectbox =="Read the paper":
	st.sidebar.write("[Pubmed link](https://pubmed.ncbi.nlm.nih.gov/)")

if add_selectbox =="Contact research team":
	st.sidebar.write("gjbooth2@gmail.com")

st.header("Test out the model yourself")

text_input = st.text_area('Type an example narrative evaluation:')


if text_input:
    j=1
    review_sents_full = process_input(text_input)
    review_sents_orig = review_sents_full[0]
    review_sents = review_sents_full[1]
    st.header('Predictions:')
    for rev in review_sents:
        #st.write(rev)
        sent = json.dumps({'sent':rev})
        response = requests.post(gate_endpt, data = sent)
        #st.write(review_sents)
        #st.write(vars(response))
        output = json.loads(response.text[1:-1])
        comps = [i.strip('__label__') for i in output['label']]
        probs = [100*np.round(i,3) for i in output['prob']]
        st.subheader(review_sents_orig[j-1])
        for i in range(0,3):
          st.write(comps[i],'('+milestone_map[comps[i]]+')',str(probs[i])+'%')
        #st.write(output['prob'])
        #st.write(response.text)
        j+=1
    if len(review_sents)>1:
    	sent = json.dumps({'sent':' '.join([r for r in review_sents_orig])})
    	#st.write('combined')
    	#st.write(sent)
    	response = requests.post(gate_endpt, data = sent)
    	output = json.loads(response.text[1:-1])
    	comps = [i.strip('__label__') for i in output['label']]
    	probs = [100*np.round(i,3) for i in output['prob']]
    	st.header('Predictions when considering all sentences together:')
    	st.subheader(text_input)
    	for i in range(0,3):
    	  st.write(comps[i],'('+milestone_map[comps[i]]+')',str(probs[i])+'%')

st.text('')
st.text('')
st.caption("The views expressed herein are those of the author(s) and do not necessarily reflect the official policy or position of the Department of the Navy, Department of Defense, or the United States Government. Where applicable, study protocols have been approved by the respective Institutional Review Boards of the military treatment facilities where the research was conducted in compliance with all Federal regulations governing the protection of human subjects.")

st.caption("Some authors may be military service members who have contributed as part of their official duties. Title 17, USC, §105 provides that 'Copyright protection under this title is not available for any work of the U.S. Government.' Title 17, USC, §101 defines a U.S. Government work as a work prepared by a military service member or employee of the U.S. Government as part of that person's official duties.")




