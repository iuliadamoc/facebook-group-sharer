import os

def detect_chrome_profiles(chrome_user_data_dir):
    profiles = []
    for item in os.listdir(chrome_user_data_dir):
        path = os.path.join(chrome_user_data_dir, item)
        # detectăm doar foldere valide
        if os.path.isdir(path) and (
            item.startswith("Profile") or item == "Default"
        ):
            profiles.append(item)
    return profiles
