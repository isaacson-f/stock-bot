import yfinance as yf
import pandas as pd
from typing import List

class Cash_Flow:
    """ This class represents the cash flow statement of the provided yfinance ticker.

        Attributes:
            cash_flow: Complete cash flow dataframe
            investing_activities: Dictionary with each investing activity value corresponding the the year key
            financing_activities: Dictionary with each financing activity value corresponding the the year key
            operating_activities: Dictionary with each operating activity value corresponding the the year key
            change_to_liabilities: Dictionary with each change to liabilities value corresponding the the year key
            net_income: Dictionary with each net income value corresponding the the year key
            change_in_cash: Dictionary with each change in cash value corresponding the the year key
    """
    def __init__(self, ticker : yf.Ticker):
        """ Initializes the cash flow object. Takes the dataframe provided from the yfinance api cash flow statement
            and extracts and seperates the information within it to different attributes of a cash flow statement.

            Raises:
                ValueError if the ticker provided is None or if an improper row name is provided to the _value method
        """
        if ticker is None:
            raise ValueError('Ticker cannot be none')
        self.__cash_flow : pd.DataFrame = ticker.get_cashflow()
        self.__investing_activities: dict[int:int] = self._value('Total Cashflows From Investing Activities')
        self.__financing_activites : dict[int:int] = self._value('Total Cash From Financing Activities')
        self.__operating_activities : dict[int:int] = self._value('Total Cash From Operating Activities')
        self.__change_to_liabilities : dict[int:int] = self._value('Change To Liabilities')
        self.__net_income : dict[int:int] = self._value('Net Income')
        self.__change_in_cash : dict[int:int] = self._value('Change In Cash')
        #self.__change_in_net_income = self._value('Change to Netincome')

    def __str__(self) -> str:
        """ Returns a string of this object

            Returns:
                String based representation of the cash flow object.
        """
        return str(self.__cash_flow)

    def _value(self, row_name : str) -> dict:
        """ Returns a dictionary of the row under the provided row name (year : value)

            Args:
                row_name: The row to be returned as a dictionary with each column as a key.

            Raises:
                ValueError if the provide row name is not in the dataframe   

            Returns:
                dictionary of row under provided name, with column names as keys and row values as values      

        """
        new_dict = {}
        try:
            dates = self.__cash_flow.loc[row_name].keys()
            values = self.__cash_flow.loc[row_name]
            for i in range(0,len(dates)):
                date = dates[i].date().year
                new_dict[date] = values[i]
        except KeyError:
            raise ValueError('Invalid row name')        
        return new_dict

    @property
    def cash_flow(self) -> pd.DataFrame:
        """ Returns the cash flow information obtained from yfinance api

            Returns:
                Dataframe of 3 years of cash flows
        """
        return self.__cash_flow

    def get_investing_activities(self, *years : int):
        """ Returns each investing activity value in the provided years in a list

            Args:
                years: Each year of the desired investing activity

            Raises:
                ValueError if a year provided is not available on the yfinance api

            Returns:
                List of each investing value
        """
        return self._get_values(self.__investing_activities, years)

    def get_operating_activities(self, *years : int) -> List[int]:
        """ Returns each operating activity value in the provided years in a list

            Args:
                years: Each year of the desired operating activities value

            Raises:
                ValueError if a year provided is not available on the yfinance api

            Returns:
                List of each operating activity value    
        """
        return self._get_values(self.__operating_activities, years)

    def get_change_to_liabilities(self, *years : int) -> List[int]:
        """ Returns each change to liabilities value in the provided years in a list

            Args:
                years: Each year of the desired change to liabilities value

            Raises:
                ValueError if a year provided is not available on the yfinance api

            Returns:
                List of each change to liability value    
        """
        return self._get_values(self.__change_to_liabilities, years)

    def get_net_income(self, *years : int) -> List[int]:
        """ Returns each net income value in the provided years in a list

            Args:
                years: Each year of the desired net income value

            Raises:
                ValueError if a year provided is not available on the yfinance api

            Returns:
                List of each net income value    
        """
        return self._get_values(self.__net_income, years)

    def get_change_in_cash(self, *years):
        """ Returns each change in cash value in the provided years in a list

            Args:
                years: Each year of the desired change in cash

            Raises:
                ValueError if a year provided is not available on the yfinance api

            Returns:
                List of each change in cash value    
        """
        return self._get_values(self.__change_in_cash, years)

    def get_change_in_net_income(self, *years):
        """ Returns each change in net income in the provided years in a list

            Args:
                years: Each year of the desired change in net income

            Raises:
                ValueError if a year provided is not available on the yfinance api

            Returns:
                List of each change in net income value    
        """
        return self._get_values(self.__change_in_net_income, years)

    def get_free_cash_flow(self, years : List[int]) -> List[int]:
        """ Returns the free cash flow for the desired years.

            Args:
                years: list of each year which the free cash flow is desired

            Raises:
                ValueError if one of the years provided is invalid

            Returns:
                List of the free cash flow values 
        """
        if not years:
            years = list(self.__operating_activities.keys())
        capital_expenditures = self._value('Capital Expenditures')
        expenditures = self._get_values(capital_expenditures, years)  
        operating_activities = self._get_values(self.__operating_activities, years)
        free_cash_flow = []
        for i in range(0, len(expenditures)):
             free_cash_flow.append(operating_activities[i] + expenditures[i])
        years_available = capital_expenditures.keys()
        free_cash_flow_dict = {}
        for i in range(0, len(years)):
            if capital_expenditures.get(years[i], -1) != -1 and self.__operating_activities.get(years[i], -1) != -1:
                free_cash_flow_dict[years[i]] = free_cash_flow[i]
            else:
                raise ValueError("Invalid year input")    
        return free_cash_flow_dict

    def _get_values(self, dict, years : List[int]) -> List[int]:
        values = []
        if not years:
            years = dict.keys()
        for year in years:
            value_to_append = dict.get(year, -1)
            if value_to_append is -1:
                raise ValueError("%r year is not valid" % year)
            values.append()
        return values
    

class Balance_Sheet:
    """ This class represents the balance sheet statement of the provided yfinance ticker.

        Attributes:
            balance_sheet: 3 year balance sheet dataframe for the provided ticker
            total_liability: 3 year total liability value dictionary 
            total_stockholder_equity: 3 year total stockholder equity value dictionary
            total_assets: 3 year total assets value dictionary
            common_stock: 3 year common stock value dictionary
            cash: 3 year cash value dictionary
            total_current_liabilities: 3 year current liabliities dictionary
            total_current_assets: 3 year current assets dictionary
            retained_earnings: 3 year retained earnings dictionary
    """

    def __init__(self, ticker):
        self.__balance_sheet : dict[int: int] = ticker.get_balance_sheet()
        self.__total_liability : dict[int:int] = self.__value('Total Liab')
        self.__total_stockholder_equity : dict[int:int] = self.__value('Total Stockholder Equity')
        self.__total_assets : dict[int:int] = self.__value('Total Assets')
        self.__common_stock : dict[int:int] = self.__value('Common Stock')
        self.__cash = self.__value('Cash')
        self.__total_current_liabilities = self.__value('Total Current Liabilities')
        self.__total_current_assets = self.__value('Total Current Assets')
        self.__retained_earnings = self.__value('Retained Earnings')

    def __str__(self):
        return str(self.__balance_sheet)        
        
    def __value(self, row_name):
        new_dict = {}
        dates = self.__balance_sheet.loc[row_name].keys()
        values = self.__balance_sheet.loc[row_name]
        for i in range(0,len(dates)):
            date = dates[i].date().year
            new_dict[date] = values[i]
        return new_dict 
    
    def get_balance_sheet(self):
        return self.__balance_sheet

    def get_total_liability(self, *years):
        return self._get_values(self.total_liability, years)

    def get_total_stockholder_equity(self, *years):
        return self._get_values(self.__total_stockholder_equity, years)

    def get_total_assets(self, years):
        return self._get_values(self.__total_assets, years)

    def get_common_stock(self, *years):
        return self._get_values(self.__common_stock, years)

    def get_cash(self, *years):
        return self._get_values(self.__cash, years)

    def get_current_liabilities(self, years):
        return self._get_values(self.__total_current_liabilities, years)

    def get_current_assets(self, years):
        return self._get_values(self.__total_current_assets, years)

    def get_retained_earnings(self, *years):
        return self._get_values(self.__retained_earnings, years)

    def _get_values(self, dict, years):
        values = []
        if not years:
            years = dict.keys()
        for year in years:
            values.append(dict.get(year, -1))
        return values



class Income_Statement:

    def __init__(self, ticker):
        self.__ticker = ticker
        self.__financials = self.__ticker.get_financials()
        self.__net_sales = self.__value('Total Revenue')
        self.__cogs = self.__value('Cost Of Revenue')
        self.__gross_profit = self.__value('Gross Profit')
        self.__operating_income = self.__value('Operating Income')
        self.__op_expenses = self.__value('Total Operating Expenses')
        self.__ibit = self.__value('Income Before Tax')
        self.__income_tax = self.__value('Income Tax Expense')
        self.__net_income = self.__value('Net Income')

    def __str__(self):
        return str(self.__financials)

    def __value(self, row_name):
        new_dict = {}
        dates = self.__financials.loc[row_name].keys()
        values = self.__financials.loc[row_name]
        for i in range(0,len(dates)):
            date = dates[i].date().year
            new_dict[date] = values[i]

        return new_dict

#years can only go up to 4 yeasr
    def get_net_sales(self, *years):
        dict = self.__net_sales
        return self._get_values(dict, years)

    def get_cogs(self, *years):
        dict = self.__cogs
        return self._get_values(dict, years)    

    def get_gross_profit(self, *years):
        dict = self.__gross_profit
        return self._get_values(dict, years)

    def get_op_expenses(self, *years):
        dict = self.__op_expenses
        return self._get_values(dict, years)

    def get_op_income(self, *years):
        dict = self.__operating_income
        return self._get_values(dict, years)

    def get_ibit(self, *years):
        dict = self.__ibit
        return self._get_values(dict, years)

    def get_income_tax(self, *years):
        dict = self.__income_tax
        return self._get_values(dict, years)                        

    def get_net_income(self, years):
        dict = self.__net_income
        return self._get_values(dict, years)

    def _get_values(self, dict, years):
        values = []
        if not years:
            years = dict.keys()
        for year in years:
            values.append(dict.get(year, -1))
        return values      