# Спека: polish-public (i18n + Linux docs + scanner perf)

Дата: 2026-11-05 · Статус: v0.3 · Родитель: PROJECT_PLAN.md

## 1. i18n интерфейса доски
- В шаблоне `kanban.html.template`: словарь `UI = {en:{…}, ru:{…}}` + `var LANG='en'` (публичный дефолт; `'ru'` переключается одной правкой в шапке файла, README это документирует) + хелпер `t(key)`.
- Все пользовательские строки через t(): заголовок/подзаголовок/легенда, STAGES/CATS/MODES (id-ключи неизменны — данные и localStorage совместимы), фильтры, «показано X из Y», aria/tooltip, «Семейство».
- Метки updater-а (m-факты) → английские: tests, Python pkg, Go module, … (EXTRA регенерируется, совместимо).
- Инвариант: **ноль кириллицы** в шаблоне и трёх py-скриптах (README.ru.md — исключение). Личный русский канбан владельца не затрагивается.

## 2. Linux-инструкции
- README EN/RU: секция «Scheduled refresh» расширяется: cron (уже есть) + systemd timer (юнит + таймер, `WantedBy=timers.target`, `systemctl --user enable --now`). Приложение остаётся macOS-only — помечено.

## 3. Ускорение сканера (kanban-update.py)
- Для git-репо: список файлов через `git ls-files -z --cached --others --exclude-standard` (tracked + untracked-не-игнорируемые; .gitignore уважается автоматически) → один проход stat/ext/marks по этому списку. Fallback: прежний os.walk со SKIP_DIRS (негитовые папки).
- Семантика f/marks: сегменты пути вместо обхода каталогов (tests/test → tests; .agent-gates; .github/workflows → CI; корневые файлы).
- Консольные сообщения скриптов → английские.

## Критерии приёмки
1. Headless Chrome рендерит доску из /tmp: в DOM есть карточки, стадии EN («Idea / Discovery»), кириллицы в отрендеренном тексте нет.
2. Факты корректны: f == `git ls-files -c -o --exclude-standard | wc -l`; node_modules (в .gitignore) не считается; marks (tests/CI) находятся по сегментам.
3. Скорость: репо с ~20k игнорируемых файлов обновляется < ~5 c.
4. Негитовая папка по-прежнему сканируется fallback-ом.
5. Повторный запуск updater — «No changes.» (идемпотентность сохранена).
6. README EN/RU: LANG-инструкция + systemd-секция; SSOT обновлены.
