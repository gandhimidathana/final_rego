import os
import csv
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

def process_qld(filepath):
    OUTPUT_FOLDER = 'output'
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--headless=new")
    service = Service("chromedriver")
    driver = webdriver.Chrome(service=service, options=options)
    driver.get("https://www.service.transport.qld.gov.au/checkrego/application/TermAndConditions.xhtml")

    wait = WebDriverWait(driver, 20)
    output_rows = [["Registration Number", "VIN", "Description", "Purpose", "Status", "Expiry"]]

    with open(filepath, "r") as f:
        rego_list = [line.strip() for line in f if line.strip()]

    for rego in rego_list:
        try:
            print(f"[>] Checking: {rego}")

            # Accept Terms and Conditions
            try:
                accept_btn = wait.until(EC.element_to_be_clickable((By.ID, "tAndCForm:confirmButton")))
                driver.execute_script("arguments[0].click();", accept_btn)
                time.sleep(1)
            except:
                print("[-] Terms button not found or already accepted")

            # Enter rego
            input_box = wait.until(EC.presence_of_element_located((By.ID, "vehicleSearchForm:plateNumber")))
            input_box.clear()
            input_box.send_keys(rego)

            # Search
            search_btn = wait.until(EC.element_to_be_clickable((By.ID, "vehicleSearchForm:confirmButton")))
            search_btn.click()

            # Wait for result form
            wait.until(EC.presence_of_element_located((By.ID, "j_id_61")))

            def get_info(label):
                try:
                    dt_element = driver.find_element(By.XPATH, f"//dt[normalize-space(text())='{label}']")
                    dd_element = dt_element.find_element(By.XPATH, "following-sibling::dd[1]")
                    return dd_element.text.strip()
                except:
                    return "-"

            rego_number = get_info("Registration number") or rego
            vin = get_info("Vehicle Identification Number (VIN)")
            desc = get_info("Description")
            purpose = get_info("Purpose of use")
            status = get_info("Status")
            expiry = get_info("Expiry")

            output_rows.append([rego_number, vin, desc, purpose, status, expiry])

            # Click Search Again
            try:
                again_btn = wait.until(EC.element_to_be_clickable((By.ID, "j_id_61:searchAgain")))
                again_btn.click()
                wait.until(EC.presence_of_element_located((By.ID, "vehicleSearchForm:plateNumber")))
                time.sleep(1)
            except:
                print("[!] Could not return to search page, reloading")
                driver.get("https://www.service.transport.qld.gov.au/checkrego/application/TermAndConditions.xhtml")
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
