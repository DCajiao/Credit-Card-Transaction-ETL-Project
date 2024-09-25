import pandas as pd


class DataManagement:
    def __init__(self):
        self.df = pd.read_csv('./data/world_population.csv')

    def get_all_the_df(self):
        return self.df

    def get_countries(self):
        return self.df['Country/Territory'].unique()

    def get_by_countries(self, list_countries):
        # Filter the DataFrame by the list of countries
        filtered_data = self.df[self.df['Country/Territory'].isin(
            list_countries)]
        
        if filtered_data.empty:
            return ({"error": "No data found for the provided countries"}), 404
        
        # Convert the filtered DataFrame to a list of dictionaries
        result = filtered_data.to_dict(orient='records')
        return result

    def get_by_country_code(self, country_code):
        # Filter by the CCA3 country code
        filtered_data = self.df[self.df['CCA3'] == country_code]
        
        if filtered_data.empty:
            return {"error": f"No data found for the country code {country_code}"}, 404
        
        # Convert the filtered DataFrame to a list of dictionaries
        result = filtered_data.to_dict(orient='records')
        return result

    def get_by_year(self, year):
        # Filter the DataFrame by a specific year
        column_name = f"{year} Population"  # Format the year column dynamically
        if column_name not in self.df.columns:
            return {"error": f"No data available for the year {year}"}, 404

        filtered_data = self.df[['Country/Territory', column_name]]
        # Convert the filtered DataFrame to a list of dictionaries
        result = filtered_data.to_dict(orient='records')
        return result

    def get_by_range_of_years(self, start, end):
        # Create a list of columns for the range of years
        columns_to_include = [f"{year} Population" for year in range(start, end + 1) if f"{year} Population" in self.df.columns]
        
        if not columns_to_include:
            return {"error": f"No data available for the range {start}-{end}"}, 404
        
        # Filter the DataFrame by the selected columns
        filtered_data = self.df[['Country/Territory'] + columns_to_include]
        # Convert the filtered DataFrame to a list of dictionaries
        result = filtered_data.to_dict(orient='records')
        return result

def get_api_documentation():
    with open('../../README.md', encoding="utf-8") as f:
        return f.read()
