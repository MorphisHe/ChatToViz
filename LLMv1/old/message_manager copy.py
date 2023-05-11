import re
import pandas as pd
import datamart_profiler
import os

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

def processDataset(datapath):
    metadata = datamart_profiler.process_dataset(datapath)
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
    
    df = pd.read_csv(datapath)
    df = df.sample(5)
    sample = df.to_csv(index=False)

    context=formatContext(contextArr,sample)
    print(context)
    return context

class MessageManager:
    def __init__(self,datapath=None):
        if datapath:
            self.context = processDataset(datapath) #can input a csv file.
            self.csv = pd.read_csv(datapath) #using it to full store csv for frontend, was confused by backend stuff, may not be necessary code - nick
        else:
            self.context = ''
            self.csv = None
        self.message_history = [
                {"role": "system", "content": "You are a python data visualization code generator which uses matplotlib."},
                {"role": "user", "content": "Generate the python function for the requested visualization which takes df as input, show the plot and saves output plot to 'static/img/plot.png'. The input is a random sample of rows of a larger dataset.\
                 The context shows the datatypes per column. \n"+self.context+"\n"}]
        self.regex_patterns = [r"```python\n(.*?)```", r"```\n(.*?)```"]        

    def get_message_history(self):
        return self.message_history
    
    def get_last_response(self):
        return self.message_history[-1]["content"]
    
    def get_clean_code(self, message):
        '''
        code return by chatgpt is wrapper by ```python ```
        '''
        for pattern in self.regex_patterns:
            result = re.findall(pattern, message, re.DOTALL)
            if len(result):
                return result[0]
            
    def process_code(self, clean_code):
        code_lines = clean_code.split('\n')
        code_lines = [line for line in code_lines if not line.startswith('#')]
        function_header = [code_line for code_line in code_lines if "def" in code_line]
        if len(function_header):
            invoke_function = function_header[0].replace("def ", "").replace("df", "message_manager.csv").replace(":", "")
            code_lines.append(invoke_function)
        code = '\n'.join(code_lines)
        return code
    
    def append(self, message, role="user"):
        self.message_history.append(
            {
                "role": role,
                "content": message
            }
        )
    
    def reset_message_history(self):
        self.message_history = [
                {"role": "system", "content": "You are a python data visualization code generator which uses matplotlib."},
                {"role": "user", "content": "Generate the python function for the requested visualization which takes df as input, show the plot and saves output plot to 'static/img/plot.png'. The input is a random sample of rows of a larger dataset.\
                 The context shows the datatypes per column. \n"+self.context+"\n"}]
    