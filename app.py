from flask import Flask
from flask import request, jsonify, abort

from CMC_service import cmc_service

app = Flask(__name__)


@app.route('/healthCheck', methods=['GET'])
def health_check():
    return 'CMC service is running'


@app.route('/message', methods=['POST'])
def message():
    data = request.json
    friend_name = data.get("friendName", None)
    message_content = data.get("message", None)
    if friend_name is None or message is None:
        abort(400, description='Bad request!The reqeust must contain "friendName" and "message" field')
    response = cmc_service.select_response(friend_name, message_content)
    return response


@app.route('/rate', methods=['POST'])
def rate():
    data = request.json
    friend_name = data.get("friendName", None)
    message_content = data.get("message", None)
    response_content = data.get("response", None)
    is_like = data.get("like", None)
    if friend_name is None or (not isinstance(is_like, bool)):
        abort(400, description='Bad request!The reqeust must contain "friendName", "message", "response" and "is_like" field, ' \
                   'and "is_like" field should be true or false')
    rate_result = cmc_service.rate_func(friend_name, message_content, response_content, is_like)
    if rate_result.is_success:
        return rate_result.message
    else:
        abort(400, description=rate_result.message)


@app.route('/saveData', methods=['POST'])
def save_data():
    cmc_service.save_data()
    return 'successfully save data to file'


@app.route('/inspect', methods=['GET'])
def inspect():
    parameter = request.args.get('type')
    result = cmc_service.inspect(parameter)
    return result


@app.errorhandler(400)
def error_handler(e):
    return jsonify(error=str(e)), 400


if __name__ == '__main__':
    # app.run(port=5000, debug=True)
    app.run(port=5000)
