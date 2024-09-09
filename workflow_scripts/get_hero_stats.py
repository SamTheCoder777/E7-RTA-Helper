import pandas as pd
from collections import defaultdict

# Load your CSV data into a DataFrame
df = pd.read_csv('data/epic7_match_history.csv')

# Function to calculate winrates, counters, picks, and counters against
def calculate_winrates_counters_and_counters_against(df):
    # Initialize dictionaries to store hero statistics
    hero_stats = defaultdict(lambda: {'total_matches': 0, 'total_wins': 0, 'counters': defaultdict(int), 'picked_with': defaultdict(int), 'countered_by': defaultdict(int)})

    # Group by 'Match Number' to efficiently handle enemy and team heroes
    match_groups = df.groupby('Match Number')
    
    # Iterate through each match
    for match_number, match_data in match_groups:
        my_team_heroes = match_data[match_data['Team'] == 'My Team']['Hero'].values
        enemy_team_heroes = match_data[match_data['Team'] == 'Enemy Team']['Hero'].values
        
        # Precompute win condition
        win_mask = (match_data['Match Result'] == 'Win') & (match_data['Team'] == 'My Team')
        
        for hero in my_team_heroes:
            hero_stats[hero]['total_matches'] += 1
            if win_mask.any():
                hero_stats[hero]['total_wins'] += 1

            # Update picked_with for allies and counters for enemies
            for ally in my_team_heroes:
                if ally != hero:
                    hero_stats[hero]['picked_with'][ally] += 1

            for enemy in enemy_team_heroes:
                hero_stats[hero]['counters'][enemy] += 1
                hero_stats[enemy]['countered_by'][hero] += 1
    
    # Calculate winrates, counters, picked_with, countered_by, and pick rates per hero
    winrates = {}
    counters = {}
    picked_with = {}
    countered_by = {}
    pick_rates = {}

    total_matches = df['Match Number'].nunique()

    for hero, stats in hero_stats.items():
        if stats['total_matches'] > 0:
            winrates[hero] = stats['total_wins'] / stats['total_matches']
        else:
            winrates[hero] = -1
        
        pick_rates[hero] = stats['total_matches'] / total_matches
        
        # Get top 3 counters (most wins against)
        counters[hero] = sorted(stats['counters'].items(), key=lambda x: -x[1])[:3]
        counters[hero] += [(-1, -1)] * (3 - len(counters[hero]))
        
        # Get top 3 best picks (most picked with)
        picked_with[hero] = sorted(stats['picked_with'].items(), key=lambda x: -x[1])[:3]
        picked_with[hero] += [(-1, -1)] * (3 - len(picked_with[hero]))
        
        # Get top 3 countered by (most countered by)
        countered_by[hero] = sorted(stats['countered_by'].items(), key=lambda x: -x[1])[:3]
        countered_by[hero] += [(-1, -1)] * (3 - len(countered_by[hero]))
    
    # Create a DataFrame to store all data
    data = []
    for hero in winrates:
        data.append({
            'Hero': hero,
            'Winrate': winrates[hero],
            'Pick Rate': pick_rates[hero],
            'Counter1': counters[hero][0][0],
            'Counter1_Wins': counters[hero][0][1],
            'Counter2': counters[hero][1][0],
            'Counter2_Wins': counters[hero][1][1],
            'Counter3': counters[hero][2][0],
            'Counter3_Wins': counters[hero][2][1],
            'Pick1': picked_with[hero][0][0],
            'Pick1_Count': picked_with[hero][0][1],
            'Pick2': picked_with[hero][1][0],
            'Pick2_Count': picked_with[hero][1][1],
            'Pick3': picked_with[hero][2][0],
            'Pick3_Count': picked_with[hero][2][1],
            'CounteredBy1': countered_by[hero][0][0],
            'CounteredBy1_Count': countered_by[hero][0][1],
            'CounteredBy2': countered_by[hero][1][0],
            'CounteredBy2_Count': countered_by[hero][1][1],
            'CounteredBy3': countered_by[hero][2][0],
            'CounteredBy3_Count': countered_by[hero][2][1]
        })
    
    df_all_info = pd.DataFrame(data)
    
    return df_all_info

# Calculate all information
df_all_info = calculate_winrates_counters_and_counters_against(df)

# Save to CSV
df_all_info.to_csv('data/epic7_hero_stats.csv', index=False)

# Print confirmation
print("Data saved successfully.")