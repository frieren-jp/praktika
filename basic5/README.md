# BASIC-5 - настройка рабочего окружения

В этой папке лежат материалы для сдачи задачи BASIC-5.

Что нужно сдать руководителю: скриншот терминала Ubuntu в WSL с успешным выводом команд из чеклиста.

Файлы:

- `final-checklist.txt` - текстовый вариант финального вывода команд.
- `final-screenshot.png` - сюда нужно сохранить итоговый скриншот терминала.

Статус на новом ПК:

- WSL включен и Ubuntu установлена как WSL 2.
- Docker и Docker Compose установлены внутри Ubuntu.
- `docker run hello-world` успешно выполнен.
- `uv` установлен, Python 3.12 установлен через `uv`.
- FastAPI успешно проверен через `uv`.
- Node.js, npm и VS Code CLI отвечают в Ubuntu.

На финальном скриншоте должны быть видны:

- версия Docker;
- версия Docker Compose;
- успешный запуск `docker run hello-world`;
- версия `uv`;
- установленный Python 3.12 через `uv`;
- успешная проверка FastAPI;
- версии `node` и `npm`;
- версия VS Code через `code --version`.

Команды, которые удобно выполнить в Ubuntu-терминале перед скриншотом:

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
