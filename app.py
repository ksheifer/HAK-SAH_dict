import csv
from flask import Flask, render_template, request

app = Flask(__name__)

# Функция для загрузки данных из CSV
def load_dictionary():
    dictionary = []
    try:
        with open('/Users/karinasheifer/Documents/Languages/Turkic/NorthSiberian/DLG/tyldit.csv', mode='r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file, delimiter='\t')
            for row in csv_reader:
                row = {key.strip(): (value.strip() if value else '') for key, value in row.items()}
                dictionary.append(row)
    except Exception as e:
        print(f"Ошибка при загрузке словаря: {e}")
    return dictionary

# Функция для нормализации текста
def normalize_text(text):
    return (text.replace('е', 'ё')
               .replace('ҕ', '5')
               .replace('һ', 'ь')
               .replace('5', 'ҕ')
               .replace('ң', 'ҥ'))

@app.route("/", methods=["GET", "POST"])
def index():
    dictionary = load_dictionary()  # Загружаем данные из CSV
    results = []  # Список для хранения результатов
    error_message = None  # Сообщение об ошибке

    # Получаем общий поисковый запрос
    search_query = request.form.get("search_query", "")

    # Статистика по словам
    total_words = len(dictionary)  # Общее количество слов в словаре
    identical_words = 0  # Слова, где SIM == 100
    different_words = 0  # Слова, где SIM == 0
    partially_different_words = 0  # Слова, где SIM != 0 и SIM != 100

    for entry in dictionary:
        sim_value = entry.get('SIM')
        if sim_value:
            sim_value = int(sim_value)  # Преобразуем в число для сравнения
            if sim_value == 100:
                identical_words += 1
            elif sim_value == 0:
                different_words += 1
            else:
                partially_different_words += 1

    identical_percent = int((identical_words / total_words) * 100) if total_words else 0
    different_percent = int((different_words / total_words) * 100) if total_words else 0
    partially_different_percent = int((partially_different_words / total_words) * 100) if total_words else 0

    # Поиск по запросу
    if search_query:
        normalized_query = normalize_text(search_query.lower())
        exact_matches = []
        prefix_matches = []

        for entry in dictionary:
            normalized_nyuchchaly = normalize_text(entry.get('НЬУУЧЧАЛЫЫ', '').lower())
            normalized_hakaly = normalize_text(entry.get('ҺАКАЛЫЫ', '').lower())
            normalized_sakhaly = normalize_text(entry.get('САХАЛЫЫ', '').lower())

            if (normalized_query == normalized_nyuchchaly or
                normalized_query == normalized_hakaly or
                normalized_query == normalized_sakhaly):
                exact_matches.append(entry)
            else:
                for field in [normalized_nyuchchaly, normalized_hakaly, normalized_sakhaly]:
                    prefix_length = 3 if len(field) <= 5 else 4
                    if normalized_query[:prefix_length] == field[:prefix_length]:
                        prefix_matches.append(entry)
                        break

        results = exact_matches + prefix_matches
        if not results:
            error_message = "Тугу эмэ атыны көрдөөн көр"

    return render_template(
        'index.html',
        results=results,
        search_query=search_query,
        error_message=error_message,
        total_words=total_words,
        identical_words=f"{identical_percent}%",
        different_words=f"{different_percent}%",
        partially_different_words=f"{partially_different_percent}%"
    )

if __name__ == "__main__":
    app.run(debug=True)
