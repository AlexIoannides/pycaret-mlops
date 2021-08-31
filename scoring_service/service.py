"""
This module defines the model-scoring service in the following steps:

- loads the ML model into memory;
- defines the ML scoring REST API endpoints; and,
- starts the service.

When running the script locally, the scoring service can be tested from
the command line using,

curl http://0.0.0.0:5000/iris/v1/score \
    --request POST \
    --header "Content-Type: application/json" \
    --data '{"sepal_length": 5.1, "sepal_width": 3.5, "petal_length": 1.4, "petal_width": 0.2}'

The expected response should be,
{
    "species_prediction":"setosa"
    "probabilities": "setosa=1.0|versicolor=0.0|virginica=0.0",
    "model_info": "DecisionTreeClassifier(class_weight='balanced', random_state=42)"
}
"""
from typing import Dict

import numpy as np
from flask import Flask, jsonify, make_response, request, Response
from joblib import load
from sklearn.base import BaseEstimator

MODEL_PATH = 'classification_model.joblib'
CLASS_TO_SPECIES_MAP = {0: 'setosa', 1: 'versicolor', 2: 'virginica'}

app = Flask(__name__)


@app.route('/iris/v1/score', methods=['POST'])
def score() -> Response:
    """Iris species classification API endpoint"""
    request_data = request.json
    X = make_features_from_request_data(request_data)
    model_output = model_predictions(X)
    response_data = jsonify({**model_output, 'model_info': str(model)})
    return make_response(response_data)


def make_features_from_request_data(
    request_data: Dict[str, float]
) -> np.ndarray:
    """Create feature array from JSON data parsed as dictionay."""
    X = np.array(
        [request_data['sepal_length'],
         request_data['sepal_width'],
         request_data['petal_length'],
         request_data['petal_width']],
        ndmin=2
    )
    return X


def model_predictions(features: np.ndarray) -> Dict[str, str]:
    """Return model scores for a single instance of feature data."""
    class_prediction = int(model.predict(features)[0])
    class_probabilities = model.predict_proba(features)[0]
    species_prediction = CLASS_TO_SPECIES_MAP[class_prediction]
    species_probabilities = [
        f'{k}={v}'
        for k, v in zip(CLASS_TO_SPECIES_MAP.values(), class_probabilities)
    ]
    results = {
        'species_prediction': species_prediction,
        'probabilities': '|'.join(species_probabilities)
    }
    return results


if __name__ == '__main__':
    model = load(MODEL_PATH)
    print(f'loaded model={model}')
    print(f'starting API server')
    app.run(host='0.0.0.0', port=5000)
