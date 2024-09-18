import logging
import json

from flask import Flask, request, jsonify

import app.datamanagement as datamanagement

datafunctions = datamanagement.DataManagement()

######## LOGGING CONFIGURATION ########
logging.basicConfig(level=logging.INFO)

######## FLASK APP CONFIGURATION ######
app = Flask(__name__)

#######################################


@app.route('/api/v1/documentation', methods=['GET'])
def documentation():
    logging.info("Documentation requested")
    return datamanagement.get_api_documentation()


@app.route('/api/v1/data/', methods=['GET'])
def get_all_data():
    logging.info("All data requested")
    return jsonify(datafunctions.get_all_the_df().to_dict())


@app.route('/api/v1/data/available_countries', methods=['GET'])
def get_countries():
    logging.info("Countries requested")
    response = datafunctions.get_countries().tolist()
    return jsonify({"countries": response}), 200


@app.route('/api/v1/data/countries', methods=['GET'])
def get_by_countries():
    list_countries = request.get_json()  
    if list_countries is None or not isinstance(list_countries, list):
        return jsonify({"error": "You need to provide a list of countries"}), 400
    logging.info("Data requested for countries: %s", list_countries)
    response = datafunctions.get_by_countries(list_countries)
    return jsonify(response), 200

@app.route('/api/v1/data/country_code/<country_code>', methods=['GET'])
def get_by_country_code(country_code):
    logging.info("Data requested for country code: %s", country_code)
    response = datafunctions.get_by_country_code(country_code)
    return jsonify(response), 200 if "error" not in response else 404

@app.route('/api/v1/data/year/<int:year>', methods=['GET'])
def get_by_year(year):
    logging.info("Data requested for year: %d", year)
    response = datafunctions.get_by_year(year)
    return jsonify(response), 200 if "error" not in response else 404


@app.route('/api/v1/data/years', methods=['GET'])
def get_by_range_of_years():
    start_year = request.args.get('start', type=int)
    end_year = request.args.get('end', type=int)
    
    if start_year is None or end_year is None:
        return jsonify({"error": "You need to provide 'start' and 'end' query parameters"}), 400
    
    logging.info("Data requested for years range: %d-%d", start_year, end_year)
    response = datafunctions.get_by_range_of_years(start_year, end_year)
    return jsonify(response), 200 if "error" not in response else 404

#########################################################
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
