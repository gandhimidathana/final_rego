import os
import csv
import time
from flask import send_file
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import undetected_chromedriver as uc

def process_nt(filepath):
    OUTPUT_FOLDER = 'output'
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36")
    service = Service("chromedriver")
    driver = uc.Chrome(headless=True)
    driver = webdriver.Chrome(service=service, options=options)
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    driver.get("https://nt.gov.au/driving/rego/existing-nt-registration/rego-check")

    time.sleep(0.1)
    wait = WebDriverWait(driver, 20)
    output_rows = [["Input Rego", "Plate", "Status", "Expiry", "Make", "Model"]]

    with open(filepath, "r") as f:
        rego_list = [line.strip() for line in f if line.strip()]

    for rego in rego_list:
        try:
            print(f"[>] Checking: {rego}")
            input_box = wait.until(EC.presence_of_element_located((By.ID, "rego")))
            input_box.clear()
            input_box.send_keys(rego)

            search_btn = wait.until(EC.element_to_be_clickable((By.ID, "search")))
            search_btn.click()

            wait.until(EC.presence_of_element_located((By.ID, "search-result")))
            time.sleep(2)

            def get_text(label):
                try:
                    return driver.find_element(By.XPATH, f"//p[strong[text()='{label}']]/following::p[1]").text.strip()
                except:
                    return "-"

            plate = rego
            make = get_text("Make")
            model = get_text("Model & Year")
            status = get_text("Status")
            expiry = get_text("Expiry")

            output_rows.append([rego, plate, status, expiry, make, model])

        except Exception as e:
            print(f"[!] Error for {rego}: {e}")
            output_rows.append([rego, rego, "-", "-", "-", "-", "Error"])

    driver.quit()

    output_file = os.path.join(OUTPUT_FOLDER, "result.csv")
    with open(output_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(output_rows)

    return output_file  