from langdetect import detect
from gtts import gTTS
import os

def text_to_speech(text, output_file="output.mp3"):
    succes = 1
    try:
        # Определение языка текста
        language = detect(text)
        # print(f"Определён язык: {language}")
        
        # Создание аудиофайла с помощью gTTS
        tts = gTTS(text=text, lang=language)
        tts.save(output_file)
        # print(f"Аудиофайл сохранён как {output_file}")
    
    except Exception as e:
        print(f"Ошибка: {e}")
        succes = 0
    
    return succes

if __name__ == "__main__":
    # Введите текст для озвучивания
    input_text = input("Введите текст для озвучивания: ")
    
    # Укажите имя файла для сохранения (по желанию)
    output_filename = input("Введите имя выходного файла (по умолчанию 'output.mp3'): ") or "output.mp3"
    
    # Вызов функции озвучивания
    text_to_speech(input_text, output_filename)
