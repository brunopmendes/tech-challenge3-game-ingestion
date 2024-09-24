provider "aws" {
  region = "us-east-1"
}

resource "aws_lambda_function" "lambda_game_ingestion" {
  filename      = data.archive_file.lambda_my_function.output_path
  function_name = "lambda_game_ingestion"
  role          = "arn:aws:iam::306876822650:role/LabRole"
  description   = "Lambda captura mensalmente dataset do kaggle de recomendação de jogos"

  handler = "lambda_handler.lambda_handler"
  runtime = "python3.9"

  source_code_hash = filebase64sha256(data.archive_file.lambda_my_function.output_path) #hash para capturar qualquer alteracao na lambda

  environment {
    variables = {
      S3_BUCKET   = "raw-data-game-recommendations"
      SECRET_NAME = "kaggle-api-secrets"
    }
  }

  layers      = [aws_lambda_layer_version.lambda_layer.arn]
  timeout     = 180
  memory_size = 4096
  ephemeral_storage {
    size = 4096
  }
}

# TRIGGER
resource "aws_cloudwatch_event_rule" "monthly_trigger_rule" {
  name                = "monthly-trigger-rule"
  description         = "Regra do EventBridge para rodar Lambda no dia 1 de cada mês"
  schedule_expression = "cron(0 0 1 * ? *)" # Todo dia 1 de cada mês à meia-noite (UTC)
}

resource "aws_cloudwatch_event_target" "lambda_target" {
  rule = aws_cloudwatch_event_rule.monthly_trigger_rule.name
  arn  = aws_lambda_function.lambda_game_ingestion.arn
}

resource "aws_lambda_permission" "allow_eventbridge_to_invoke_lambda" {
  statement_id  = "AllowEventBridgeInvokeLambda"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.lambda_game_ingestion.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.monthly_trigger_rule.arn
}

# LAMBDA LAYER - KAGGLE
resource "aws_lambda_layer_version" "lambda_layer" {
  filename   = "${path.module}/../out/libs.zip"
  layer_name = "kaggle_layer"

  compatible_runtimes = ["python3.9"]

  source_code_hash = filebase64sha256("${path.module}/../out/libs.zip")
}


# CRIA ZIP PARA LAMBDA
data "archive_file" "lambda_my_function" {
  type             = "zip"
  source_dir       = "${path.module}/../app/"
  output_file_mode = "0666"
  output_path      = "${path.module}/../out/lambda_handler.zip"
}

# CRIA ZIP PARA LIB KAGGLE
# data "archive_file" "lambda_my_layer" {
#   type             = "zip"
#   source_dir       = "${path.module}/../libs/"
#   output_file_mode = "0666"
#   output_path      = "${path.module}/../out/libs.zip"
# }