import os
import cloudpickle
from datetime import datetime
from app.utils.s3_utils import S3Ingestion
from app.data_loader import load_games_data, load_games_metadata
from app.preprocess import preprocess_games_data
from sklearn.neighbors import NearestNeighbors

class GameRecommender:
    def __init__(self, model, feature_matrix, df_games):
        self.model = model
        self.feature_matrix = feature_matrix
        self.df_games = df_games

    def recommend_games(self, app_id, n_recommendations=5):
        if n_recommendations <= 0:
            raise ValueError("O número de recomendações deve ser maior que zero.")

        try:
            game_index = self.df_games[self.df_games['app_id'] == app_id].index[0]
            game = self.feature_matrix.tocsr()[game_index:game_index+1]
        except IndexError:
            raise ValueError(f"Game with app_id {app_id} not found")

        _, indices = self.model.kneighbors(game, n_neighbors=n_recommendations+1)
        similar_games = self.df_games.iloc[indices[0][1:]]
        return similar_games

def build_model(feature_matrix):
    model = NearestNeighbors(n_neighbors=5, metric='cosine')
    model.fit(feature_matrix)

    return model

def save_model(model, path):
    print(f"Salvando o modelo em {path}")
    with open(path, 'wb') as f:
        cloudpickle.dump(model, f)
    print("Modelo salvo com sucesso!")

def main():
    date = datetime.now().strftime('%Y-%m')
    s3_ingestion = S3Ingestion()

    s3_ingestion.s3_download_datasets()

    games_path = os.path.join('data', 'games.csv')
    games_metadata_path = os.path.join('data', 'games_metadata.json')

    print("Carregando DataFrames...")
    df_games = load_games_data(games_path)
    df_games_metadata = load_games_metadata(games_metadata_path)
    print("DataFrames carregados com sucesso.")

    df_games_processed, feature_matrix = preprocess_games_data(df_games, df_games_metadata)

    model = build_model(feature_matrix)

    game_recommender = GameRecommender(model, feature_matrix, df_games_processed)

    local_model_dir = os.path.join(os.getcwd(), 'models')
    os.makedirs(local_model_dir, exist_ok=True)
    model_path = os.path.join(local_model_dir, 'game_recommender.pkl')
    save_model(model=game_recommender, path=model_path)

    bucket_name = 'raw-data-game-recommendations'
    prefix = f'anoMes={date}'
    model_filename = f'{prefix}/{os.path.basename(model_path)}'

    s3_ingestion.s3_upload_file(model_path, bucket_name, model_filename)

if __name__ == "__main__":
    main()
