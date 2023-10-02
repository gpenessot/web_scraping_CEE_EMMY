
from bs4 import BeautifulSoup
import requests
import pandas as pd
import numpy as np
from io import StringIO
from datetime import datetime
import locale
import plotly.express as px
import warnings

warnings.filterwarnings("ignore")
locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')

ANNEES = [i for i in range(2009, datetime.now().year+1)] #date eproduction classique
ANNEES2 = [i for i in range(2017, datetime.now().year+1)] #date production précarité
ANNEE_COURANTE = datetime.now().year


def currate_dataframe(dataframe):
    """
    Clean and modify the input pandas DataFrame.

    Args:
        dataframe (pandas.DataFrame): The DataFrame to be processed. It should have a header row and the columns 'Date', 'Prix Moyen pondéré (en €/MWh)', and 'Volume Total (en GWh Cumac)'.

    Returns:
        pandas.DataFrame: The modified DataFrame with the header row removed, column names set, 'Prix Moyen pondéré (en €/MWh)' column converted to float values, and 'Volume Total (en GWh Cumac)' column converted to integer values.
    """
    header = dataframe.iloc[0]
    dataframe = dataframe[1:]
    dataframe.columns = header
    dataframe = dataframe.rename_axis('', axis='columns')
    dataframe = dataframe.rename_axis('Date')
    dataframe=dataframe.fillna(0)
    dataframe['Prix Moyen pondéré (en €/MWh)'] = dataframe['Prix Moyen pondéré (en €/MWh)'].astype('int') / 100
    dataframe['Volume Total (en GWh Cumac)'] = dataframe['Volume Total (en GWh Cumac)'].astype('string').apply(lambda x: x.replace(u'\xa0', '').replace(',', ''))
    dataframe['Volume Total (en GWh Cumac)'] = dataframe['Volume Total (en GWh Cumac)'].astype('int')

    return dataframe


def add_start_month(dataframe, year):
    """
    Adds the start month to the index of a pandas DataFrame by converting the existing index values to a specific date format.

    Args:
        dataframe (pd.DataFrame): The pandas DataFrame object.
        year (int): The year.

    Returns:
        pd.DataFrame: A modified copy of the input DataFrame with the start month added to the index.

    Raises:
        TypeError: If the 'dataframe' input is not an instance of pd.DataFrame.
        ValueError: If the 'year' input is not an integer or is less than 0.
    """
    if not isinstance(dataframe, pd.DataFrame):
        raise TypeError("'dataframe' n'est pas un objet pandas.Dataframe")
    if not isinstance(year, int) or year < 0:
        raise ValueError("'year' doit être un entier positif")
    new_dataframe = dataframe.copy()
    new_dataframe.index = new_dataframe.index.map(lambda x: datetime.strptime(f'01/{x}/{year}', '%d/%B/%Y').strftime('%d/%m/%Y'))    
    new_dataframe.index = pd.to_datetime(new_dataframe.index, format="%d/%m/%Y")
    
    return new_dataframe


def get_table_from_website(current_year, cotation_year, type_cee="false"):
    """
    Retrieves a table from a website based on the input parameters.

    Args:
        current_year (int): The current year for which the table is requested.
        cotation_year (int): The year for which the cotation is requested.
        type_cee (str, optional): The type of cee. Defaults to "false".

    Returns:
        pandas.DataFrame: The transposed table retrieved from the website.
    """
    url = f"https://www.emmy.fr/public/donnees-mensuelles?selectedYearCee={current_year}&precarite={type_cee}&selectedYearCotation={cotation_year}#graphic-cotation"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content , "html.parser")
            table = soup.find('div', attrs={'class':'vat public-cotation-transfert'}).find_all('table')
            table = pd.read_html(StringIO(str(table[0])))[0].transpose()
            table = currate_dataframe(table)
            if type_cee == "false":
                table['Type CEE']="Classique"
            else:
                table['Type CEE']="Précarité"
            table = add_start_month(table, cotation_year)
            return table
        else:
            print('Erreur', response.status_code)
    except Exception as e:
        print('Erreur', e)


#columns=['Prix Moyen pondéré (en €/MWh)', 'Volume Total (en GWh Cumac)', 'Nombre de transactions', 'Type CEE']
def compil_data_from_emmy(list_cee_type = ['false', 'true'], current_year=ANNEE_COURANTE):
    full_data = pd.DataFrame()
    for cee in list_cee_type:
        if cee == 'false':
            for year in ANNEES:
                temp = get_table_from_website(current_year=current_year,
                                              cotation_year=year,
                                              type_cee=cee)
                try:
                    full_data = pd.concat([full_data, temp])
                except Exception as e:
                    print(e)
        else:
            for year in ANNEES2:
                temp = get_table_from_website(current_year=current_year,
                                              cotation_year=year,
                                              type_cee=cee)
                try:
                    full_data = pd.concat([full_data, temp])
                except Exception as e:
                    print(e)
    
    return full_data


if '__name__' == '__main__':
    historical_data_cee = compil_data_from_emmy()
    historical_data_cee.to_csv('cee_historical_data.csv')