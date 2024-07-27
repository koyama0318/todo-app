from flask import Flask, request, jsonify, abort
import logging

app = Flask(__name__)
GITHUB_SECRET = 'secret'
logging.basicConfig(level=logging.DEBUG)

def log_issue_details(issue_title, issue_body, issue_number, action):
    app.logger.debug(f"action #{action}")
    app.logger.debug(f"number #{issue_number}")
    app.logger.debug(f"title #{issue_title}")
    app.logger.debug(f"body #{issue_body}")

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/webhook', methods=['POST'])
def webhook():
    if request.method == 'POST':
        data = request.json
        if 'issue' in data:
            issue_title = data['issue']['title']
            issue_body = data['issue']['body']
            issue_number = data['issue']['number']
            action = data['action']

             # log_issue_details関数を呼び出し、コンソールに表示
            log_issue_details(issue_title, issue_body, issue_number, action)
            
            response_message = f"Issue #{issue_number} '{issue_title}' has been {action}. The body of the issue is: {issue_body}"
            app.logger.debug(response_message)

            return jsonify({'message': response_message})
        
        return jsonify({'message': 'Not an issue event'})
    
    return jsonify({'message': 'Method not allowed'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
