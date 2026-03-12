# AGENTS.md

## 1. プロジェクトの概要

本プロジェクトは、医療記録（カルテ・看護記録・オーダーなど）から  
関係者・医療イベント・進行状態を抽出し、患者中心のケアグラフと  
医療プロセスタイムラインを生成する研究プロトタイプである。

入力  
- カルテ
- 看護記録
- オーダー記録
- その他医療テキスト

出力  
- Care Graph（関係図）
- Process Timeline（進行チャート）

本プロジェクトの価値は

医療記録 → 構造抽出 → グラフ生成

の変換エンジンにあり、  
単なる可視化ダッシュボードではない。


---

## 2. このプロジェクトでやること

以下の機能を実装する。

- 医療記録の入力
- 関係者（Actor）抽出
- 医療イベント抽出
- 状態抽出
- ケアグラフ生成
- 医療プロセスタイムライン生成
- 抽出結果の可視化
- 抽出結果と根拠テキストの紐付け


---

## 3. このプロジェクトでやらないこと

以下は本プロジェクトの対象外。

- 診断推定
- 治療提案
- 医療意思決定支援
- 実患者データの使用
- 推測によるデータ補完


---

## 4. 抽出パイプライン

medical text input  
↓  
entity extraction  
↓  
role classification  
↓  
event extraction  
↓  
state extraction  
↓  
graph generation  
↓  
timeline generation  

入力は複数テキストを想定する。

例

- カルテ
- 看護記録
- オーダー記録

これらを統合して解析する。


---

## 5. UI構成

最低限の画面構成

### Record Input
医療記録の入力画面

### Care Graph
患者中心の関係図

ノード

- patient
- staff
- event

エッジ

- responsible
- performed
- requested

### Process Timeline
医療イベントの時系列表示


---

## 6. 開発優先順位

実装順序

1. 医療記録入力
2. entity extraction
3. event extraction
4. graph JSON生成
5. timeline生成
6. graph visualization
7. UI改善


---

## 7. 技術スタック

Backend  
- Python  
- FastAPI  

Extraction  
- rule-based extraction  
- regex / dictionary  

Frontend  
- React  
- Next.js  

Graph visualization  
- React Flow  


---

## 8. リポジトリ構成

repo
├ backend
│  ├ extraction
│  ├ graph
│  ├ timeline
│  └ api
├ frontend
│  ├ components
│  ├ graph
│  ├ timeline
│  └ pages
├ data
│  └ sample_records
├ docs
│  └ architecture
└ tests


---

## 9. 実装ルール

- 抽出ロジックは rule-based を基本とする
- LLM は使用しない
- 抽出結果は必ず元テキストに紐づける
- グラフ生成は決定的処理とする
- UIは抽出ロジックを持たない
- extraction → graph → visualization の分離を保つ


---

## 10. エージェントへの作業指示

1. backend の extraction モジュールを実装する
2. extraction 結果を JSON に構造化する
3. graph generator を実装する
4. timeline generator を実装する
5. API を作成する
6. frontend で graph を表示する
7. timeline UI を作成する

抽出ロジック変更時は sample_records で動作確認すること。


---

## 11. 実行コマンド

backend dev  
uvicorn backend.api.main:app --reload

frontend dev  
npm run dev

test  
pytest

lint  
ruff check .


---

## 12. レビュー基準

- 抽出 → 構造化 → 可視化 の分離が守られているか
- 推測でデータを生成していないか
- 医療判断を含む処理が入っていないか
- evidence テキストが保持されているか
- UI中心の実装になっていないか