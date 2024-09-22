import boto3

class S3Ingestion:


    def __init__(self) -> None:
        self.s3 = boto3.client('s3')

    
    def s3_upload_file(self, file_name: str, bucket: str, key: str) -> None:
        try:
            self.s3.upload_file(file_name, bucket, key)
            print(f'Sucesso no uploado do arquivo {file_name} no bucket {bucket}')
        except Exception as e:
            print(f'Erro no upload do arquivo {file_name} no bucket {bucket}')
            raise e 

