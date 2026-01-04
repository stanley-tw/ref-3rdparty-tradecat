# 🐱 TradeCat 一键安装

> 复制提示词到 AI 助手，AI 会生成完整安装脚本，你只需执行一次

---

## 📋 安装提示词

复制以下内容到 **Claude / ChatGPT**：

```
生成一个 TradeCat 全自动安装脚本，要求：

1. 系统: Ubuntu 22.04/24.04
2. 安装: TimescaleDB 2.x + TA-Lib + Python 3.10+
3. 项目: github.com/tukuaiai/tradecat
4. 数据库: postgres/postgres@localhost:5432/market_data

脚本要求：
- 一个 bash 脚本，复制执行即可
- 自动检测已安装的组件，跳过
- 每步有清晰的进度提示
- 最后输出验证结果
- 出错时显示具体原因

脚本结构：
1. 检查系统
2. 安装系统依赖
3. 安装 TimescaleDB
4. 创建数据库
5. 安装 TA-Lib
6. 克隆项目到 ~/.projects/tradecat
7. 运行 ./scripts/init.sh
8. 验证安装

直接输出完整脚本，不要解释。
```

---

## 🚀 执行安装

AI 生成脚本后，在 Ubuntu 终端执行：

```bash
# 1. 保存脚本
cat > install_tradecat.sh << 'SCRIPT'
# 粘贴 AI 生成的脚本内容
SCRIPT

# 2. 执行
chmod +x install_tradecat.sh
./install_tradecat.sh
```

---

## ✅ 验证安装

安装完成后检查：

```bash
cd ~/.projects/tradecat
./scripts/verify.sh
```

应显示：
```
✅ TimescaleDB 连接正常
✅ TA-Lib 安装正常
✅ 项目初始化完成
✅ 所有服务就绪
```

---

## ⚙️ 配置 Bot (必须)

```bash
# 编辑配置，填入你的 Telegram Bot Token
vim ~/.projects/tradecat/services/telegram-service/config/.env
```

```ini
TELEGRAM_BOT_TOKEN=你的Token
# 如需代理
HTTPS_PROXY=http://127.0.0.1:7890
```

---

## 🎬 启动服务

```bash
cd ~/.projects/tradecat
./scripts/start.sh daemon    # 启动
./scripts/start.sh status    # 查看状态
```

---

## 📥 导入历史数据 (可选)

从 [HuggingFace](https://huggingface.co/datasets/123olp/binance-futures-ohlcv-2018-2026) 下载后：

```bash
cd ~/.projects/tradecat/backups/timescaledb
zstd -d candles_1m.bin.zst -c | psql -d market_data -c "COPY market_data.candles_1m FROM STDIN WITH (FORMAT binary)"
```

---

## ❓ 问题反馈

- Telegram 群: [@glue_coding](https://t.me/glue_coding)
- 频道: [@tradecat_ai_channel](https://t.me/tradecat_ai_channel)
