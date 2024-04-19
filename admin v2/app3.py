from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index3.html')
@app.route('/add_story', methods=['POST'])
def add_story():
    story_name = request.form['story_name']
    intent = request.form['intent']
    action = request.form['action']

    with open('../stories.yml', 'a') as f:
        f.write(f"\n\n- story: {story_name}\n")
        f.write("  steps:\n")
        f.write(f"  - intent: {intent}\n")
        f.write(f"  - action: {action}\n")

    return "Story added successfully!"


if __name__ == '__main__':
    app.run(debug=True)
