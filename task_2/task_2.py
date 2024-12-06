import requests
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
import matplotlib.pyplot as plt
import re
import sys

# Функція для завантаження тексту за URL
def fetch_text(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.text

# MapReduce: функція "Mapper"
def mapper(text_chunk):
    words = re.findall(r'\b\w+\b', text_chunk.lower())
    return Counter(words)

# MapReduce: функція "Reducer"
def reducer(counters):
    total_counter = Counter()
    for counter in counters:
        total_counter.update(counter)
    return total_counter

# Функція для розбиття тексту на частини
def split_text(text, num_chunks):
    lines = text.splitlines()
    chunk_size = max(1, len(lines) // num_chunks)
    return ["\n".join(lines[i * chunk_size:(i + 1) * chunk_size]) for i in range(num_chunks)]

# Візуалізація топ-слів
def visualize_top_words(word_counts, top_n=10):
    if not word_counts:
        print("Помилка: словник частот порожній. Можливо, текст не містить слів.")
        return

    top_words = word_counts.most_common(top_n)
    if not top_words:
        print("Помилка: немає даних для візуалізації.")
        return

    words, counts = zip(*top_words)

    plt.figure(figsize=(10, 6))
    plt.bar(words, counts, color='skyblue')
    plt.xlabel('Words')
    plt.ylabel('Frequency')
    plt.title(f'Top {top_n} Words by Frequency')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    # Перевірка наявності аргументів командного рядка
    if len(sys.argv) < 2:
        print("Помилка: Вкажіть URL для аналізу як аргумент командного рядка.")
        print("Приклад використання: python task_2.py https://example.com/text.txt")
        sys.exit(1)

    # URL з аргументу командного рядка
    url = sys.argv[1]

    try:
        # Крок 1: Завантаження тексту
        print("Завантаження тексту...")
        text = fetch_text(url)

        # Крок 2: Розбиття тексту на частини
        num_chunks = 8  # Кількість потоків
        text_chunks = split_text(text, num_chunks)

        # Крок 3: Аналіз частоти слів за допомогою MapReduce
        print("Аналіз частоти слів...")
        with ThreadPoolExecutor(max_workers=num_chunks) as executor:
            counters = list(executor.map(mapper, text_chunks))

        word_counts = reducer(counters)

        # Крок 4: Візуалізація результатів
        print("Візуалізація результатів...")
        visualize_top_words(word_counts, top_n=10)

    except requests.RequestException as e:
        print(f"Помилка завантаження тексту: {e}")
    except Exception as e:
        print(f"Сталася помилка: {e}")


