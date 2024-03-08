from selenium import webdriver
import chromedriver_autoinstaller
chromedriver_autoinstaller.install()
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import pandas as pd
timeout_duation = 60


def write_to_csv(all_information=None):
    df = pd.DataFrame(all_information)
    df.to_csv('hspcs_codes.csv',index=False)

def extract_data():
    chrome_options = Options()
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(options=chrome_options)

    # Open the main website

    driver.get('https://www.hcpcsdata.com/Codes')
    main_body = WebDriverWait(driver, 300).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'tbody'))
    )

    # Get all the rows in the table body
    all_information =[]

    first_page_rows = driver.execute_script("""
        const rows = Array.from(document.querySelectorAll('tbody tr'));
        return rows.map(row => {
            const columns = Array.from(row.querySelectorAll('td'));
            const group = columns[0].textContent.trim();
            const category = columns[2].textContent.trim();
            const secondaryLink = columns[0].querySelector('a').href;
            return { group, category, secondaryLink };
        });
    """)


    for data in first_page_rows:
        driver.get(data.get("secondaryLink"))
        secondary_body = WebDriverWait(driver, 300).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'tbody'))
        )

        secondary_rows = driver.execute_script("""
            const rows = Array.from(document.querySelectorAll('tbody tr'));
            return rows.map(row => {
                const columns = Array.from(row.querySelectorAll('td'));
                const code = columns[0].textContent.trim();
                const longDescription = columns[1].textContent.trim();
                const tertiaryLink = columns[0].querySelector('a') ? columns[0].querySelector('a').href : null;
                return { code, longDescription, tertiaryLink };
            });
        """)

        for second_data in secondary_rows:
            new_data = {**data, **second_data}
            if new_data.get('tertiaryLink'):
                driver.get(new_data.get("tertiaryLink"))
                tertiary_body = WebDriverWait(driver, 300).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'tbody'))
                )

                short_description = driver.execute_script("""
                    const row = document.querySelector('tbody tr');
                    const columns = Array.from(row.querySelectorAll('td'));
                    return columns[1].textContent.trim();
                """)

                new_data['shortDescription'] = short_description
                del new_data['secondaryLink'], new_data['tertiaryLink']
            all_information.append(new_data)
    driver.quit()
    return all_information
if __name__=="__main__":
    all_information = extract_data()
    write_to_csv(all_information=all_information)
