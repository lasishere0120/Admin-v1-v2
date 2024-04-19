from flask import Flask, render_template, request
import yaml

app = Flask(__name__, static_folder='static')


@app.route('/')
def index():
    return render_template('page de acueil.html')


#pour l ajouter de dataset
def intent_exists(intent_name, nlu_data):
        return intent_name in nlu_data


def add_intent(IN, EX):
    # Load NLU data
    with open('../nlu.yml', 'r') as f:
        nlu_data = f.read()

    # Check if intent already exists
    if intent_exists(IN, nlu_data):
        return "Intent already exists!"
    else:

        formatted_examples = ["    - " + example.strip() for example in EX.split('\n')]

        with open('../nlu.yml', 'a') as f:
            f.write(f"\n- intent: {IN}\n")
            f.write("  examples: |\n")
            f.write('\n'.join(formatted_examples) + '\n')

    return "Intent added successfully!"


def add_story(SN, I, A):
    with open('../stories.yml', 'r') as f:
        existing_stories = f.read()

    # Construct the story string
    new_story = f"\n\n- story: {SN}\n"
    new_story += "  steps:\n"
    new_story += f"  - intent: {I}\n"
    new_story += f"  - action: {A}\n"

    # Check if the story already exists, if not, add it
    if new_story in existing_stories:
        return "Story already exists!"

    # Add the new story
    with open('../stories.yml', 'a') as f:
        f.write(new_story)

    return "Story added successfully!"


def add_response(IN, RN, RC):
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
    print(responses)

    # Check if the intent already exists, if not, add it
    if IN not in intents:
        intents.append(IN)

    # Construct response key
    response_key = f"utter_{RN}"

    # Check if the response already exists, if not, add it
    if response_key in responses:
        return "Response name already exists!"

    responses[response_key] = []

    # Split the RC by newline and add each line as a separate response
    for line in RC.split('\n'):
        line = line.strip()  # Remove leading and trailing whitespace
        if line:  # Skip empty lines
            responses[response_key].append({'text': line})

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
                # You can add other fields such as image here if needed

        # Write the session_config block
        f.writelines(lines[session_config_index:])  # Write the session_config block as it is

    return "Intent and response added successfully!"


@app.route('/add_data', methods=['POST'])
def handle_add_data():
    intent_name = request.form['name_intent']
    examples = request.form['examples']
    response_name = request.form['response_name']
    response_text = request.form['response_text']

    add_intent_result = add_intent(intent_name, examples)
    add_response_result = add_response(intent_name, response_name, response_text)

    story_name = "admin story"
    action_global = "utter_" + response_name
    intent_global = intent_name
    add_story_result = add_story(story_name, intent_global, action_global)

    # Concatenate all the results into a single response
    response = f"{add_intent_result}\n{add_response_result}\n{add_story_result}"

    return response

#modfier dataset


def update_intent(IN, EX):
    # Load NLU data
    with open('nlu.yml', 'r') as f:
        nlu_data = f.readlines()

    # Check if intent already exists
    intent_index = intent_exists(IN, nlu_data)
    if intent_index != -1:
        # Intent already exists, update its examples
        formatted_examples = ["    - " + example.strip() + "\n" for example in EX.split('\n')]

        # Find the start index of the examples section
        start_index = nlu_data.index(f"- intent: {IN}\n") + 2
        # Find the end index of the examples section
        end_index = len(nlu_data)  # Default to end of file
        for i in range(start_index + 1, len(nlu_data)):
            if nlu_data[i].startswith("- intent:"):
                end_index = i
                break
        # Replace existing examples with new examples
        nlu_data[start_index:end_index] = formatted_examples
        # Write updated NLU data back to the file
        with open('nlu.yml', 'w') as f:
            f.writelines(nlu_data)
        return "Intent examples updated successfully!"
    else:
        return "Intent not exist"


def intent_exists(intent_name, nlu_data):
    # Check if intent exists in the NLU data
    for index, line in enumerate(nlu_data):
        if line.strip() == f"- intent: {intent_name}":
            return index
    return -1


def update_response_text(RN, RC):
    with open('../domain.yml', 'r') as f:
        lines = f.readlines()

    # Find the index of the 'responses' section
    responses_index = lines.index('responses:\n')

    # Extract existing responses
    existing_responses = {}
    for i in range(responses_index + 1, len(lines)):
        line = lines[i].strip()
        if line.startswith('utter_'):
            response_key = line.split(':')[0].strip()
            existing_responses[response_key] = []
        elif line.startswith('- text:'):
            existing_responses[response_key].append(line.strip()[8:])  # Extract response text
    response_key = f"utter_{RN}"

    # Check if the response exists
    if response_key not in existing_responses:
        return "Response does not exist!"

    # Find the index of the response to be updated
    response_index = lines.index(f'  {response_key}:\n')


    # Replace the existing response text with new text
    lines[response_index + 1] = f'  - text: "{RC.strip()}"\n'

    # Write the updated responses back to the domain.yml file
    with open('../domain.yml', 'w') as f:
        f.writelines(lines)

    return "Response text updated successfully!"







@app.route('/update_data', methods=['POST'])
def handle_data():
    intent_name = request.form['intent_name']
    examples = request.form['new_examples']
    rep_name = request.form['resp_name']
    rep_text=request.form['resp_text']

    add_intent_result = update_intent(intent_name, examples)
    add_rep_result=update_response_text(rep_name,rep_text)



    # Concatenate all the results into a single response
    response = f"{add_intent_result},{add_rep_result}"

    return response

#supprimer dataset

def remove_intent(intent_name):
    try:
        with open('nlu.yml', 'r') as f:
            nlu_data = f.readlines()

        # Find the index of the intent to be removed
        intent_index = -1
        for i, line in enumerate(nlu_data):
            if line.strip() == f"- intent: {intent_name}":
                intent_index = i
                break

        if intent_index != -1:
            # Find the start and end index of the intent block
            start_index = intent_index
            while start_index >= 0 and nlu_data[start_index].strip() != '':
                start_index -= 1
            end_index = intent_index
            while end_index < len(nlu_data) and nlu_data[end_index].strip() != '':
                end_index += 1

            # Remove the intent block from the list of lines
            del nlu_data[start_index + 1:end_index]

            # Write the updated data back to the file
            with open('nlu.yml', 'w') as f:
                f.writelines(nlu_data)

            return f"Intent '{intent_name}' removed successfully!"
        else:
            return f"Intent '{intent_name}' not found!"
    except Exception as e:
        return f"Error removing intent: {str(e)}"

@app.route('/remove_intent', methods=['POST'])
def remove_intent_route():
    intent_name = request.form.get('intent_name')
    if intent_name:
        message = remove_intent(intent_name)
    else:
        message = "Please provide an intent name."
    return message

@app.route('/ajouter')
def ajouter_final():
    return render_template('Ajouter_final.html')
@app.route('/acueil')
def acueil():
    return render_template('page de acueil.html')
@app.route('/modifier')
def modifier():
    return render_template('Modifier_final.html')
@app.route('/supprimer')
def supp():
    return render_template('Supprimer.html')

if __name__ == '__main__':
    app.run(debug=True)
