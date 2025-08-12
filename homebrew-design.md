# Homebrew配布設計計画

## 1. 統合コマンド設計

### アーキテクチャ: 統合Bashスクリプト

```
mcp-starter (単一実行ファイル)
├── シェル検出ロジック
├── 共通コア機能
├── シェル固有の実装選択
└── エラーハンドリング
```

### シェル検出ロジック

```bash
# 実行中のシェルを検出
detect_shell() {
    # 1. $SHELL環境変数をチェック
    # 2. 親プロセス名をチェック  
    # 3. PS1パターンをチェック
    # 4. デフォルトはbash
}
```

### ファイル構造

```
mcp-starter/
├── bin/
│   └── mcp-starter              # 統合実行ファイル
├── Formula/
│   └── mcp-starter.rb           # Homebrew Formula
├── lib/
│   ├── core.sh                 # 共通コア機能
│   ├── shell-detect.sh         # シェル検出
│   └── templates/              # 設定テンプレート
├── test/
│   ├── formula_test.rb         # Formula テスト
│   └── integration_test.sh     # 統合テスト
├── .github/
│   └── workflows/
│       └── release.yml         # リリース自動化
├── Makefile                    # ビルドプロセス
├── VERSION                     # バージョン管理
└── LICENSE                     # ライセンス
```

## 2. Homebrew Formula設計

### mcp-starter.rb の構造

```ruby
class McpStarter < Formula
  desc "Multi-shell MCP server configuration tool"
  homepage "https://github.com/username/mcp-starter"
  url "https://github.com/username/mcp-starter/archive/v1.0.0.tar.gz"
  sha256 "..."
  license "MIT"
  
  depends_on "node"
  depends_on "python@3.11"
  depends_on "uv"
  
  def install
    bin.install "bin/mcp-starter"
    lib.install "lib"
    man1.install "man/mcp-starter.1"
  end
  
  test do
    system "#{bin}/mcp-starter", "--version"
  end
end
```

## 3. 統合スクリプト設計

### 基本構造

```bash
#!/usr/bin/env bash
set -euo pipefail

VERSION="1.0.0"
SCRIPT_DIR="$(dirname "${BASH_SOURCE[0]}")"
LIB_DIR="${SCRIPT_DIR}/../lib"

# ライブラリ読み込み
source "${LIB_DIR}/shell-detect.sh"
source "${LIB_DIR}/core.sh"

# メイン処理
main() {
    local shell_type
    shell_type=$(detect_current_shell)
    
    case "$shell_type" in
        "bash"|"zsh")
            run_posix_implementation "$@"
            ;;
        "fish")
            run_fish_implementation "$@"
            ;;
        "powershell"|"pwsh")
            run_powershell_implementation "$@"
            ;;
        "nu")
            run_nushell_implementation "$@"
            ;;
        *)
            echo "Warning: Unsupported shell $shell_type, using bash implementation"
            run_posix_implementation "$@"
            ;;
    esac
}

main "$@"
```

## 4. ビルドプロセス

### Makefile

```makefile
VERSION := $(shell cat VERSION)
BINARY := bin/mcp-starter
INSTALL_PATH := /usr/local/bin

.PHONY: build test install clean release

build: $(BINARY)

$(BINARY): lib/*.sh
	mkdir -p bin
	cat lib/header.sh lib/shell-detect.sh lib/core.sh lib/main.sh > $(BINARY)
	chmod +x $(BINARY)
	sed -i 's/__VERSION__/$(VERSION)/g' $(BINARY)

test: build
	./test/integration_test.sh
	
install: build
	cp $(BINARY) $(INSTALL_PATH)

clean:
	rm -rf bin/

release: build test
	gh release create v$(VERSION) $(BINARY)
```

## 5. 依存関係管理

### Homebrew依存関係

```ruby
depends_on "node"           # Cipher用
depends_on "python@3.11"    # Serena用
depends_on "uv"            # Python パッケージマネージャー

# オプション依存関係
uses_from_macos "git"      # Serena インストール用
```

### ランタイム検証

```bash
check_dependencies() {
    local missing_deps=()
    
    command -v node >/dev/null 2>&1 || missing_deps+=("node")
    command -v python3 >/dev/null 2>&1 || missing_deps+=("python3")
    command -v uv >/dev/null 2>&1 || missing_deps+=("uv")
    
    if [ ${#missing_deps[@]} -ne 0 ]; then
        echo "Error: Missing dependencies: ${missing_deps[*]}"
        echo "Install with: brew install ${missing_deps[*]}"
        exit 1
    fi
}
```

## 6. バージョン管理戦略

### セマンティックバージョニング

```
1.0.0  - 初期リリース
1.1.0  - 新機能追加
1.1.1  - バグフィックス
```

### リリースプロセス

1. `VERSION` ファイル更新
2. `CHANGELOG.md` 更新
3. Git tag 作成
4. GitHub Release 作成
5. Formula SHA256 更新

## 7. テスト戦略

### 統合テスト

```bash
#!/usr/bin/env bash
# test/integration_test.sh

test_basic_functionality() {
    local temp_dir
    temp_dir=$(mktemp -d)
    
    cd "$temp_dir"
    mcp-starter test-project typescript
    
    assert_directory_exists "test-project"
    assert_file_exists "test-project/.serena/project.yml"
    assert_file_exists "test-project/memAgent/cipher.yml"
    
    rm -rf "$temp_dir"
}

test_shell_detection() {
    # 各シェルでの動作テスト
    bash -c "mcp-starter --version"
    zsh -c "mcp-starter --version"
    # fish -c "mcp-starter --version"
}
```

## 8. 配布戦略

### Homebrew Tap

```
# カスタムtap作成
https://github.com/username/homebrew-mcp-starter
└── Formula/
    └── mcp-starter.rb

# インストール方法
brew tap username/mcp-starter
brew install mcp-starter
```

### 公式Homebrew Core

```
# PRを homebrew/homebrew-core に提出
# 要件:
# - 30日以上のGitHub stars
# - 30日以上の活発な開発
# - 安定版リリース
```

## 9. ユーザーエクスペリエンス

### インストール

```bash
# Homebrew経由
brew install mcp-starter

# 使用方法（変更なし）
mcp-starter my-project typescript
```

### アップグレード

```bash
brew upgrade mcp-starter
```

### アンインストール

```bash
brew uninstall mcp-starter
```

## 10. 実装フェーズ

### Phase 1: 統合スクリプト作成
- [ ] シェル検出ロジック実装
- [ ] 統合スクリプト作成
- [ ] テストフレームワーク構築

### Phase 2: Formula作成
- [ ] Homebrew Formula作成
- [ ] 依存関係定義
- [ ] インストールテスト

### Phase 3: 自動化
- [ ] GitHub Actions設定
- [ ] リリース自動化
- [ ] CI/CDパイプライン

### Phase 4: 配布
- [ ] Homebrew Tap作成
- [ ] ドキュメント更新
- [ ] コミュニティフィードバック

この設計により、`brew install mcp-starter` でインストール後、`mcp-starter project-name` で任意のシェル環境で動作する統一されたツールが提供されます。