import os
from datetime import datetime

from utils.s3_utils import S3Ingestion
from utils.secrets_manager import SecretsManager

from kaggle.api.kaggle_api_extended import KaggleApi
from kaggle.api_client import ApiClient
from kaggle.configuration import Configuration


S3_BUCKET = os.environ.get('S3_BUCKET')
KAGGLE_DATASET = 'antonkozyriev/game-recommendations-on-steam'
SECRET_NAME = os.environ.get('SECRET_NAME')

def lambda_handler(event, context):

    secrets_manager = SecretsManager()

    # obter segredos do secrets manager
    kaggle_username, kaggle_key = secrets_manager.get_secrets_values(SECRET_NAME)

    # autenticar usando API do kaggle
    config = Configuration(kaggle_username, kaggle_key)
    api = KaggleApi(ApiClient(config))

    # definir caminho para arquivo temp na lambda
    date = datetime.now().strftime('%Y-%m')

    # baixar dataset do kaggle
    api.dataset_download_files(KAGGLE_DATASET, path='/tmp', unzip=True)


    s3_bucket = os.environ.get('S3_BUCKET')
    s3_ingestion = S3Ingestion()

    for file in os.listdir('/tmp'):
        # fazer upload para o s3
        s3_key = f'anoMes={date}/{file}'
        s3_ingestion.s3_upload_file(f'/tmp/{file}', s3_bucket, s3_key)

    return {
        'statusCode': 200,
        'body': f'Dataset armazenado com sucesso em {s3_bucket}/{s3_key}'
    }
