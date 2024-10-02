import pandas as pd

def load_games_data(file_path):
    return pd.read_csv(file_path)

def load_games_metadata(file_path):
    return pd.read_json(file_path, lines=True)

def load_user_data(file_path):
    return pd.read_csv(file_path)

def load_reviews_data(file_path):
    return pd.read_csv(file_path)