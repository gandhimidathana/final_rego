import os
import csv
import time
import traceback
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
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36")

    # Set up ChromeDriver
    print("[Debug] Launching Chrome")
    service = Service("chromedriver")
    driver = webdriver.Chrome(service=service, options=options)
    
    print("[Debug] Chrome Capabilities:")
    print(driver.capabilities)

    try:
        driver.get("https://nt.gov.au/driving/rego/existing-nt-registration/rego-check")
        print("[Debug] NT site loaded")
        print("[Debug] Page Source (first 1000 chars):")
        print(driver.page_source[:1000])

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
                print("[Debug] Entered rego")

                search_btn = wait.until(EC.element_to_be_clickable((By.ID, "search")))
                search_btn.click()
                print("[Debug] Clicked search")

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
                print(f"[✔] Done: {rego} → {status}, {expiry}, {make}, {model}")

            except Exception as e:
                print(f"[!] Error for {rego}: {e}")
                traceback.print_exc()
                output_rows.append([rego, rego, "-", "-", "-", "-", "Error"])

        driver.quit()

        output_file = os.path.join(OUTPUT_FOLDER, "result.csv")
        with open(output_file, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerows(output_rows)

        print("[✅] Finished processing all regos.")
        return output_file

    except Exception as e:
        print(f"[!] Fatal error: {e}")
        traceback.print_exc()
        driver.quit()
        return os.path.join(OUTPUT_FOLDER, "result.csv")
