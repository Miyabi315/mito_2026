# mito_2026

医療記録から rule-based で構造抽出し、Care Graph と Process Timeline を生成する研究プロトタイプです。

## Current Status

- Step1: 医療記録入力（完了）
- Step2: entity extraction（完了）
- Step3: event extraction（完了）
- Step4: graph JSON生成（完了）
- Step5: timeline生成（完了）
- Step6: graph visualization（完了）
- Step7: UI改善（timeline表示・evidenceパネルを実装）

## Backend

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
uvicorn backend.api.main:app --reload
```

FastAPI Docs:

- `http://127.0.0.1:8000/docs`

主なAPI:

- `POST /records/normalize`
- `POST /extraction/entities`
- `POST /extraction/events`
- `POST /graph/care`
- `POST /timeline/process`

## Frontend

```bash
cd frontend
npm install
npm run dev
```

ブラウザ:

- `http://127.0.0.1:3000`

フロントは `POST /graph/care` を呼び出して React Flow で Care Graph を表示します。
ノード/エッジをクリックすると evidence を右ペインで確認できます。

## Test / Lint

```bash
. .venv/bin/activate
pytest -q
ruff check .
```
