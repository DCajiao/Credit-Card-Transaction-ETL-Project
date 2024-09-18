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
        pass

    def get_by_year(self, year):
        pass

    def get_by_range_of_years(self, start, end):
        pass


def get_api_documentation():
    with open('../README.md', encoding="utf-8") as f:
        return f.read()
