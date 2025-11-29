import time
import random
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# ==========================================
# USER CONFIG
# ==========================================

POST_URL = "https://www.facebook.com/anca.borsaru1/"
DELAY_SECONDS = 40
GROUPS_FILE = "groups.txt"
RETRY_COUNT = 3

# ==========================================
# LOGGING SETUP
# ==========================================

logging.basicConfig(
    filename="log_share.txt",
    filemode="a",
    format="%(asctime)s — %(levelname)s — %(message)s",
    level=logging.INFO,
)

def log_console(level, message):
    colors = {
        "info": "\033[94m",
        "success": "\033[92m",
        "warning": "\033[93m",
        "error": "\033[91m",
    }
    reset = "\033[0m"
    print(f"{colors.get(level, '')}{message}{reset}")

# ==========================================
# START BROWSER
# ==========================================

options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

# ==========================================
# LOGIN FACEBOOK
# ==========================================

log_console("info", "\nDeschid Facebook...")
driver.get("https://www.facebook.com")

input("\n📌 Loghează-te în browser și APASĂ ENTER în VS Code când ești logată... ")

# ==========================================
# LOAD GROUPS
# ==========================================

with open(GROUPS_FILE, "r", encoding="utf-8") as f:
    groups = [line.strip() for line in f.readlines() if line.strip()]

log_console("info", "\n📌 Grupuri încărcate:")
for g in groups:
    print(" -", g)

# ==========================================
# SHARE FUNCTION
# ==========================================

def try_share_once(group_name):
    driver.get(POST_URL)
    time.sleep(random.uniform(2, 4))

    # CLICK SHARE - versiunea TA, care mergea
    try:
        share_parent = driver.find_element(
            By.XPATH, "//div[@data-ad-rendering-role='share_button']/parent::div"
        )
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", share_parent)
        time.sleep(0.6)
        driver.execute_script("arguments[0].click();", share_parent)
        time.sleep(1.2)
    except Exception as e:
        return False, f"Eroare la click Share — {e}"

    # CLICK "Share to a group" - versiunea TA, care MERGEA
    try:
        button_group = driver.find_element(
            By.XPATH, "//span[contains(text(), 'Share to a group')]/ancestor::div[3]"
        )
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", button_group)
        time.sleep(0.3)
        driver.execute_script("arguments[0].click();", button_group)
        time.sleep(2)
    except Exception as e:
        return False, f"Nu pot apăsa 'Share to a group' — {e}"

    # CĂUTARE GRUP
    try:
        search_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "//input[@placeholder='Search for groups' or @placeholder='Caută grupuri']")
            )
        )
        search_box.clear()
        search_box.send_keys(group_name)
        time.sleep(1.5)
    except Exception as e:
        return False, f"Nu găsesc căsuța de căutare — {e}"

    # SELECTEAZĂ EXACT GRUPUL DUPĂ NUME — FIX FINAL
    try:
        exact_group = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((
                By.XPATH,
                f"//span[normalize-space(text())='{group_name}']/ancestor::div[@role='button']"
            ))
        )
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", exact_group)
        time.sleep(0.5)
        driver.execute_script("arguments[0].click();", exact_group)
        time.sleep(2)

    except Exception:
        return False, "Nu găsesc grupul exact — apare dar nu e clickable"

    # CLICK POST
    try:
        post_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((
                By.XPATH,
                "//span[text()='Post' or text()='Postează']/ancestor::div[@role='button']"
            ))
        )
        driver.execute_script("arguments[0].click();", post_btn)
        return True, "Succes"
    except Exception as e:
        return False, f"Nu găsesc butonul Post — {e}"

# ==========================================
# RETRY LOGIC
# ==========================================

def share_to_group(group_name):
    log_console("info", f"\n📌 Share către: {group_name}")
    logging.info(f"Încep share către: {group_name}")

    for attempt in range(1, RETRY_COUNT + 1):
        success, message = try_share_once(group_name)

        if success:
            log_console("success", f"✔ Reușit — {group_name}")
            logging.info(f"✔ Succes: {group_name}")
            return True

        log_console("warning", f"❌ Eroare ({attempt}/{RETRY_COUNT}) — {message}")
        logging.warning(f"Eroare la {group_name}: {message}")
        time.sleep(3)

    log_console("error", f"⛔ Eșuat definitiv — {group_name}")
    logging.error(f"⛔ Eșuat definitiv: {group_name}")
    return False

# ==========================================
# SHARE LOOP
# ==========================================

for group in groups:
    share_to_group(group)
    log_console("info", f"⏳ Aștept {DELAY_SECONDS} secunde înainte de următorul share...")
    time.sleep(DELAY_SECONDS)

log_console("success", "\n🎉 GATA! Toate share-urile au fost procesate.")
logging.info("=== Script finalizat ===")

driver.quit()
