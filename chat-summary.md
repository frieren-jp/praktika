# Сводка по практике

Этот файл нужен, чтобы быстро продолжить работу без потери контекста.

## Общая структура

```text
praktika/
  basic1/
  todo_app/
  basic4/
  basic5/
  chat-summary.md
```

## BASIC-1 - archtool и web_fractal

Задача: изучить документацию `archtool` и `web_fractal`, затем подготовить текстовый документ с ответами на вопросы.

Формат сдачи: markdown, Google Docs или PDF.

В папке `basic1` лежат:

- `README.md` - что находится в папке;
- `basic1-answers.md` - готовый документ для сдачи.

Документ покрывает:

- `DependencyInjector` и проблему ручной разводки зависимостей;
- двухпроходной алгоритм `discover` / `inject`;
- `Layer`, контроль слоев и `TopLevelLayerUsingException`;
- `AppModule` как bounded context;
- роль `web_fractal` поверх `archtool`;
- `UnitOfWork`, `BaseRepo`, `initialize_controllers_api`, `import_all_models`, `HttpControllerABC`;
- пример структуры проекта на `archtool` + `web_fractal`.

Статус: документ подготовлен, можно отправлять руководителю или переносить в Google Docs/PDF.

## BASIC-2 - ToDo API на archtool + web_fractal

Задача: создать работающий мини-проект ToDo API на `archtool`, `web_fractal`, FastAPI и async SQLAlchemy.

Проект лежит в папке `todo_app`.

Реализовано:

- bounded context `users`: создание и получение пользователя;
- bounded context `todos`: создание, список задач пользователя, отметка задачи выполненной;
- `DependencyInjector` с передачей всех 4 дефолтных слоев;
- зависимости через классовые аннотации без параметров `__init__`;
- кросс-модульная зависимость `TodoService -> UserServiceABC`;
- репозитории используют `UnitOfWork`;
- `session_maker` регистрируется через `injector.register()`;
- контроллеры наследуют `HttpControllerABC`;
- используются `import_all_models()` и `initialize_controllers_api()`;
- приложение запускается через `uvicorn`;
- README содержит инструкцию запуска и curl-примеры.

Команды проверки:

```powershell
cd todo_app
.\check.ps1
```

Команда запуска сервера из Windows PowerShell:

```powershell
cd todo_app
.\run.ps1
```

Проверка пройдена: все 5 эндпоинтов ответили успешно.

Статус: проект готов локально. Для сдачи осталось опубликовать папку `todo_app` в публичный GitHub-репозиторий и отправить ссылку руководителю.

## BASIC-4 - ООП и SOLID в Python

Задача: подготовиться к устному опросу по ООП и принципам SOLID.

Формат сдачи: устный опрос с руководителем практики на 10-15 минут.

В папке `basic4` лежат материалы на русском:

- `README.md` - описание файлов;
- `konspekt.md` - краткий конспект по ООП и SOLID с примерами на Python;
- `otvety.md` - готовые ответы на частые вопросы устного опроса.

Статус: материалы подготовлены, можно читать перед опросом.

## BASIC-5 - настройка рабочего окружения

Задача: настроить рабочее окружение для разработки.

Формат сдачи: скриншот терминала Ubuntu в WSL с успешным выводом команд из чеклиста.

В папке `basic5` лежат:

- `README.md` - что нужно сдать;
- `final-checklist.txt` - текстовый вариант успешного вывода команд.

Что было проверено и заработало на новом ПК:

- WSL Ubuntu установлен и работает как WSL 2;
- Docker установлен внутри Ubuntu WSL;
- `docker --version` показывает `Docker version 29.1.3`;
- `docker compose version` показывает `Docker Compose version 2.40.3`;
- `docker run hello-world` успешно выводит `Hello from Docker!`;
- `uv` установлен: `uv 0.11.21`;
- Python 3.12 установлен через `uv`;
- проверка FastAPI дала `FastAPI 0.137.0 OK`;
- Node.js установлен: `v22.22.1`;
- npm работает: `9.2.0`;
- `code --version` показал `1.120.0`.

Финальный чеклист для скриншота:

```bash
docker --version
docker compose version
docker run hello-world
uv --version
uv python install 3.12
uv run --with fastapi python -c "import fastapi; print('FastAPI', fastapi.__version__, 'OK')"
node --version
npm --version
code --version
```

Статус: окружение настроено. Осталось сохранить финальный скриншот в `basic5/final-screenshot.png` и отправить руководителю.
