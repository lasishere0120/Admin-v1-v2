from flask import Flask, render_template, request
import yaml

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index2.html')

@app.route('/add_intent', methods=['POST'])
def add_intent():
    new_intent = request.form['intent']
    examples = request.form['examples'].strip().split('\n')
    formatted_examples = ["    - " + example.strip() for example in examples]

    with open('../nlu.yml', 'a') as f:
        f.write(f"\n- intent: {new_intent}\n")
        f.write("  examples: |\n")
        f.write('\n'.join(formatted_examples) + '\n')

    return "Intent added successfully!"

if __name__ == '__main__':
    app.run(debug=True)
