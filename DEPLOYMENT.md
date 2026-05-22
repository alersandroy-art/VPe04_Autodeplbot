# Деплой и настройка секретов

Инструкция по настройке автоматического деплоя через GitHub Actions  
(файл workflow: `.github/workflows/deploy.yml`).

## Как это работает

1. **Джоба `build-and-push`** — собирает Docker-образ и публикует в GitHub Container Registry (GHCR).
2. **Джоба `deploy`** — по SSH подключается к серверу, скачивает образ и запускает контейнер `time-api`.

Запуск при push в ветки `main` и `develop`, а также вручную: **Actions → Build and Deploy → Run workflow**.

Образ: `ghcr.io/<ваш-логин>/vpe04-autodeplbot`

---

## Секреты репозитория

Добавляются здесь:

**GitHub → репозиторий → Settings → Secrets and variables → Actions → New repository secret**

| Секрет | Обязательный | Описание |
|--------|:------------:|----------|
| `SSH_HOST` | да | IP сервера VPe05: `89.108.98.6` |
| `SSH_USER` | да | Пользователь SSH (например `root` или `deploy`) |
| `SSH_PRIVATE_KEY` | да | Приватный SSH-ключ (весь текст файла, с `BEGIN` и `END`) |
| `GHCR_TOKEN` | да* | Токен для `docker login` на сервере |
| `SSH_PORT` | нет | Порт SSH (по умолчанию `22`) |

\* Если образ в GHCR **публичный**, pull иногда работает и без логина, но шаг `docker login` в workflow всё равно ожидает непустой `GHCR_TOKEN`. Рекомендуется всегда задавать этот секрет.

`GITHUB_TOKEN` для push образа в GHCR настраивать **не нужно** — Actions предоставляет его автоматически.

---

## Пошаговая настройка

### 1. SSH-ключ

На своём компьютере (если ключа ещё нет):

```powershell
ssh-keygen -t ed25519 -C "github-deploy" -f $env:USERPROFILE\.ssh\deploy_key
```

- **Публичный ключ** (`deploy_key.pub`) — добавьте на сервер в `~/.ssh/authorized_keys` пользователя `SSH_USER`.
- **Приватный ключ** (`deploy_key`) — целиком скопируйте в секрет `SSH_PRIVATE_KEY`.

Проверка подключения:

```powershell
ssh VPe05
```

### 2. Секреты SSH на GitHub

| Секрет | Что вставить |
|--------|----------------|
| `SSH_HOST` | IP или домен сервера |
| `SSH_USER` | имя пользователя SSH |
| `SSH_PRIVATE_KEY` | содержимое приватного ключа |
| `SSH_PORT` | `22` (или другой порт, если не стандартный) |

### 3. Токен GHCR (`GHCR_TOKEN`)

Нужен для входа в реестр на сервере при `docker pull`.

1. GitHub → **Settings** (профиля) → **Developer settings** → **Personal access tokens**.
2. Создайте **Fine-grained** или **Classic** токен.
3. Права (минимум):
   - `read:packages` — скачивание образа на сервере;
   - при **приватном** пакете может понадобиться также `write:packages` для сборки (в Actions используется `GITHUB_TOKEN`).

4. Скопируйте токен в секрет репозитория `GHCR_TOKEN`.

**Через GitHub CLI** (если установлен `gh`):

```powershell
gh secret set GHCR_TOKEN --repo alersandroy-art/VPe04_Autodeplbot
# вставьте токен при запросе
```

Аналогично для остальных секретов:

```powershell
gh secret set SSH_HOST --body "ВАШ_IP"
gh secret set SSH_USER --body "root"
gh secret set SSH_PORT --body "22"
Get-Content $env:USERPROFILE\.ssh\deploy_key -Raw | gh secret set SSH_PRIVATE_KEY
```

### 4. Требования к серверу

На VPS должны быть установлены:

- **Docker**
- SSH-доступ для пользователя из `SSH_USER`
- Пользователь в группе `docker` (или root)

Проверка:

```bash
docker --version
```

Порт **8000** на сервере должен быть свободен (контейнер публикуется как `8000:8000`).

---

## Проверка после настройки

1. **Actions** → **Build and Deploy** → **Run workflow** (ветка `develop` или `main`).
2. Обе джобы должны завершиться зелёным статусом.
3. API на сервере **VPe05** (`89.108.98.6`):
   - http://89.108.98.6:8000/time
   - http://89.108.98.6:8000/date
   - Grafana (логи): http://89.108.98.6:3000

---

## Частые ошибки

| Ошибка в логах | Причина | Решение |
|----------------|---------|---------|
| `missing server host` | Не задан `SSH_HOST` | Добавьте секрет |
| `missing server host` / пустой username | Нет `SSH_USER` или `SSH_PRIVATE_KEY` | Проверьте секреты |
| `Bind for 0.0.0.0:8000 failed` | Порт 8000 занят | Остановите другой контейнер или смените `APP_PORT` в workflow |
| Ошибка `docker login` | Пустой или неверный `GHCR_TOKEN` | Создайте PAT с `read:packages` |
| Ошибка `docker pull` | Приватный образ без токена | Задайте `GHCR_TOKEN` или сделайте пакет публичным в GHCR |

Просмотр логов: **Actions** → выберите запуск → джоба → шаг с ошибкой.

---

## Публичный vs приватный образ в GHCR

После первого успешного push:

**GitHub → ваш профиль → Packages → `vpe04-autodeplbot` → Package settings**

- **Public** — проще для учебного проекта, `docker pull` без сложной авторизации.
- **Private** — обязателен рабочий `GHCR_TOKEN` с `read:packages` на сервере.

---

## Ручной деплой на сервере (без Actions)

```bash
echo "ВАШ_GHCR_TOKEN" | docker login ghcr.io -u ВАШ_ЛОГИН_GITHUB --password-stdin
docker pull ghcr.io/alersandroy-art/vpe04-autodeplbot:latest
docker stop time-api 2>/dev/null || true
docker rm time-api 2>/dev/null || true
docker run -d --name time-api --restart unless-stopped -p 8000:8000 ghcr.io/alersandroy-art/vpe04-autodeplbot:latest
```

---

## Список секретов (чеклист)

- [ ] `SSH_HOST`
- [ ] `SSH_USER`
- [ ] `SSH_PRIVATE_KEY`
- [ ] `GHCR_TOKEN`
- [ ] `SSH_PORT` (если не 22)

После заполнения — push в `develop`/`main` или ручной запуск workflow.
