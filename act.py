import os
import csv
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

def process_act(filepath):
    OUTPUT_FOLDER = 'output'
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--headless=new")  
    service = Service("chromedriver")  
    driver = webdriver.Chrome(service=service, options=options)
    driver.get("https://rego.act.gov.au/regosoawicket/public/reg/FindRegistrationPage?0")

    wait = WebDriverWait(driver, 20)
    output_rows = [[
        "Plate Number", "Make", "Model", "Colour", "Manufacture Date",
        "VIN", "Engine Number", "GVM", "Tare Mass", "Stolen VIN",
        "CO2 Emissions", "Stolen Plate", "Stolen Engine", "Reg Status",
        "No. of Operators"
    ]]

    with open(filepath, "r") as f:
        rego_list = [line.strip() for line in f if line.strip()]

    for rego in rego_list:
        try:
            print(f"[>] Checking: {rego}")

            # Enter plate
            input_box = wait.until(EC.presence_of_element_located((By.ID, "plateNumber")))
            input_box.clear()
            input_box.send_keys(rego)

            # Click checkbox
            checkbox = wait.until(EC.element_to_be_clickable((By.ID, "privacyCheck")))
            checkbox.click()
            time.sleep(0.5)

            # Click next
            next_btn = wait.until(EC.element_to_be_clickable((By.ID, "id3")))
            next_btn.click()

            # Try to click the first vehicle result (e.g., HOLDEN)
            try:
                vehicle_option = wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'HOLDEN')]"))
                )
                vehicle_option.click()
                time.sleep(0.5)
            except Exception as e:
                print(f"[✖] No vehicle found for rego {rego}, skipping to next.")
                output_rows.append([rego] + ["-"] * 14)

                # Redirect and click "< Previous"
                driver.get("https://rego.act.gov.au/regosoawicket/public/reg/FindRegistrationPage?0")
                try:
                    previous_btn = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.ID, "id7"))
                    )
                    previous_btn.click()
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.ID, "plateNumber"))
                    )
                    time.sleep(1)
                except:
                    print("[!] Couldn't return to start after invalid rego.")
                continue  # Move to next rego

            # Extract vehicle data
            def get_val(id):
                try:
                    return driver.find_element(By.ID, id).get_attribute("value").strip()
                except:
                    return "-"

            plate = get_val("plateNumber")
            make = get_val("vehicleMake")
            model = get_val("vehicleModel")
            colour = get_val("vehicleColour")
            manu_date = get_val("manufacturingDate")
            vin = get_val("vinNumber")
            engine = get_val("engineNumber")
            gvm = get_val("gvm")
            tare = get_val("tareMass")
            stolen_vin = get_val("stolenIndicator")
            co2 = get_val("gvRating")
            stolen_plate = get_val("stolenPlateIndicator")
            stolen_engine = get_val("stolenEngineIndicator")
            reg_status = get_val("regStatus")
            operators = get_val("operators")

            output_rows.append([
                plate, make, model, colour, manu_date,
                vin, engine, gvm, tare, stolen_vin,
                co2, stolen_plate, stolen_engine, reg_status,
                operators
            ])

            # Redirect to home and click "< Previous"
            print("[↩] Redirecting to home page...")
            driver.get("https://rego.act.gov.au/regosoawicket/public/reg/FindRegistrationPage?0")

            try:
                previous_btn = WebDriverWait(driver, 15).until(
                    EC.element_to_be_clickable((By.ID, "id7"))
                )
                previous_btn.click()
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, "plateNumber"))
                )
                time.sleep(1)
                print("[✔] Returned to plate input form.")
            except Exception as e:
                print(f"[!] Failed to return to start after valid rego: {e}")

        except Exception as e:
            print(f"[!] Unexpected error for {rego}: {e}")
            output_rows.append([rego] + ["-"] * 14)

    driver.quit()

    output_file = os.path.join(OUTPUT_FOLDER, "result.csv")
    with open(output_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(output_rows)

    return output_file  
