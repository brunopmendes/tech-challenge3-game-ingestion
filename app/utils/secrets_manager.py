import boto3
import json

class SecretsManager():


    def __init__(self) -> None:
        self.secret_client = boto3.client('secretsmanager')


    def get_secrets_values(self, secret_name: str):
        try:
            secret_response = self.secret_client.get_secret_value(SecretId=secret_name)
            print(f'Segredo {secret_name} recuperado com sucesso')

            secret = json.loads(secret_response['SecretString'])
            return secret['KAGGLE_USERNAME'], secret['KAGGLE_KEY']
            return secret_response['SecretString']
        except Exception as e:
            print(f'Erro ao recuperar o segrego {secret_name}, erro: {e}')
            raise e
