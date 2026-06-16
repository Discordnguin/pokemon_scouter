from flask import Flask, render_template, request, jsonify
from web.models import ScoutRequest
from web.controllers import ScoutController

app = Flask(__name__, template_folder='web/templates', static_folder='web/static')

controller = ScoutController()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/generate-scouts', methods=['POST'])
def generate_scouts():
    data = request.json
    try:
        scout_request = ScoutRequest.from_json(data)
        result = controller.generate_scouts(scout_request)
        return jsonify({'status': 'success', 'output': result})
    except ValueError as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Error: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
