import time
import random
import logging
from dotenv import load_dotenv
import os
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

load_dotenv()

# PRELUĂM PROFILUL SELECTAT DIN GUI (argument linie de comandă)
if len(sys.argv) < 2:
    print("❌ Nu ai selectat niciun profil! Rulează din GUI!")
    sys.exit()

SELECTED_PROFILE = sys.argv[1]  # ex: "Profile 1"
CHROME_PROFILE = os.getenv("CHROME_PROFILE")

MESSAGE_TEXT = ""
if len(sys.argv) >= 2:  # dacă există mesaj
    MESSAGE_TEXT = sys.argv[2]

POST_URL = os.getenv("POST_URL")
DELAY_SECONDS = 20
GROUPS_FILE = f"userdata/{SELECTED_PROFILE}_groups.txt"
RETRY_COUNT = 3

if not os.path.exists(GROUPS_FILE):
    with open(GROUPS_FILE, "w", encoding="utf-8") as f:
        f.write("")  

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
options.add_argument(f"--user-data-dir={CHROME_PROFILE}")
options.add_argument(f"--profile-directory={SELECTED_PROFILE}")
options.add_argument("--start-maximized")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option("useAutomationExtension", False)

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

# ---- PATCH 1: pornim cu o pagină neutră ----
driver.get("chrome://newtab/")

time.sleep(1)

# ---- PATCH 2: forțăm încărcarea postării ----
driver.execute_script(f"window.location.href = '{POST_URL}';")

time.sleep(2)

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

    # CLICK SHARE BUTTON
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


    # -----------------------------------------------------------
    # ÎNCERCĂ DIRECT "Share to a group"
    # -----------------------------------------------------------
    found_direct_group = False

    try:
        direct_button = WebDriverWait(driver, 2).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//span[contains(text(),'Share to a group')]/ancestor::div[@role='button']")
            )
        )
        found_direct_group = True
    except:
        found_direct_group = False


    # -----------------------------------------------------------
    # 1️⃣ VARIANTA DIRECTĂ — fără More Options
    # -----------------------------------------------------------
    if found_direct_group:
        try:
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", direct_button)
            time.sleep(0.3)
            driver.execute_script("arguments[0].click();", direct_button)
            time.sleep(1.5)
        except Exception as e:
            return False, f"Nu pot apăsa direct Share to a group — {e}"

    else:
        # -----------------------------------------------------------
        # 2️⃣ CAUTĂ MORE OPTIONS
        # -----------------------------------------------------------
        try:
            more_options = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//span[contains(text(),'More options')]/ancestor::div[@role='button']")
                )
            )
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", more_options)
            time.sleep(0.4)
            driver.execute_script("arguments[0].click();", more_options)
            time.sleep(1.5)
        except Exception as e:
            return False, f"Nu găsesc More options — {e}"

        # -----------------------------------------------------------
        # 3️⃣ SHARE TO A GROUP DIN MENIU SECUNDAR
        # -----------------------------------------------------------
        try:
            direct_button = WebDriverWait(driver, 6).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//span[contains(text(),'Share to a group')]/ancestor::div[@role='button']")
                )
            )
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", direct_button)
            time.sleep(0.3)
            driver.execute_script("arguments[0].click();", direct_button)
            time.sleep(2)
        except Exception as e:
            return False, f"Nu găsesc Share to a group după More options — {e}"


    # -----------------------------------------------------------
    # 4️⃣ AȘTEAPTĂ SIGUR APARIȚIA SEARCH BOX (NO MATTER WHAT)
    # -----------------------------------------------------------

    search_box = None

    possible_search_xpaths = [
        "//input[@placeholder='Search for groups']",
        "//input[@placeholder='Caută grupuri']",
        "//label//input[contains(@class,'x1i10hfl')]",
        "//input[contains(@type,'text') and contains(@class,'x1i10hfl')]"
    ]

    # încearcă toate XPATH-urile
    for xpath in possible_search_xpaths:
        try:
            search_box = WebDriverWait(driver, 6).until(
                EC.presence_of_element_located((By.XPATH, xpath))
            )
            break
        except:
            pass

    if search_box is None:
        return False, "Nu apare search box după Share to a group — pagina nu s-a încărcat corect."

    # -----------------------------------------------------------
    # 5️⃣ CĂUTAREA GRUPULUI
    # -----------------------------------------------------------
    try:
        search_box.clear()
        search_box.send_keys(group_name)
        time.sleep(1.5)
    except:
        return False, "Nu pot scrie în search box."


    # -----------------------------------------------------------
    # 6️⃣ SELECTEAZĂ EXACT GRUPUL DUPĂ NUME
    # -----------------------------------------------------------
    try:
        exact_group = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, f"//span[normalize-space(text())='{group_name}']/ancestor::div[@role='button']")
            )
        )
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", exact_group)
        time.sleep(0.5)
        driver.execute_script("arguments[0].click();", exact_group)
        time.sleep(2)

    except Exception:
        return False, "Nu găsesc grupul exact — apare dar nu este clickable."

    # -----------------------------------------------------------
    # SCRIE MESAJUL ÎN CASETA DE TEXT (în dialogul Share)
    # -----------------------------------------------------------
    if MESSAGE_TEXT.strip():
        try:
            message_box = WebDriverWait(driver, 6).until(
                EC.presence_of_element_located((
                    By.XPATH,
                    "//div[@role='dialog']//div[@role='textbox']"
                ))
            )

            # folosim JavaScript pentru click pentru a evita overlay-ul
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", message_box)
            time.sleep(0.2)
            driver.execute_script("arguments[0].click();", message_box)
            time.sleep(0.2)

            message_box.send_keys(MESSAGE_TEXT)
            time.sleep(0.3)

        except Exception as e:
            return False, f"Nu pot scrie mesajul în caseta de text — {e}"


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
