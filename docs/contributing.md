# Discord RSS Bot コントリビューションガイド

このガイドでは、Discord RSS Botプロジェクトへの貢献方法について説明します。

## 目次

1. [開発環境のセットアップ](#開発環境のセットアップ)
2. [コーディング規約](#コーディング規約)
3. [テスト](#テスト)
4. [プルリクエスト](#プルリクエスト)
5. [機能追加のガイドライン](#機能追加のガイドライン)
6. [バグ報告](#バグ報告)

## 開発環境のセットアップ

### 前提条件

- Python 3.8以上
- Git
- （オプション）Docker

### リポジトリのクローン

```bash
git clone https://github.com/yourusername/discord-rss-bot.git
cd discord-rss-bot
```

### 仮想環境のセットアップ

```bash
python -m venv venv
source venv/bin/activate  # Linuxの場合
# または
venv\Scripts\activate  # Windowsの場合
```

### 依存パッケージのインストール

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt  # 開発用パッケージ
```

### 環境変数の設定

```bash
cp .env.example .env
```

`.env`ファイルを編集して、必要な環境変数を設定します。

## コーディング規約

このプロジェクトでは、PEP 8コーディング規約に従っています。以下の点に特に注意してください：

- インデントには4スペースを使用
- 行の最大長は100文字
- クラス名はCamelCase、関数名とメソッド名はsnake_case
- モジュールレベルの定数は大文字のSNAKE_CASE
- docstringはGoogle形式で記述

### コードフォーマット

コードをフォーマットするには、以下のコマンドを実行します：

```bash
black .
isort .
```

### リンター

コードの品質をチェックするには、以下のコマンドを実行します：

```bash
flake8
pylint discord_rss_bot
```

## テスト

### テストの実行

すべてのテストを実行するには、以下のコマンドを実行します：

```bash
python run_tests.py
```

特定のテストを実行するには、以下のコマンドを実行します：

```bash
python -m unittest tests.test_config_manager
```

### テストの作成

新しい機能を追加する場合は、対応するテストも作成してください。テストファイルは`tests`ディレクトリに配置し、ファイル名は`test_*.py`の形式にしてください。

テストクラスは`unittest.TestCase`を継承し、テストメソッドは`test_*`の形式にしてください。

```python
import unittest

class TestMyFeature(unittest.TestCase):
    def setUp(self):
        # テスト前の準備
        pass
        
    def tearDown(self):
        # テスト後のクリーンアップ
        pass
        
    def test_my_function(self):
        # テストコード
        result = my_function()
        self.assertEqual(result, expected_result)
```

## プルリクエスト

### ブランチ戦略

- `main`: 安定版のコード
- `develop`: 開発版のコード
- 機能ブランチ: `feature/feature-name`
- バグ修正ブランチ: `bugfix/bug-name`

### プルリクエストの作成手順

1. 新しいブランチを作成します：

```bash
git checkout -b feature/my-feature
```

2. 変更を加えます。

3. テストを実行して、すべてのテストがパスすることを確認します：

```bash
python run_tests.py
```

4. 変更をコミットします：

```bash
git add .
git commit -m "Add my feature"
```

5. 変更をプッシュします：

```bash
git push origin feature/my-feature
```

6. GitHubでプルリクエストを作成します。

### プルリクエストのレビュー

プルリクエストは以下の基準でレビューされます：

- コードの品質
- テストの有無と品質
- ドキュメントの更新
- 既存の機能との互換性

## 機能追加のガイドライン

新しい機能を追加する場合は、以下のガイドラインに従ってください：

1. 機能の目的と仕様を明確にする
2. 既存のコードベースとの整合性を確認する
3. 必要なテストを作成する
4. ドキュメントを更新する

### モジュール追加のガイドライン

新しいモジュールを追加する場合は、以下の構造に従ってください：

```
module_name/
├── __init__.py
├── main_class.py
└── utils.py
```

`__init__.py`ファイルでは、モジュールの公開インターフェースを定義します：

```python
from .main_class import MainClass
from .utils import utility_function

__all__ = ["MainClass", "utility_function"]
```

## バグ報告

バグを報告する場合は、以下の情報を含めてください：

- バグの詳細な説明
- 再現手順
- 期待される動作
- 実際の動作
- 環境情報（OSバージョン、Pythonバージョン、依存パッケージのバージョンなど）
- エラーメッセージやスタックトレース（ある場合）

バグ修正のプルリクエストを作成する場合は、以下の手順に従ってください：

1. バグ修正ブランチを作成します：

```bash
git checkout -b bugfix/bug-name
```

2. バグを修正します。

3. テストを追加して、バグが修正されたことを確認します。

4. 変更をコミットしてプッシュします。

5. プルリクエストを作成します。

