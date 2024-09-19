# API World Population - ETL project: Documentation

## 1. Overview

This API provides information on the world population over the years, information related to territorial extension, population density, growth rate and percentage of the world population.

## 2. Folder structure

The folder structure of this project is as follows:

```
api/
│
├── Dockerfile                  # Docker file for containerization
├── README.md                   # Project documentation
├── requirements.txt            # Dependencies required to run the API
└── src/                        # Main folder containing the source code
    ├── app/
    │   └── datamanagement.py  # Logic for data management
    ├── data/                  # Folder containing the data used by the API
    └── main.py                # Main file to run the Flask application
```

## 3. Usage

### Available Methods:

1. **GET `/api/v1/documentation`**
   - Description: Returns the API documentation.
   - Response: 
     ```json
     {
       "documentation": "<content>"
     }
     ```
   - Status Code: `200 OK`

2. **GET `/api/v1/data/`**
   - Description: Fetches all available data.
   - Response: Returns the data in JSON format.
     ```json
     {
       "<column_name>": { ... }
     }
     ```
   - Status Code: `200 OK`

3. **GET `/api/v1/data/available_countries`**
   - Description: Returns a list of available countries in the dataset.
   - Response: 
     ```json
     {
       "countries": ["<country1>", "<country2>", ...]
     }
     ```
   - Status Code: `200 OK`

4. **GET `/api/v1/data/countries`**
   - Description: Filters the data by country.
   - Query Parameters: 
     - `countries`: List of countries to filter by.
   - Response: Returns the data filtered by the specified countries.
     ```json
     {
       "<country_name>": { ... }
     }
     ```
   - Status Code: `200 OK` (if the filter is successful) or `400 Bad Request` (if parameters are missing or there's an error in the query).

### Example Usage

To fetch all available data, you can make an HTTP GET request:

```bash
curl -X GET http://localhost:5000/api/v1/data/
```

To get the available countries in the dataset:

```bash
curl -X GET http://localhost:5000/api/v1/data/available_countries
```

## 4. How to clone and run locally using venv

Follow these steps to clone and run the project locally:

1. **Clone the repository**:
   ```bash
   git clone Credit-Card-Transaction-Airflow-ETL-Project
   cd Credit-Card-Transaction-Airflow-ETL-Project/api
   ```

2. **Create and activate a virtual environment using `venv`**:
   - On Linux/MacOS:
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```
   - On Windows:
     ```bash
     python -m venv venv
     venv/Scripts/activate
     ```

3. **Install the dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**:
   ```bash
   cd src
   python main.py
   ```

   The API will be available at `http://localhost:5000`.
  
You can still test the API deployed in Render here: https://api-world-population-etl-project.onrender.com

## 5. Docker

If you prefer to use Docker to run the API, you can build and run the image with the following commands:

1. **Build the image**:
   ```bash
   docker build -t api:latest .
   ```

2. **Run the container**:
   ```bash
   docker run -p 5000:5000 api:latest
   ```

## 6. Requirements

- Python 3.x
- Flask
- Other dependencies listed in `requirements.txt`