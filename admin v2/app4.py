from flask import Flask, render_template, request
import yaml

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index4.html')


@app.route('/add_intent_response', methods=['POST'])
def add_intent_response():
    intent_name = request.form['intent_name']
    response_text = request.form['response_text']

    with open('../domain.yml', 'r') as f:
        lines = f.readlines()

    # Extract the version
    version_line = lines[0].strip()

    # Find the index of the 'intents' line
    intents_index = lines.index('intents:\n')

    # Extract existing intents and responses
    existing_data = yaml.safe_load(''.join(lines[intents_index:]))
    intents = existing_data.get('intents', [])
    responses = existing_data.get('responses', {})

    # Check if the intent already exists, if not, add it
    if intent_name not in intents:
        intents.append(intent_name)

    # Construct response key
    response_key = f"utter_{intent_name}"

    # Check if the response already exists, if not, add it
    if response_key not in responses:
        responses[response_key] = []

    responses[response_key].append({'text': response_text})

    new_data = {'intents': intents, 'responses': responses}

    # Find the index of the 'session_config' line
    session_config_index = lines.index('session_config:\n')

    with open('../domain.yml', 'w') as f:
        f.write(version_line + '\n\n')  # Add an extra newline after the version line
        f.write('intents:\n')
        for intent in intents:
            f.write(f'  - {intent}\n')  # Ensure proper indentation

        f.write('\nresponses:\n')
        for response_key, response_list in responses.items():
            f.write(f'  {response_key}:\n')
            for response in response_list:
                f.write(f'  - text: "{response["text"]}"\n')  # Ensure proper indentation for response text
                if "image" in response:
                    f.write(f'    image: "{response["image"]}"\n')  # Ensure proper indentation for image if present

        # Write the session_config block
        f.writelines(lines[session_config_index:])  # Write the session_config block as it is

    return "Intent and response added successfully!"


if __name__ == '__main__':
    app.run(debug=True)
