import string
from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict
import requests
import matplotlib.pyplot as plt

# Функція для отримання тексту з URL
def get_text(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Перевірка на помилки HTTP
        return response.text
    except requests.RequestException as e:
        return None

# Функція для видалення знаків пунктуації
def remove_punctuation(text):
    return text.translate(str.maketrans("", "", string.punctuation))

# Функція мапінгу для MapReduce
def map_function(word):
    return word.lower(), 1

# Функція перемішування для MapReduce
def shuffle_function(mapped_values):
    shuffled = defaultdict(list)
    for key, value in mapped_values:
        shuffled[key].append(value)
    return shuffled.items()

# Функція редукції для MapReduce
def reduce_function(key_values):
    key, values = key_values
    return key, sum(values)

# Головна функція MapReduce
def map_reduce(text):
    # Видалення пунктуації та розділення на слова
    text = remove_punctuation(text)
    words = text.split()

    # Паралельний мапінг
    with ThreadPoolExecutor() as executor:
        mapped_values = list(executor.map(map_function, words))

    # Перемішування
    shuffled_values = shuffle_function(mapped_values)

    # Паралельна редукція
    with ThreadPoolExecutor() as executor:
        reduced_values = list(executor.map(reduce_function, shuffled_values))

    return dict(reduced_values)

# Функція для візуалізації топ слів
def visualize_top_words(word_freq, top_n=10):
    # Сортування слів за частотою та вибір топ N
    sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:top_n]
    words, frequencies = zip(*sorted_words)
    
    # Створення горизонтальної гістограми
    plt.figure(figsize=(10, 6))
    plt.barh(words, frequencies, color='skyblue')
    plt.xlabel('Частота')
    plt.ylabel('Слова')
    plt.title(f'Топ {top_n} найчастіших слів')
    plt.gca().invert_yaxis()  # Інвертуємо вісь Y для відображення найчастіших слів зверху
    plt.tight_layout()
    plt.show()

if __name__ == '__main__':
    # URL тексту для аналізу (роман "Гордість і упередження" Джейн Остін)
    url = "https://www.gutenberg.org/files/1342/1342-0.txt"
    text = get_text(url)
    if text:
        # Виконання MapReduce
        result = map_reduce(text)
        # Візуалізація результатів
        visualize_top_words(result)
    else:
        print("Помилка: Не вдалося отримати текст.")
