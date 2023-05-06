from bs4 import BeautifulSoup
import pandas as pd
import openai
import re
import matplotlib.pyplot as plt
import datamart_profiler
import os

openai.api_key = os.getenv("OPENAI_API_KEY")
def get_clean_code(message):
        '''
        code return by chatgpt is wrapper by ```python ```
        '''
        return re.findall(r"```python\n(.*?)```", message, re.DOTALL)[0] ##need to fix 

def formatContext(contextArr,sample):
    result=""
    for d in contextArr:
        result+="Column "+d['name']+" is a "+d['structural_type']+". "
        if('num_distinct_values' in d.keys()):
            result+="There are "+str(d['num_distinct_values'])+" distinct values. "
        if('coverage' in d.keys()):
            result+="The range of values are from "+str(d['coverage'][0])+" to "+str(d['coverage'][1])+". "
        result+="The semantic types are: "
        for s in d['semantic_types']:
            result+=s+", "
        result=result[:-2]
        result+=". "
        result+="\n"
    final = "Input: \n" + sample + "\n\n" + "Context: \n" + result
    return final

def processDataset(df):
    metadata = datamart_profiler.process_dataset(df)
    contextArr=[]
    for i in range(len(metadata['columns'])):
        metDict = metadata['columns'][i]
        cDict={'name':metDict['name']
               ,'structural_type':metDict['structural_type'],
               'semantic_types':metDict['semantic_types']}
        if('num_distinct_values' in metDict.keys()):
            cDict['num_distinct_values'] = metDict['num_distinct_values']
        if('coverage' in metDict.keys()):
            low=0
            high=0
            for i in range(len(metDict['coverage'])):
                if(metDict['coverage'][i]['range']['gte']<low):
                    low=metDict['coverage'][i]['range']['gte']
                if(metDict['coverage'][i]['range']['lte']>high):
                    high=metDict['coverage'][i]['range']['lte']
            cDict['coverage'] = [low,high]
        contextArr.append(cDict)
    
    sample = df.to_csv(index=False)

    context=formatContext(contextArr,sample)
    return context

def extractPromptsData(htmlPath):
    with open(htmlPath, 'r') as file:
        html = file.read()

    soup = BeautifulSoup(html, 'html.parser')

    dfs = pd.read_html(htmlPath)
    df = dfs[1]

    return [li.string for li in soup.find_all('li')],df

def generateVis(prompt,context):
     codeVis = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
                {"role": "system", "content": "You are a python data visualization code generator."},
                {"role": "user", "content": "Generate the python code for the requested visualization. The input is the dataset.\
                 The context shows the datatypes per column. Include the dataframe definition within the code. \n"+context+"\n"},
                {"role": "user", "content": prompt}])
     
     code = codeVis.choices[0]['message']['content'] # type: ignore
     try:
         return get_clean_code(code) # type: ignore
     except:
         return code
     
def main(htmlPath):
    codeArr = []
    global prompts
    prompts,df = extractPromptsData(htmlPath)

    context = processDataset(df)

    for prompt in prompts:
        code = generateVis(prompt,context)
        codeArr.append(code)
    return codeArr


if __name__=="__main__":
    p = main("nvBench/nvBench_VegaLite/VIS_2.html")
    for i in range(len(p)):
        try:
            exec(p[i])
            print("success running code: "+prompts[i])
        except:
            print("error running code: "+prompts[i])
            print(p[i])
            print("----")
            pass