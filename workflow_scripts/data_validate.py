import pandas as pd
import logging
import json
from packaging.version import Version
logging.basicConfig(filename="workflow_scripts/readme.md", level=logging.INFO)


valid_group = []


def validate_matches():
    # Load the data
    matches = pd.read_csv('data/epic7_match_history.csv')

    # Group by match number
    match_group = matches.groupby('Match Number')
    invalid_matches = []
    for match, group in match_group:
        if group['Pick Order'].nunique() != 10:
            logging.error(f'Removing: Match {match} does not have 10 heroes!\n')
            invalid_matches.append(match)

        characters_used = set()
        for i in range(1, 11):
            pick = group[group['Pick Order'] == i]
            if not pick.empty:
                current_char = pick['Hero'].values[0]
                if current_char in characters_used:
                    logging.error(f'Removing: Match {match} has a duplicate character!\n')
                    invalid_matches.append(match)
                    break

                characters_used.add(current_char)

        if group[group['Team'] == 'My Team']['Team'].value_counts().values[0] != 5 or\
                group[group['Team'] == 'Enemy Team']['Team'].value_counts().values[0] != 5:
                    logging.error(f'Removing: Match {match} does not have 5 characters on each teams!\n')
                    invalid_matches.append(match)

    #now save the valid groups only
    matches = matches[~matches['Match Number'].isin(invalid_matches)]
    matches.to_csv('data/epic7_match_history.csv', index=False)

print('Running validation checks!')
open('workflow_scripts/readme.md', 'w').close()

logging.info('Validating matches...\n')
validate_matches()
logging.info('Validating matches complete!\n')

# Update versions.json
with open('versions.json', 'r+') as f:
    data = json.load(f)
    current_version = data['data_version']
    current_version_obj = Version(current_version)
    current_version_list = list(current_version_obj.release)
    current_version_list[-1] += 1
    data['data_version'] = '.'.join(map(str, current_version_list))
    print(data)
    f.seek(0)
    json.dump(data, f)
    f.truncate()