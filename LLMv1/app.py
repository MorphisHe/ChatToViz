# app.py
from message_manager import MessageManager, processDataset
from werkzeug.utils import secure_filename

# app.py
from flask import Flask, render_template, request
from io import BytesIO
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import openai
import base64
import os

app = Flask(__name__)
os.makedirs("temp_uploads", exist_ok=True)
message_manager = MessageManager()

# Set up OpenAI API key
openai.api_key = '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'
# Define route for the homepage
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/reset', methods=['POST'])
def reset():
    global message_manager
    message_manager.reset_message_history()
    # Delete the plot image if it exists
    if os.path.exists('static/img/plot.png'):
        os.remove('static/img/plot.png')
    return render_template('index.html')

@app.route('/upload_csv', methods=['POST'])
def upload_csv():
    global message_manager
    user_csv_file = request.files.get("csv_file")
    if user_csv_file and user_csv_file.filename.endswith(".csv"):
        filename = secure_filename(user_csv_file.filename)
        file_path = os.path.join("temp_uploads", filename)
        print("File Path: " + file_path)
        user_csv_file.save(file_path)
        message_manager.context = processDataset(file_path)
        message_manager.csv = pd.read_csv(file_path)
        csv_dict = message_manager.csv.to_dict(orient="records")
        table_html = render_template('table.html', csv_data=csv_dict)
        return table_html
    else:
        return "Invalid file format"

# Define route for handling form submission
@app.route('/submit', methods=['POST'])
def submit():
    # Get the prompt and API key from the form
    prompt = request.form['prompt']
    api_key = request.form['api_key']
    openai.api_key = api_key

    # add new message to message_history
    message_manager.append(prompt, role="user")

    # Generate code using OpenAI
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=message_manager.get_message_history(),
        temperature=0,
    )
    response_message = response.choices[0].message.content
    code = message_manager.get_clean_code(response_message)
    print(response_message)
    print("----")
    print(code)
    
    # add response to message_history
    message_manager.append(response_message, role="assistant")

    # Create matplotlib visualization using generated code
    matplotlib.use('Agg')
    fig, ax = plt.subplots()

    # Remove comments from code
    code_lines = code.split('\n')
    code_lines = [line for line in code_lines if not line.startswith('#')]
    code = '\n'.join(code_lines)

    # Execute modified code
    exec(code)

    plt.savefig('static/img/plot.png')
    plt.close()

    # Encode image as base64 for embedding in HTML
    with open('static/img/plot.png', 'rb') as f:
        plot_data = f.read()
    plot_b64 = base64.b64encode(plot_data).decode('utf-8')

    #for table building
    csv_dict = message_manager.csv.to_dict(orient="records")

    # Return rendered template with embedded plot
    return render_template('index.html', plot_data=plot_b64, csv_data=csv_dict, code_data=code)



"""
from flask import Flask, render_template, request
from io import BytesIO
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import openai
import base64

app = Flask(__name__)

# Set up OpenAI API key
openai.api_key = 'YOUR_API_KEY_HERE'

# Define route for the homepage
@app.route('/')
def index():
    return render_template('index.html')

# Define route for handling form submission
@app.route('/submit', methods=['POST'])
def submit():
    # Get the prompt and API key from the form
    prompt = request.form['prompt']
    api_key = request.form['api_key']
    openai.api_key = api_key
    chat_history = {
    "messages": [
        {
            "role": "user",
            "content": prompt
        }
    ]
}
    # Generate code using OpenAI
    print(chat_history)
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        prompt=chat_history,
        max_tokens=1024,
        temperature=0.5,
    )
    code = response.choices[0].text

    # Create matplotlib visualization using generated code
    matplotlib.use('Agg')
    fig, ax = plt.subplots()

    # Remove comments from code
    code_lines = code.split('\n')
    code_lines = [line for line in code_lines if not line.startswith('#')]
    code = '\n'.join(code_lines)

    print(code[2:])

    # Execute modified code
    exec(code[2:])

    plt.savefig('static/img/plot.png')
    plt.close()

    # Encode image as base64 for embedding in HTML
    with open('static/img/plot.png', 'rb') as f:
        plot_data = f.read()
    plot_b64 = base64.b64encode(plot_data).decode('utf-8')

    # Return rendered template with embedded plot
    return render_template('index.html', plot_data=plot_b64)

"""
"""
from flask import Flask, request, render_template
import openai
import matplotlib.pyplot as plt
import base64
from io import BytesIO

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/generate-visualization", methods=["POST"])
def generate_visualization():
    prompt = request.form["prompt"]
    openai.api_key = "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"
    response = openai.ChatCompletion.create(
        engine="gpt-3.5-turbo",
        prompt=prompt,
        temperature=0.5,
        max_tokens=512,
        n = 1,
        stop = "\n\n"
    )
    code = response.choices[0].text.strip()
    exec(code)
    figfile = BytesIO()
    plt.savefig(figfile, format="png")
    figdata_png = base64.b64encode(figfile.getvalue()).decode("utf8")
    return f'<img src="data:image/png;base64,{figdata_png}"/>'

if __name__ == "__main__":
    app.run(debug=True)

import openai
from flask import Flask, request, render_template

app = Flask(__name__)
openai.api_key = "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"

def generate_code(prompt):
    completions = openai.Completion.create(
        engine="text-davinci-002",
        prompt=prompt,
        max_tokens=2048,
        n=1,
        stop=None,
        temperature=0.5,
        presence_penalty=0,
        frequency_penalty=0,
    )
    print(completions)
    message = completions.choices[0].text.strip()
    return message

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate_code_api():
    prompt = request.form['prompt']
    code = generate_code(prompt)
    return code


import openai
from flask import Flask, request, render_template

app = Flask(__name__)
openai.api_key = "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"

def generate_code(prompt):
    completions = openai.Completion.create(
        engine="text-davinci-002",
        prompt=prompt,
        max_tokens=2048,
        n=1,
        stop=None,
        temperature=0.5,
        presence_penalty=0,
        frequency_penalty=0,
    )
    message = completions.choices[0].text.strip()
    return message

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate_code_api():
    prompt = request.form['prompt']
    code = generate_code(prompt)
    return code

@app.route('/graph')
def generate_graph():
    code = '''
    import matplotlib.pyplot as plt
    import numpy as np

    x = np.linspace(0, 2 * np.pi, 100)
    y = np.sin(x)

    plt.plot(x, y)
    plt.show()
    '''
    return "<pre>" + code + "</pre>"
"""