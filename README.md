# Higgsfield AI Prompt Filter (Telegram Bot & Engine)

Production-ready Telegram-бот с AI-слоем **Prompt Filter**, работающим по методологии **Higgsfield**.

Превращает человеческие сырые запросы вроде:
> *«Сделай красивое видео BMW E39 ночью в Алматы»*

в профессиональные, технически выверенные задания для генеративных видео- и фото-нейросетей (Kling, Veo, Runway, Flux, Seedance, Sora, Midjourney, Hailuo, Nano Banana).

---

## 🎯 Архитектурный принцип

```
Telegram User Input
       ↓
Context Manager (Anti-Degradation Memory)
       ↓
AI Scene Analyzer (Decomposition & Cinematography Spec)
       ↓
Structured Scene JSON (Internal Representation)
       ↓
Director / Prompt Engineer
       ↓
Model Adapter: PromptAdapter(model, task, input)
       ↓
Copy-Ready Output to Telegram
```

---

## 🚀 Возможности

1. **Глубокая декомпозиция сцены**:
   - Главный объект (`subject`), персонажи (`characters`), окружение (`environment`), локация (`location`);
   - Положение и движение камеры (`camera`), оптика (`lens`), тип кадра (`shot_type`);
   - Освещение (`lighting`), время суток (`time_of_day`), контраст, цветовая температура;
   - Физика (`physics`), динамика (`dynamics`), размытие движения (`motion blur`);
   - Временная согласованность (`temporal consistency`) и сохранение геометрии.

2. **Сохранение пользовательского намерения (Identity & Feature Preservation)**:
   - Если указано «не менять лицо» или передан фото-референс: автоматически формируется жесткое правило `PRESERVE THE SUBJECT’S IDENTITY, FACIAL STRUCTURE, HAIRSTYLE, CLOTHING...`.
   - Характеристики конкретных автомобилей, предметов и одежды надежно фиксируются.

3. **Защита от деградации контекста (Anti-Degradation)**:
   - При итерациях (*«теперь камера сзади»*, *«сделай дождь сильнее»*) бот изменяет только запрошенные параметры, не сбрасывая всю сцену.

4. **Три режима работы**:
   - `FAST`: Мгновенная техническая оптимизация промпта.
   - `PRO`: Глубокий cinematographic анализ оптики, траектории камеры, света и физики.
   - `DIRECTOR`: Полная режиссерская концепция с раскадровкой на 3 шота (Establishing, Kinetic Tracking, Hero Close-Up) и отдельными адаптированными промптами для каждого шота.

5. **Модельные адаптеры (Model Adapters)**:
   - **Kling 1.5 Pro**: Синтаксис физической динамики, теги траектории камеры и плавности.
   - **Google Veo 2**: 24fps film stock, теги визуальной стабильности, кинематографическая композиция.
   - **Runway Gen-3 Alpha**: Формат `[Camera Movement] + [Subject Action] + [Environment] + [Lighting]`.
   - **Flux.1**: Аутентичное фотографическое описание с точной оптикой без пустых стоп-слов.
   - **Seedance**: Прогрессия ключевых кадров и пространственный баланс.
   - **OpenAI Sora**: Пространственно-временная физика, трекинг и координация.
   - **Midjourney v6.1**: Параметры `--ar`, `--style raw`, `--v 6.1` и негативные флаги `--no`.
   - **MiniMax Hailuo**: Реалистичная анимация движения и мимики.
   - **Nano Banana**: Сверхкомпактный токенизированный формат.

---

## 📁 Структура проекта

```
higgsfield-prompt-filter/
├── bot/
│   ├── __init__.py
│   ├── telegram.py          # Инициализация бота и запуск polling
│   ├── handlers.py          # Обработчики команд, сообщений и фото
│   └── keyboards.py         # Кнопки Telegram меню и inline селекторы
├── ai/
│   ├── __init__.py
│   ├── analyzer.py          # Декомпозитор пользовательского запроса
│   ├── context.py           # Менеджер контекста диалога и защита от деградации
│   ├── director.py          # Генератор многошотовых планов в режиме DIRECTOR
│   └── prompt_engine.py     # Главный оркестратор пайплайна
├── adapters/
│   ├── __init__.py          # Фабрика и функция PromptAdapter(model, task, input)
│   ├── base.py              # Базовый класс BasePromptAdapter
│   ├── kling.py             # Адаптер Kling AI
│   ├── veo.py               # Адаптер Google Veo
│   ├── runway.py            # Адаптер Runway Gen-3
│   ├── flux.py              # Адаптер Flux.1
│   ├── seedance.py          # Адаптер Seedance
│   ├── sora.py              # Адаптер OpenAI Sora
│   ├── hailuo.py            # Адаптер MiniMax Hailuo
│   ├── nano_banana.py       # Адаптер Nano Banana
│   └── midjourney.py        # Адаптер Midjourney v6.1
├── models/
│   ├── __init__.py
│   └── schemas.py           # Pydantic v2 схемы промежуточного JSON
├── config/
│   ├── __init__.py
│   └── settings.py          # Безопасная загрузка конфигурации из .env
├── tests/
│   ├── __init__.py
│   ├── test_prompt_engine.py
│   └── test_adapters.py
├── cloudflare/
│   ├── wrangler.toml        # Конфигурация для Cloudflare Workers
│   └── worker.js            # Edge-обработчик вебхука и REST API
├── requirements.txt
├── run.py                   # Точка входа для запуска бота
└── .env.example
```

---

## 🛠 Установка и запуск

### 1. Клонирование и виртуальное окружение

```bash
git clone https://github.com/tapwork-kz/higgsfield-prompt-filter.git
cd higgsfield-prompt-filter

# Создание виртуального окружения
uv venv
# или: python -m venv .venv

# Активация:
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# Установка зависимостей:
uv pip install -r requirements.txt
# или: pip install -r requirements.txt
```

### 2. Настройка переменных окружения

Создайте файл `.env` на основе `.env.example`:

```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
DEFAULT_MODE=PRO
DEFAULT_MODEL=Kling
DEFAULT_TASK_TYPE=video
```

*(Файл `.env` строго добавлен в `.gitignore` и никогда не попадает в репозиторий).*

### 3. Запуск тестов

```bash
pytest -v
```

### 4. Запуск Telegram-бота

```bash
python run.py
```

---

## 🤖 Команды Telegram-бота

| Команда | Описание |
|---|---|
| `/start` | Приветствие и справка |
| `/new` | Сброс контекста и создание новой сцены |
| `/video` | Переключение в режим видеогенерации |
| `/image` | Переключение в режим фотогенерации |
| `/edit` | Режим модификации референсного изображения |
| `/models` | Меню выбора целевой нейросети |
| `/settings` | Выбор режима (`FAST`, `PRO`, `DIRECTOR`) |

Также доступны быстрые кнопки в клавиатуре Telegram:
`[VIDEO]`, `[IMAGE]`, `[EDIT IMAGE]`, `[ENHANCE PROMPT]`, `[CHANGE MODEL]`, `[GENERATE]`.

---

## ☁️ Развертывание в Cloudflare Workers

Для serverless выполнения в Cloudflare Edge:

```bash
cd cloudflare
npx wrangler deploy
```

Задайте токен секретом:
```bash
npx wrangler secret put TELEGRAM_BOT_TOKEN
```

Установите Webhook:
```bash
curl "https://api.telegram.org/bot<YOUR_TOKEN>/setWebhook?url=https://higgsfield-prompt-filter.<subdomain>.workers.dev/webhook"
```
