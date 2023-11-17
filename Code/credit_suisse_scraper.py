import sys, time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import string
import pandas as pd

# Parameters
driver = webdriver.Firefox()
wait = WebDriverWait(driver, 30)

DATA_FOLDER = "../Data/"
LINK = "https://derivative.credit-suisse.com/"
DERIVATIVE_SUBLINK = "ch/ch/en/detail/outperformance-bonus-certificate-euro-stoxx-50/CH1149494077/114949407"
DISCLAIMER_SUBLINK = "/ch/ch/en/disclaimer"
SLEEP_SECONDS = 300

# Visit page - Disclaimer pops up
driver.get(LINK+DERIVATIVE_SUBLINK)

# Click on 'Reject all cookies' button
wait.until(EC.presence_of_element_located((By.ID, "onetrust-reject-all-handler")))
onetrust_reject_all_button = driver.find_element(By.ID, "onetrust-reject-all-handler")
onetrust_reject_all_button.click()
time.sleep(1)

# Click on accept disclaimer button - Redirects to derivative page
disclaimer_accept_btn = driver.find_element(By.CLASS_NAME, "disclaimer-accept")
disclaimer_accept_btn.click()

# Iterate through all scripts on page
wait.until(EC.presence_of_element_located((By.CLASS_NAME, "amcharts-chart-div")))
time.sleep(0.5) # in case charts don't load

# JavaScript code to extract data from AmCharts v3.20.17
SCRIPT = """
var dataProviders = [];
var currObject = {};
for (const chart of AmCharts.charts)
{
    if (chart.type == "stock")
    {
        currObject.instrument_name = chart.mainDataSet.title;
    }
    else if (chart.type == "serial")
    {
        if ('instrument_name' in currObject)
        {
            currObject.data_provider = chart.dataProvider;
            dataProviders.push(currObject);
            currObject = {};
        }
    }
}
return dataProviders;
"""
valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
datasets = driver.execute_script(SCRIPT)
for dataset in datasets:
    instrument_name = "".join(x for x in dataset["instrument_name"] if x in valid_chars)
    instrument_filename = instrument_name.replace(" ", "_") + ".csv"
    print(f"Found {instrument_name}")

    instrument_data = []
    for data_point in dataset["data_provider"]:
        date = data_point['date'] # Takes the format of an ISO 8601 string
        value = data_point['value']
        instrument_data.append(data_point)

    # Save data to CSV using Pandas DataFrame after parsing ISO 8601 date string
    instrument_df = pd.DataFrame(instrument_data, columns=["date", "value"])
    instrument_df['date'] = pd.to_datetime(instrument_df['date']).dt.tz_convert(None)
    instrument_df.to_csv(f"{DATA_FOLDER}/{instrument_filename}", index=False)
    print(f"- Extracted to {DATA_FOLDER}/{instrument_filename}\n")
print("If any instrument is not included, please re-run the script.")
driver.close()
