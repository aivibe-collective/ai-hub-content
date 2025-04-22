#!/usr/bin/env python3
"""
Simple test script that doesn't rely on pytest.
"""

import unittest
import json
import flask

class SimpleTest(unittest.TestCase):
    """Simple test case."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a Flask test app
        self.app = flask.Flask(__name__)
        self.app.testing = True
    
    def test_simple(self):
        """Simple test that always passes."""
        self.assertTrue(True)
    
    def test_flask_app(self):
        """Test that Flask app works."""
        # Define a simple route
        @self.app.route('/test', methods=['GET'])
        def test_route():
            return flask.jsonify({'status': 'success'})
        
        # Create a test client
        client = self.app.test_client()
        
        # Make a request
        response = client.get('/test')
        
        # Assert
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertEqual(response_data['status'], 'success')
    
    def test_flask_request(self):
        """Test Flask request handling."""
        # Define a simple route
        @self.app.route('/test', methods=['POST'])
        def test_route():
            request_json = flask.request.get_json()
            if not request_json:
                return flask.jsonify({'status': 'error'}), 400
            return flask.jsonify({'status': 'success', 'data': request_json})
        
        # Create a test client
        client = self.app.test_client()
        
        # Make a request
        test_data = {'key': 'value'}
        response = client.post('/test', json=test_data)
        
        # Assert
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertEqual(response_data['status'], 'success')
        self.assertEqual(response_data['data'], test_data)

if __name__ == '__main__':
    unittest.main()
