import os
from datetime import datetime

from utils.s3_utils import S3Ingestion
from utils.secrets_manager import SecretsManager
from kaggle.kaggle.api.kaggle_api_extended import KaggleApi


S3_BUCKET = os.environ.get('S3_BUCKET')
KAGGLE_DATASET = 'antonkozyriev/game-recommendations-on-steam'
SECRET_NAME = os.environ.get('SECRET_NAME')

def lambda_handler(event, context):

    secrets_manager = SecretsManager()

    # obter segredos do secrets manager
    kaggle_username, kaggle_key = secrets_manager.get_secrets_values(SECRET_NAME)
    # print(SECRET_NAME)
    # teste = secrets_manager.get_secrets_values(SECRET_NAME)
    print("teste: ",kaggle_username, kaggle_key) 

    #definir credenciais como variaveis de ambiente
    os.environ['KAGGLE_USERNAME'] = kaggle_username
    os.environ['KAGGLE_KEY'] = kaggle_key

    # autenticar usando API do kaggle
    api = KaggleApi()
    api.authenticate()

    # definir caminho para arquivo temp na lambda
    date = datetime.now().strftime('%Y-%m')
    dataset_path = f'/tmp/{KAGGLE_DATASET}/{date}.zip'

    # baixar dataset do kaggle
    api.dataset_download_files(KAGGLE_DATASET, path='/tmp', unzip=True)

    # renomear arquivo descompactado
    os.rename(f'/tmp/{KAGGLE_DATASET}.csv', dataset_path)

    # fazer upload para o s3
    s3_bucket = os.environ.get('S3_BUCKET')
    s3_key = f'kaggle_datasets/{KAGGLE_DATASET}/{date}.csb'

    s3_ingestion = S3Ingestion()
    s3_ingestion(dataset_path, s3_bucket, s3_key)

    return {
        'statusCode': 200,
        'body': f'Dataset armazenado com sucesso em {s3_bucket}/{s3_key}'
    }
