def temporal(year):
    if year in {2021,2022}: return 'train'
    if year==2023: return 'dev'
    if year==2024: return 'test'
    if year==2025: return 'future_holdout'
    return 'review'
