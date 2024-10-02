import pandas as pd
import time
from googletrans import Translator
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy.sparse import hstack
from app.utils.texts import remove_special_chars, remove_emojis

translator = Translator()

def translate_text(text, retries=5):
    """Translates the text to english"""
    for attempt in range(retries):
        try:
            translator.raise_Exception = True
            translated_text = translator.translate(text, dest='en').text
            time.sleep(1)
            return remove_special_chars(f'{translated_text} ({text})').strip().lower()
        except Exception as error:
            if '429' in str(error):
                print(f'Erro 429 detectado. Tentando novamente... (Tentativa {attempt + 1})')
                time.sleep(5 + attempt * 5)
            else:
                print(f'Erro ao traduzir: {text}\n{error}\n')
                return text
    print(f'Falha ao traduzir após {retries} tentativas: {text}')
    return text

def preprocess_games_data(df_games: pd.DataFrame, df_games_metadata: pd.DataFrame):
    print("Removendo colunas desnecessárias do dataset...")
    df_games.drop(columns=['date_release', 'price_final', 'price_original', 'discount'], inplace=True)
    print("Colunas removidas com sucesso.")

    print("Realizando encoding da coluna rating, win, mac, linux e steam_deck")
    ratings_encoding = {
        'Overwhelmingly Negative': 0,
        'Very Negative': 1,
        'Negative': 2,
        'Mostly Negative': 3,
        'Mixed': 4,
        'Mostly Positive': 5,
        'Positive': 6,
        'Very Positive': 7,
        'Overwhelmingly Positive': 8
    }
    df_games['rating'] = df_games['rating'].map(ratings_encoding)
    df_games[['win', 'mac', 'linux', 'steam_deck']] = df_games[['win', 'mac', 'linux', 'steam_deck']].astype(int)
    print("Encoding feito com sucesso!")
    
    print("Juntando dataframe de jogos com sua metadata...")
    df_games = pd.merge(df_games, df_games_metadata, on='app_id', how='inner')
    print("Dataframes únidos com sucesso.")

    print("Tratando gêneros dos jogos.")
    tags_dummies = preprocess_genres(df_games['tags'])
    df_games = pd.concat([df_games, tags_dummies], axis=1)
    print("One-hot encoding aplicado com sucesso aos gêneros dos jogos.")

    print("Removendo caracteres especiais e emojis dos títulos e descrições dos jogos")
    df_games['clean_title'] = df_games['title'].apply(lambda x: remove_emojis(remove_special_chars(x)))
    df_games['clean_description'] = df_games['description'].apply(lambda x: remove_emojis(remove_special_chars(x)))
    print("Caracteres especiais e emojis tratados com sucesso.")

    print("Traduzindo títulos e descrições para o inglês")
    non_ascii_full_regex = r'^[^\x00-\x7F\d.,:;!?\'"()\-–…\s]+[\d.,:;!?\'"()\-–…\s]*$'
    df_games.loc[df_games['clean_title'].str.match(non_ascii_full_regex, na=False), 'clean_title'] = df_games[df_games['clean_title'].str.match(non_ascii_full_regex, na=False)]['clean_title'].apply(translate_text)
    df_games.loc[df_games['clean_description'].str.match(non_ascii_full_regex, na=False), 'clean_description'] = df_games[df_games['clean_description'].str.match(non_ascii_full_regex, na=False)]['clean_description'].apply(translate_text)
    print("Títulos e descrições traduzidas com sucesso.")

    print("Tratando textos vazios")
    df_games.loc[df_games["clean_description"] == "", 'clean_description'] = df_games.loc[df_games["clean_description"] == "", 'clean_title']
    print("Textos tratados com sucesso.")

    feature_matrix = get_feature_matrix(df_games, tags_dummies)

    return df_games, feature_matrix

def preprocess_genres(tags: pd.Series):
    tags_dummies = pd.get_dummies(tags.explode()).groupby(level=0).sum()
    return tags_dummies

def get_tfidf():
    return TfidfVectorizer(stop_words=None)

def preprocess_title(df_games: pd.DataFrame):
    tfidf = get_tfidf()
    title_tfidf = tfidf.fit_transform(df_games['clean_title'])
    return title_tfidf

def preprocess_description(df_games: pd.DataFrame):
    tfidf = get_tfidf()
    description_tfidf = tfidf.fit_transform(df_games['clean_description'])
    return description_tfidf

def get_feature_matrix(df_games: pd.DataFrame, genres: pd.DataFrame):
    TITLE_WEIGHT = 2.5
    DESCRIPTION_WEIGHT = 1.0
    GENRES_WEIGHT = 3.0
    
    print("Criando feature matrix")
    title_tfidf = preprocess_title(df_games)
    description_tfidf = preprocess_description(df_games)

    feature_matrix = hstack([
        genres * GENRES_WEIGHT,
        title_tfidf * TITLE_WEIGHT,
        description_tfidf * DESCRIPTION_WEIGHT
    ])
    print("Feature matrix criada com sucesso.")

    return feature_matrix
    