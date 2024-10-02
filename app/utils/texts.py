import re

def contains_chinese(text):
    chinese_char_pattern = re.compile(r'[\u4e00-\u9fff]+')
    return bool(chinese_char_pattern.search(text))

def remove_emojis(text):
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # Emoticons
        "\U0001F300-\U0001F5FF"  # Símbolos e pictogramas
        "\U0001F680-\U0001F6FF"  # Símbolos de transporte e mapas
        "\U0001F1E0-\U0001F1FF"  # Bandeiras (alfabeto regional)
        "\U00002500-\U00002BEF"  # Setas e símbolos variados
        "\U00002702-\U000027B0"  # Outros tipos de símbolos e pictogramas
        "\U000024C2-\U0001F251"  # Diversos símbolos extras
        "\U0001F900-\U0001F9FF"  # Símbolos e pictogramas de extensão
        "\U0001FA70-\U0001FAFF"  # Novos pictogramas e símbolos adicionais
        "\U00002600-\U000026FF"  # Diversos símbolos como ☀️, ⛅, ☁️
        "\U0001F7E0-\U0001F7FF"  # Quadrados coloridos, etc.
        "\U0001F780-\U0001F7D8"  # Círculos e quadrados coloridos
        "]+", flags=re.UNICODE)

    if (contains_chinese(text)):
        emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # Emoticons
        "\U0001F300-\U0001F5FF"  # Símbolos e pictogramas
        "\U0001F680-\U0001F6FF"  # Símbolos de transporte e mapas
        "\U0001F1E0-\U0001F1FF"  # Bandeiras (alfabeto regional)
        "\U0001F900-\U0001F9FF"  # Símbolos e pictogramas de extensão
        "\U0001FA70-\U0001FAFF"  # Novos pictogramas e símbolos adicionais
        "\U0001F7E0-\U0001F7FF"  # Quadrados coloridos, etc.
        "\U0001F780-\U0001F7D8"  # Círculos e quadrados coloridos
        "]+", flags=re.UNICODE)

    return emoji_pattern.sub(r'', text).strip().lower()

def remove_special_chars(text):
    special_char_pattern = re.compile(r'[™©®…<>#$%^&*+=\[\]{}|\\/~`.,;:!?\'\"()/]')
    return special_char_pattern.sub(r'', text)