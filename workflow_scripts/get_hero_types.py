import pandas as pd
import csv

hero = pd.read_csv('data/hero_code_to_name.csv')
hero_details = pd.read_csv('data/hero_types.csv')

hero = hero.merge(hero_details, left_on='code', right_on='code', how='left')

# Check where Type is missing and fill with 'Unknown'
hero['type'] = hero['type'].fillna('"[\'Unknown\']"')
# Drop name_y and rename name_x to name
hero = hero.drop(columns=['name_y'])
hero = hero.rename(columns={'name_x': 'name'})

# Function to ensure correct quoting
def ensure_quotes(x):
    x = x.strip()  # Remove any leading/trailing whitespace
    if not x.startswith('"') and not x.endswith('"'):
        x = '"' + x + '"'
    return x

# Apply the function to the 'type' column
hero['type'] = hero['type'].apply(ensure_quotes)
hero.to_csv('data/hero_types.csv', index=False, quoting=csv.QUOTE_MINIMAL)

# open csv as just a file and replace all """ with " and save it back
with open('data/hero_types.csv', 'r') as f:
    data = f.read()
    data = data.replace('"""', '"')
    with open('data/hero_types.csv', 'w') as f:
        f.write(data)

# Print names of heroes with missing types
print('Heroes with missing types:')
print(hero[hero['type'] == '"[\'Unknown\']"']['name'].values)