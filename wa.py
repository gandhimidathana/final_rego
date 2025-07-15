
import os
import csv
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

def process_wa(filepath):
    OUTPUT_FOLDER = 'output'
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--headless=new")
    service = Service("chromedriver") 
    driver = webdriver.Chrome(service=service, options=options)
    driver.get("https://online.transport.wa.gov.au/webExternal/registration/?0")

    wait = WebDriverWait(driver, 20)
    output_rows = [["Plate", "Make", "Model", "Year", "Colour", "Expiry"]]

    with open(filepath, "r") as f:
        rego_list = [line.strip() for line in f if line.strip()]

    for rego in rego_list:
        try:
            print(f"[>] Checking: {rego}")
            input_box = wait.until(EC.presence_of_element_located((By.ID, "id1")))
            input_box.clear()
            input_box.send_keys(rego)
            time.sleep(1)

            search_btn = wait.until(EC.element_to_be_clickable((By.ID, "id4")))
            search_btn.click()
            time.sleep(3)

            def get_cell_value(label):
                try:
                    xpath = f"//td[@class='label' and normalize-space(text())='{label}']/following-sibling::td/span"
                    return driver.find_element(By.XPATH, xpath).text.strip()
                except:
                    return "-"

            plate = get_cell_value("Plate Number") or rego
            make = get_cell_value("Make")
            model = get_cell_value("Model")
            year = get_cell_value("Year")
            colour = get_cell_value("Colour")
            expiry = get_cell_value("This vehicle licence expires on")

            output_rows.append([plate, make, model, year, colour, expiry])

            driver.get("https://online.transport.wa.gov.au/webExternal/registration/?0")
            time.sleep(2)

        except Exception as e:
            print(f"[!] Error for {rego}: {e}")
            output_rows.append([rego] + ["-"] * 5)

    driver.quit()

    output_file = os.path.join(OUTPUT_FOLDER, "result.csv")
    with open(output_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(output_rows)

    return output_file  
