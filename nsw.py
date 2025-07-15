import os
import csv
import time
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def process_nsw(filepath):
    OUTPUT_FOLDER = 'output'
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    options = uc.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36")

    driver = uc.Chrome(options=options)
    wait = WebDriverWait(driver, 20)
    driver.get("https://check-registration.service.nsw.gov.au/frc?isLoginRequired=true")

    # ✅ Ensure page is ready before loop starts
    try:
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, "plateNumberInput")))
        print("[✔] NSW page loaded")
    except Exception as e:
        print("[!] NSW page did not load properly: ", e)
        driver.quit()
        return

    output_rows = [[
        "Plate", "Description", "VIN", "Expiry",
        "Make", "Model", "Variant", "Colour", "Shape",
        "Manufacture Year", "Tare Weight", "GVM",
        "Concession", "Condition Codes"
    ]]

    with open(filepath, "r") as f:
        rego_list = [line.strip() for line in f if line.strip()]

    for rego in rego_list:
        try:
            print(f"[>] Checking: {rego}")

            # Accept checkbox
            try:
                checkbox = wait.until(EC.presence_of_element_located((By.ID, "termsAndConditions")))
                driver.execute_script("arguments[0].click();", checkbox)
                time.sleep(1)
            except Exception as e:
                print("[-] Checkbox not found or already accepted")

            # Plate input
            input_box = wait.until(EC.presence_of_element_located((By.ID, "plateNumberInput")))
            input_box.clear()
            input_box.send_keys(rego)
            time.sleep(0.5)

            # Search button
            search_btn = wait.until(EC.element_to_be_clickable((By.ID, "id-2")))
            driver.execute_script("arguments[0].click();", search_btn)
            time.sleep(3)

            # Try extract main vehicle info
            try:
                plate = driver.find_element(By.CSS_SELECTOR, "h2.heading-2").text.strip()
                desc = driver.find_element(By.XPATH, "//p[contains(text(),'VIN/Chassis')]/preceding-sibling::p[1]").text.strip()
                vin = driver.find_element(By.XPATH, "//p[contains(text(),'VIN/Chassis')]").text.split(":")[-1].strip()
                expiry_el = driver.find_element(By.XPATH, "//strong[contains(text(),'Registration expires')]").text
                expiry = expiry_el.replace("Registration expires:", "").strip()
            except:
                plate = rego
                desc = vin = expiry = "-"

            # Extract more fields
            def get_info(label):
                try:
                    return driver.find_element(By.XPATH, f"//div[text()='{label}']/following-sibling::div[1]").text.strip()
                except:
                    return "-"

            make = get_info("Make")
            model = get_info("Model")
            variant = get_info("Variant")
            colour = get_info("Colour")
            shape = get_info("Shape")
            year = get_info("Manufacture year")
            tare = get_info("Tare weight")
            gvm = get_info("Gross vehicle mass")
            concession = get_info("Registration concession")
            condition = get_info("Condition codes")

            output_rows.append([
                plate, desc, vin, expiry,
                make, model, variant, colour, shape,
                year, tare, gvm, concession, condition
            ])

            # ✅ Return to start for next rego
            driver.get("https://check-registration.service.nsw.gov.au/frc?isLoginRequired=true")
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "plateNumberInput")))
            time.sleep(1)

        except Exception as e:
            print(f"[!] Error for {rego}: {e}")
            output_rows.append([rego] + ["-"] * 13)
            # Attempt to recover page
            driver.get("https://check-registration.service.nsw.gov.au/frc?isLoginRequired=true")
            time.sleep(2)

    driver.quit()

    output_file = os.path.join(OUTPUT_FOLDER, "result.csv")
    with open(output_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(output_rows)

    return output_file
