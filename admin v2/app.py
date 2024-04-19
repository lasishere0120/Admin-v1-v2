from flask import Flask, render_template, request
import yaml

app = Flask(__name__)


def load_yaml(file_path):
    try:
        with open(file_path, 'r') as yaml_file:
            data = yaml.safe_load(yaml_file)
        return data
    except Exception as e:
        print(f"Error loading YAML file: {e}")
        return {}


def dump_yaml(data, file_path):
    with open(file_path, 'w') as yaml_file:
        yaml.dump(data, yaml_file, default_flow_style=False, sort_keys=False, allow_unicode=True)



@app.route('/')
def index():
    return render_template('index.html')


@app.route('/add_rule', methods=['POST'])
def add_rule():
    rule_name = request.form['rule_name']
    intent_name = request.form['intent_name']
    action_name = request.form['action_name']

    # Load existing rules from YAML file
    yaml_data = load_yaml('../rules.yml')

    # Create new rule dictionary
    new_rule = {'rule': rule_name, 'steps': [{'intent': intent_name}, {'action': action_name}]}

    # Add new rule next to the last rule
    yaml_data['rules'].insert(-1, new_rule)

    # Dump the updated YAML data back to the file
    dump_yaml(yaml_data, '../rules.yml')

    return 'Rule added successfully!'


if __name__ == '__main__':
    app.run(debug=True)
