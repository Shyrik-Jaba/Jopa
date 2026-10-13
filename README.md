# FitTrack — APK через GitHub Actions

Собираем APK в облаке GitHub. Локально ничего ставить не нужно.

## Что понадобится

- Аккаунт на https://github.com (бесплатно)
- Git для Windows: https://git-scm.com/download/win (при установке — оставь всё по умолчанию)

## Шаг 1. Создай репозиторий на GitHub

1. Зайди на https://github.com/new
2. Repository name: `fittrack`
3. Тип: **Public** (для Private тоже работает, но Actions бесплатны с лимитом)
4. **Не** ставь галочки "Add README", "Add .gitignore", "Choose license"
5. Нажми **Create repository**

GitHub покажет страницу с командами. Не закрывай её.

## Шаг 2. Залей проект

Открой терминал (PowerShell / CMD) и выполни:

    cd "D:\Desktop\хуй хуй хуй хуй\fittrack"

    git init
    git branch -M main
    git add .
    git commit -m "Initial commit"
    git remote add origin https://github.com/ТВОЙ_НИК/fittrack.git
    git push -u origin main

Замени `ТВОЙ_НИК` на свой ник на GitHub. При первом push попросит логин/пароль — используй токен (см. ниже) или Git Credential Manager.

### Если просит пароль — нужен Personal Access Token

1. https://github.com/settings/tokens
2. **Generate new token (classic)**
3. Отметь галочку **repo**
4. Сгенерируй, скопируй
5. Введи как пароль при push

## Шаг 3. Дождись сборки

1. Открой свой репозиторий на GitHub
2. Вкладка **Actions**
3. Увидишь workflow **Build APK** — он уже запустился
4. Первая сборка 20–40 минут
5. Когда зелёная галочка — заходи в неё

## Шаг 4. Скачай APK

1. Внутри успешного запуска — блок **Artifacts** внизу
2. Скачай **fittrack-apk** (zip)
3. Внутри zip — `fittrack-0.1-debug.apk`

## Шаг 5. Установи на телефон

1. Скинь APK на телефон (кабель / Telegram / Google Drive)
2. Открой файл на телефоне
3. Android спросит про "неизвестные источники" — разреши
4. Установи

## Что внутри APK

- Экран **Обзор** — серия дней подряд, всего тренировок, быстрый старт A/B/C
- Экран **Тренировки** — чек-лист упражнений, кнопка "Сохранить"
- Экран **История** — все тренировки по датам
- Экран **Вес** — запись веса, список

Данные хранятся в `/data/data/org.fittrack.fittrack/files/workout_data.json` (внутренняя память приложения).

## Если сборка упала

Загляни в лог Actions — там видно, на каком шаге. Обычно:

- Опечатка в `buildozer.spec` → проверь отступы и кавычки
- Проблемы с версией NDK → попробуй `android.ndk = 25b` → `android.ndk = 23b`
- Долго собирается — это нормально, p4a компилирует Python под ARM

## Обновление приложения

Меняешь код → `git add . && git commit -m "update" && git push` → Actions запустится сам → новый APK.
