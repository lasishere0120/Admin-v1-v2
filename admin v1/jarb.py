from flask import Flask, render_template
import yaml

app = Flask(__name__)

def read_intents_from_domain():
    with open('../domain.yml', 'r') as file:
        domain_data = yaml.safe_load(file)
        intents = domain_data.get('intents', [])
    return intents
def read_responses_from_domain():
    with open('../domain.yml', 'r') as file:
        domain_data = yaml.safe_load(file)
        responses = domain_data.get('responses', {})
    return responses
@app.route('/')
def display_intents():
    intents = read_intents_from_domain()
    response=read_responses_from_domain()
    return render_template('jarb.html', intents=intents,responses=response)

if __name__ == '__main__':
    app.run(debug=True)
