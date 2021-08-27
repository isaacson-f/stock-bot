# api limit of 60 calls/minute, 1/second
import finnhub
import pandas as pd
# api limit of 2000 calls/hour, or 33 calls/minute, 1/ 2 seconds
import yfinance as yf
import requests
import financial_documents as fin_doc
from bs4 import BeautifulSoup as bs
import time
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver import ActionChains
from typing import List



class Company_Info:
    """ This class represents general information regarding the provided company as provided by the yfinance api. 

        Attributes:
            info: complete information provided by calling info through the yfinance api. Consists of general information such as 
                beta value
            beta: The beta value of the stock, which represents the companies correlation to the overall market in regards
                to price
    """
    def __init__(self, company):
        """ Initializes the Company_info object

        Raises:
            ValueError if the company object provided is invalid or None

        """
        try:
            self.__info = company.ticker.info
        except KeyError:
            raise ValueError('Invalid company')
        self.__beta = self.__info['beta']
        self.__stock_price = self.__info['regularMarketPrice']
        #self.__change_in_net_income = self._value('Change to Netincome')

    @property    
    def beta(self) -> float:
        """ Returns the beta of the company provided

        Returns: beta value
        """
        return self.__beta

    @property
    def stock_price(self) -> float:
        return self.__stock_price
   

class Market_Info:
    def __init__(self, finnhub_client, info_category : str):
        if info_category == "general" or info_category =="forex" or info_category == "crypto" or info_category == "merger":
            self.__news_stories = finnhub_client.general_news(info_category, min_id=0)
        else:
            today = datetime.today()
            week_ago = today - timedelta(7)
            self.__news_stories = finnhub_client.company_news(info_category, 
            _from= week_ago.strftime('%Y-%m-%d'), to= today.strftime('%Y-%m-%d'))
        

    def _get_info(self, info_grabbing, amount=0) -> List[str]:
        if amount is 0:
            amount= len(self.__news_stories)
        data = []
        if amount > len(self.__news_stories):
            raise ValueError('Only %r' + info_grabbing + 'available ' % len(self.__news_stories))
        for i in range(0, amount):
            data.append(self.__news_stories[i].get(info_grabbing))
        return data

    def get_story_headlines(self, amount=0) -> List[str]:
        if amount is 0:
            amount= len(self.__news_stories)
        result = self._get_info('headline', amount) 
        print(result)
        return result

    def get_story_datetimes(self, amount=0) -> List[str]:
        if amount is 0:
            amount= len(self.__news_stories)
        adjusted_datetimes = []
        for unix_datetime in self._get_info( 'datetime', amount):
            timestamp = int(unix_datetime)
            adjusted_datetimes.append(time.ctime(timestamp))
        return adjusted_datetimes

    def get_summary(self, amount=0) -> List[str]:
        if amount is 0:
            amount= len(self.__news_stories)
        return self._get_info('summary', amount) 

    def get_source(self, amount=0) -> List[str]:
        if amount is 0:
            amount = len(self.__news_stories)
        return self._get_info('source', amount)      

    def get_image(self, amount=0) -> List[str]:
        if amount is 0:
            amount = len(self.__news_stories)
        return self._get_info('image', amount)

    def get_url(self, amount=0) -> List[str]:
        if amount is 0:
            amount = len(self.__news_stories)
        return self._get_info('url', amount)

    def get_category(self, amount=0) -> List[str]:
        if amount is 0:
            amount = len(self.__news_stories)
        return self._get_info('category', amount)

class Insider_Transactions:
    def __init__(self, finnhub_client, company_ticker):
        self.__insider_transactions = finnhub_client.stock_insider_transactions(company_ticker)
        self.__data : List[dict] = self.__insider_transactions.get('data')
        self.__names : str = self.__date.get('name')

class Company:

    """ Represents a public company and the relevant financial aspects of that company. The years of financial documents
        included within each object varies depending on the object, currently each one contains 3 years worth of financial
        information surrounding the company.
    
    Attributes:
        company_name: The ticker of the company
        ticker: The yfinance api ticker generated, utilized to obtain the financial information about the company
        income_statement: An Income_Statement() object representing the Income statement of the company
        cash_flow: A Cash_Flow() object representing the statement of Cash Flows for the company
        balance_sheet: A Balance_Sheet() object representing the balance sheet for the company
        comp_info: A Company_Info() object representing general information about the company
        market_cap: The market cap of the company
        stock_price: The current stock price of the company
    """
    def __init__(self, company_name, market_cap=0, stock_price=0, 
    income_statement=None, cash_flow=None, balance_sheet=None):
        """ Inits Company with the provided company name to create a hollow Company class in order to conserve API calls. The company
            may be initialized with a market_cap, stock_price, income_statement, cash_flow, or balance_sheet.

            Args:
                company_name: Name of the company
                market_cap: Market cap of the company
                stock_price: Stock price of the company
                income_statement: Object representing the income statement of the company
                cash_flow: Object representing the cash flows of the company
                balance_sheet: Object representing the balance sheet of the company

            Raises:
                ValueError: If no company name is provided    
        """
        if company_name is None:
            raise ValueError('Company_name cannot be none')

        self.__company_name = company_name
        self.__ticker = yf.Ticker(self.__company_name)
        self.__income_statement : fin_doc.Income_Statement()
        self.__cash_flow : fin_doc.Cash_Flow()
        self.__balance_sheet : fin_doc.Balance_Sheet()
        self.__comp_info : Company_Info()
        self.__comp_news : Market_Info()
        #self.__fhub_financials = finnhub_client.company_basic_financials(self.__company_name, "all")
        #self.__fhub_profile = finnhub_client.company_profile2(symbol=self.__company_name)
        #self.__fhub_peers = finnhub_client.company_peers(self.__company_name)
        #self.__fhub_sentiment = finnhub_client.news_sentiment(self.__company_name)
        #self.__yfin_info = self.__ticker.info
        self.market_cap = market_cap
        self.__stock_price = stock_price

    def setup_company(self):
        """ Sets up the financial statements and information objects.
            Serves a purpose as to not overwhelm the api with calls, ensuring no limit is passed.

            Raises:
                ValueError: If the company object has an invalid company_name
        """
        try:
            finnhub_client = finnhub.Client(api_key="c3l3vkqad3idu4kfrh1g")
            self.__income_statement = fin_doc.Income_Statement(self.__ticker)
            self.__cash_flow = fin_doc.Cash_Flow(self.__ticker)
            self.__balance_sheet = fin_doc.Balance_Sheet(self.__ticker)
            self.__comp_info = Company_Info(self)
            self.__stock_price = self.__comp_info.stock_price
            self.__comp_news = Market_Info(finnhub_client, self.__company_name)
        except KeyError:
            raise ValueError('Invalid ticker symbol')

    @property
    def company_info(self) -> Market_Info:
        return self.__comp_news       

    @property
    def ticker(self) -> yf.Ticker:
      return self.__ticker     

    @property
    def company_name(self) -> str:
        return self.__company_name       

    @property
    def stock_price(self) -> float:
        return self.__stock_price  
        
    @property    
    def income_statement_3y(self) -> fin_doc.Income_Statement:
        """ Returns the Income_Statement Object attribute of this instance

            Returns:
                Income_Statement() for this company
        """
        return self.__income_statement

    @property
    def cash_flow_3y(self) -> fin_doc.Cash_Flow:
        """ Returns the Cash_Flow Object attribute of this instance

            Returns:
                Cash_Flow() for this company
        """
        return self.__cash_flow

    @property
    def balance_sheet_3y(self) -> fin_doc.Balance_Sheet:
        """ Returns the Balance_Sheet Object attribute of this instance

            Returns:
                Balance_Sheet() for this company
        """
        return self.__balance_sheet 

    @property
    def capm_expected_return(self) -> float:
        """ Returns the result of the CAPM formula when applied to this company, assuming a 10 year span when looking at
            the risk-free rate of return and an annual return from the S&P 500 of 5.6%. Beta value obtained from yfinance ticker.

            Returns:
                CAPM formula result
        """
        return self._get_risk_free_rate_return(10) + (self.__get_beta_value() * (5.6 - self._get_risk_free_rate_return(10)))

    def current_ratio(self, *years : int) -> List[int]:
        """ Returns a list of each current ratio for each year provided. If no years provided, all available years will be 
            calculated

            Args:
                *years: Each year desired for a current_ratio calculation. Currently only available for 3 years, input the specific
                years desired.
            Returns:
                Current ratios for this company
        """
        return self._ratio_calculator(
            self.balance_sheet_3y.get_current_assets(years),
            self.balance_sheet_3y.get_current_liabilities(years))
        
    def gross_profit_percentage(self, *years : int) -> List[float]:
        """ Returns a list of each gross profit percentage for each year provided. If no years provided, all available years will be 
            calculated

            Args:
                *years: Each year desired for a gross profit percentage calculation. Currently only available for 3 years, 
                input the specific years desired.

            Raises:
                ValueError if the years provided are invalid. (Is raised by the methods called within this method)     
            Returns:
                Gross profit percentages for this company
        """
        return self._ratio_calculator(
            self.income_statement_3y.get_net_income(years),
            self.balance_sheet_3y.get_total_assets(years))

    def _ratio_calculator(self, numerator : List[int], denominator : List[int]) -> List[float]:
        """ Returns a list of ratios provided a list of numerators and list of denominators.

            Args:
                numerator: List of each numerator
                denominator: List of each denominator
            Raises:
                ValueError: If the length of the numerators provided does not equal the length of the provided denominators    
            Returns:
                List of ratios
        """
        ratio = []
        if len(numerator) != len(denominator):
            raise ValueError("Length of numerators must be the same as denominators")
        for i in range(0, len(numerator)):
            ratio.append(numerator[i]/denominator[i])
        return ratio    

    def _get_free_cash_flow(self, *years) -> List[float]:
        """ Returns a list of each free cash flow value of this company given the years desired. If no years are inputted
            all years available are returned. Currently only 3 years are available.

            Args:
                years: The years desired for information regarding free cash flow
            Raises:
                ValueError: If the length of the numerators provided does not equal the length of the provided denominators    
            Returns:
                List of ratios
        """
        return self.get_cash_flow.get_free_cash_flow(years)     

    def _get_risk_free_rate_return(self, year: int) -> float:
        """ Returns the risk free rate of return of the past given years. Ex. past 5,10, or 30 years.

            Args:
                years: The past period of time which the risk free rate will be determined
            Raises:
                ValueError: If the past period of time provided is not 5,10, or 30, as those are the only available periods  
            Returns:
                Risk free rate of return float
        """
        valid_years = {5,10,30}
        market_object = Market()
        if year not in valid_years:
            raise ValueError('Year must be one of %r' % valid_years)
        if year is 5:
            return market_object.get_5_year_treasury_yield - float(market_object.get_5_year_inflation_rate)
        elif year is 10:
            return market_object.get_10_year_treasury_yield - float(market_object.get_10_year_inflation_rate)
        elif year is 30:
            return market_object.get_30_year_treasury_yield - float(market_object.get_30_year_inflation_rate)

    def __get_beta_value(self):
        """ Returns a list of each free cash flow value of this company given the years desired. If no years are inputted
            all years available are returned. Currently only 3 years are available.

            Args:
                years: The years desired for information regarding free cash flow
            Raises:
                ValueError: If the length of the numerators provided does not equal the length of the provided denominators    
            Returns:
                List of ratios
        """
        return self.__comp_info.beta  
        
           
class Market:
    def __init__(self):
        finnhub_client = finnhub.Client(api_key="c3l3vkqad3idu4kfrh1g")
        self.market_info = Market_Info(finnhub_client, 'general')
        self.stocks_in_market = Market.get_all_companies()
        self.s_p_500 = Market.get_s_p_500_companies()

    @staticmethod  
    def get_5_year_treasury_yield():
        return yf.Ticker('^FVX').info['regularMarketPrice']

    @staticmethod
    def get_10_year_treasury_yield():
        return yf.Ticker('^TNX').info['regularMarketPrice']

    @staticmethod
    def get_30_year_treasury_yield():
        return yf.Ticker('^TYX').info['regularMarketPrice']

    @classmethod
    def _get_inflation_rate(self, url):
        r = requests.get(url)
        soup = bs(r.content, 'html.parser')
        ans = soup.select_one('span.series-meta-observation-value')
        return ans.text

    @staticmethod
    def get_5_year_inflation_rate():
        return Market._get_inflation_rate('https://fred.stlouisfed.org/series/T5YIE')

    @staticmethod
    def get_10_year_inflation_rate():
        return Market._get_inflation_rate('https://fred.stlouisfed.org/series/T10YIE')

    @staticmethod
    def get_30_year_inflation_rate():
        return Market._get_inflation_rate('https://fred.stlouisfed.org/series/T30YIEM')

    @staticmethod
    def get_s_p_500_companies():
        url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies#S&P_500_component_stocks'    
        df = pd.read_html(url)[0]
        return df['Symbol'].values.tolist()

    @staticmethod
    def get_all_companies():
        companies = {}
        all_companies = []
        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        driver = webdriver.Chrome('/Users/frankisaacson/downloads/chromedriver 2', options=options)
        url = 'https://assetdash.com/largest-companies?'
        driver.get(url)
        for j in range(1,38):
            time.sleep(.25)
            content = driver.page_source
            soup = bs(content, 'html.parser')
            tags = soup.find_all('td')
            i = 4
            while i < len(tags):
                stock = Company(tags[i].text, tags[i+1].text, tags[i+2].text)
                all_companies.append(stock)
                companies.update({tags[i].text: [tags[i+1].text, tags[i+2].text]})
                i+=11
            button = driver.find_elements_by_class_name('ButtonTertiary-oygnqq-0.ButtonArrow__Button-vkbpol-0.cVYnmK.fnfpCw')
            ActionChains(driver).move_to_element(button[1]).click(button[1]).perform()
        driver.quit()
        return companies    


# Stock candles
# res = finnhub_client.stock_candles('AAPL', 'D', 1590988249, 1591852249)
# print(res['c'])

# Aggregate Indicators
# print(finnhub_client.aggregate_indicator('AAPL', 'D'))

# Basic financials
#company_1 = Company('PENN')
#company_1.setup_company()
