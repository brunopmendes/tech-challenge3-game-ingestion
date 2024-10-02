import boto3
import os
from dotenv import load_dotenv
from datetime import datetime

class S3Ingestion:


    def __init__(self) -> None:
        print("Instanciando S3...")
        load_dotenv()

        aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
        aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        aws_session_token = os.getenv('AWS_SESSION_TOKEN')

        self.s3 = boto3.client(
            's3',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            aws_session_token=aws_session_token
        )
        print("S3 instanciado com sucesso!")

    
    def s3_upload_file(self, file_name: str, bucket: str, key: str) -> None:
        try:
            self.s3.upload_file(file_name, bucket, key)
            print(f'Sucesso no upload do arquivo {file_name} no bucket {bucket}')
        except Exception as e:
            print(f'Erro no upload do arquivo {file_name} no bucket {bucket}')
            raise e 

    def s3_download_datasets(self):
        date = datetime.now().strftime('%Y-%m')
        bucket_name = 'raw-data-game-recommendations'
        prefix = f'anoMes={date}/'
        response = self.s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)

        if 'Contents' in response:
            local_data_dir = os.path.join(os.getcwd(), 'data')
            os.makedirs(local_data_dir, exist_ok=True)

            for obj in response['Contents']:
                file_key = obj['Key']
                file_name = os.path.basename(file_key)
                local_file_name = os.path.join(local_data_dir, file_name)

                if file_name == 'game_recommender.pkl':
                    continue

                if os.path.exists(local_file_name):
                    print(f"Arquivo {file_name} já existe localmente, pulando download.")
                    continue

                try:
                    self.s3.download_file(bucket_name, file_key, local_file_name)
                    print(f"Arquivo {file_name} baixado com sucesso!")
                except Exception as e:
                    print(f"Erro ao baixar o arquivo {file_name}: {e}")
            print(f"Todos os arquivos do {bucket_name} foram baixados com sucesso.")
        else:
            print(f"Nenhum arquivo encontrado no prefixo {prefix}.")
