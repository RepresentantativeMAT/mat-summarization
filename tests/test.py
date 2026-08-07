from pathlib import Path
import re

folder_path = Path('./data/input')

users = []

for item in folder_path.iterdir():
    if item.is_file():
        users.append(int(re.sub(r"\D", "", item.name)))

users.sort()
print(users)
