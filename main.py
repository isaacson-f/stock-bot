from flask import Flask, request, escape, render_template

import Company as code

app = Flask(__name__)

@app.route("/")
def index():
    market = code.Market()
    headlines1 = market.market_info.get_story_headlines(10)
    links1 = market.market_info.get_url(10)
    dates1 = market.market_info.get_story_datetimes(10)
    return render_template("index.html", headlines = headlines1, links=links1, size=len(headlines1), dates=dates1)


@app.route("/company")
def company():
    company = request.args.get("company", "")
    if company:
        setup_company = info_from(company)
        stock_price1 = setup_company.stock_price
        company_ticker = setup_company.company_name
        headlines1 = setup_company.company_info.get_story_headlines(10)
        links1 = setup_company.company_info.get_url(10)
        dates1 = setup_company.company_info.get_story_datetimes(10)
    else:
        stock_price1 = ""
        company_ticker = ""
        headlines1=[]
        links1 =[]
        dates1 = []
    return  render_template("company.html", stock_price = stock_price1, 
    ticker = company_ticker, headlines = headlines1, links=links1, size=len(headlines1), dates=dates1)    

def info_from(company) -> code.Company:
    """Get companies info."""
    new_comp = code.Company(company)
    try:
        new_comp.setup_company()
    except ValueError:
        return "Invalid Company" 
    return new_comp


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)        
