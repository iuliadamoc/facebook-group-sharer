import time
import random
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# ==========================================
# CONFIG
# ==========================================

TEXT_MESSAGE = """🌻 Recomand cu încredere!
https://www.facebook.com/andreisamuelfotograf/posts/pfbid0SakHDEDXUQVC9CNWE3JWAxrwoxf3JCCCnPiyqnU4ZTQUdfjuNoc7U769pNAgWoavl
"""

GROUPS_FILE = "groups.txt"
DELAY_SECONDS = 30
RETRY_COUNT = 2

logging.basicConfig(
    filename="log_groups.txt",
    filemode="a",
    format="%(asctime)s — %(levelname)s — %(message)s",
    level=logging.INFO,
)

def log(msg):
    print(msg)
    logging.info(msg)

# ==========================================
# START BROWSER
# ==========================================

options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

# ==========================================
# LOGIN
# ==========================================

log("Deschid Facebook...")
driver.get("https://www.facebook.com")

input("\n📌 Loghează-te manual, apoi apasă ENTER aici... ")

# ==========================================
# LOAD GROUP IDS
# ==========================================

with open(GROUPS_FILE, "r") as f:
    groups = [g.strip() for g in f if g.strip()]

log("\n📌 Grupuri încărcate:")
for g in groups:
    print(" -", g)

# ==========================================
# POST FUNCTION
# ==========================================

def post_to_group(group_id):
    log(f"\n📌 Postez în grupul: {group_id}")

    for attempt in range(1, RETRY_COUNT + 1):
        try:
            # merge direct în grup
            driver.get(f"https://www.facebook.com/groups/{group_id}")
            time.sleep(5)

            # cautăm editorul de postare
            try:
                write_box = driver.find_element(
                    By.XPATH, "//div[@role='button' and contains(text(), \"Write something\")]"
                )
            except:
                write_box = driver.find_element(
                    By.XPATH, "//div[@role='button' and contains(text(), \"Scrie ceva\")]"
                )

            driver.execute_script("arguments[0].click();", write_box)
            time.sleep(3)

            # zona unde scriem postarea
            editor = driver.find_element(
                By.XPATH, "//div[@role='textbox']"
            )

            editor.send_keys(TEXT_MESSAGE)
            time.sleep(2)

            # buton Post
            try:
                post_btn = driver.find_element(
                    By.XPATH, "//span[text()='Post' or text()='Postează']/ancestor::div[@role='button']"
                )
            except:
                return False, "Nu găsesc butonul Post"

            driver.execute_script("arguments[0].click();", post_btn)

            log(f"✔ Postare reușită în grupul {group_id}")
            return True

        except Exception as e:
            log(f"❌ Eroare ({attempt}/{RETRY_COUNT}): {e}")
            time.sleep(3)

    log(f"⛔ Eșuat definitiv în {group_id}")
    return False

# ==========================================
# MAIN LOOP
# ==========================================

for group_id in groups:
    post_to_group(group_id)
    log(f"⏳ Aștept {DELAY_SECONDS} secunde...")
    time.sleep(DELAY_SECONDS)

log("\n🎉 GATA! Toate postările au fost trimise.")
driver.quit()
