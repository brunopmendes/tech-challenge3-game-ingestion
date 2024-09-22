provider "aws" {
  region = "us-east-1"
}

resource "aws_lambda_function" "lambda_game_ingestion" {
  filename      = data.archive_file.lambda_my_function.output_path
  function_name = "lambda_game_ingestion"
  role          = "arn:aws:iam::306876822650:role/LabRole"
  description   = "Lambda captura mensalmente dataset do kaggle de recomendação de jogos"

  handler = "lambda_handler.lambda_handler"
  runtime = "python3.11"

  source_code_hash = filebase64sha256(data.archive_file.lambda_my_function.output_path) #hash para capturar qualquer alteracao na lambda

  environment {
    variables = {
      S3_BUCKET   = "raw-data-game-recommendations"
      SECRET_NAME = "kaggle-api-secrets"
    }
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



# CRIA ZIP PARA LAMBDA
data "archive_file" "lambda_my_function" {
  type             = "zip"
  source_dir       = "${path.module}/../app/"
  output_file_mode = "0666"
  output_path      = "${path.module}/../out/lambda_handler.zip"
}