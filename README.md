# 📄 ETL Document Service + RAG

![Python](https://img.shields.io/badge/python-3.12-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-API-green)
![Streamlit](https://img.shields.io/badge/Streamlit-UI-red)
![FAISS](https://img.shields.io/badge/FAISS-vector_search-orange)
![RAG](https://img.shields.io/badge/RAG-enabled-purple)
![Docker](https://img.shields.io/badge/Docker-ready-blue)

Сервис для обработки документов разных форматов и построения поиска и ответов (RAG) поверх них.

---

## 🚀 Возможности

### 📥 Поддержка форматов
- PDF (native + OCR fallback)
- DOC / DOCX
- RTF
- XLSX (таблицы)
- TXT
- Изображения (OCR)

---

### ⚙️ ETL Pipeline
- Определение типа документа
- Извлечение текста (native / OCR)
- Очистка текста
- Разбиение на блоки (Block)
- Умный chunking (Chunk)
- Оценка качества (quality scoring)

---

### 🧠 RAG (Retrieval-Augmented Generation)
- Индексация документов
- Векторный поиск (FAISS)
- Фильтрация по:
  - `document_id`
  - `file_name`
- Генерация ответа на основе найденных чанков

---

## 🌐 API (FastAPI)

### 📌 Индексация документа
```bash
POST /rag/index
```

### 🔍 Поиск
```bash
POST /rag/search
```

### 💬 Вопрос к документам
```bash
POST /rag/ask
```

### 📄 Список документов
```bash
GET /rag/documents
```

### ❌ Удаление документа
```bash
DELETE /rag/document
```

### 🧹 Очистка индекса
```bash
DELETE /rag/index
```

## 🖥️ UI (Streamlit)
- Загрузка файлов
- Индексация
- Поиск
- Вопрос-ответ (RAG)
- Управление документами

## 🏗️ Архитектура
ETL Pipeline
   ↓
Blocks → Chunks
   ↓
Embeddings
   ↓
FAISS Index
   ↓
Retriever
   ↓
Answer Builder

## 📂 Структура проекта
app/
 ├── api/          # FastAPI роуты
 ├── parsers/      # Парсеры документов
 ├── pipeline/     # ETL pipeline
 ├── rag/          # RAG логика
 ├── schemas/      # Pydantic модели
 ├── services/     # OCR, cleaning, chunking
 └── utils/

ui.py              # Streamlit интерфейс
main.py            # FastAPI entrypoint

## 🧪 Запуск локально

1. Установка зависимостей
```bash
pip install -r requirements.txt
```

2. Запуск API
```bash
uvicorn main:app --reload
```

3. Запуск UI
```bash
streamlit run ui.py
```

## 🐳 Запуск через Docker
```bash
docker compose up --build
```

### После запуска:

API: http://localhost:8000/docs
UI: http://localhost:8501

## 🧠 Особенности реализации
- OCR fallback для PDF
- Quality scoring страниц
- Очистка шумных OCR-блоков
- Учет структуры документа (таблицы, заголовки)
- LLM-ready чанки (metadata, context)

## ⚠️ Ограничения
- Таблицы обрабатываются как строки
- Формулы извлекаются частично
- OCR зависит от качества изображения

## 🔮 Возможные улучшения
- Layout-aware parsing
- Улучшенный table extraction
- Кэширование эмбеддингов
- История диалогов
- Авторизация
- Деплой

## 🛠️ Стек
- FastAPI
- Streamlit
- FAISS
- sentence-transformers
- Tesseract OCR
- LibreOffice

# 👤 Автор

#### Александр — Data Scientist 