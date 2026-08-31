# AGENTS.md — 本仓库工作规范

## 仓库定位

量化学习与 A 股策略实验仓库。`code/` 是可运行代码，`learning/` 是课程笔记，
两者不要混放。文档与注释使用中文。

## 环境与运行

- Python 解释器固定用仓库根的 `.venv`（Python 3.14；akshare 1.18.91 / pandas 3.0.5 / numpy 2.5.2）
- 资金迁移模型是**包**，不是单文件脚本。运行前先 `cd code`：
  - 基线：`python -m stock_capital_migration`
  - 研究：`python -m stock_capital_migration.research`
- Windows PowerShell 下嵌套引号易碎，复杂逻辑写成临时 .py 文件执行后删除

## 不入库清单（.gitignore 已配置，勿提交）

- `code/outputs/` — 所有脚本输出
- `code/data/` — 本地市场数据缓存
- `__pycache__/` — 字节码缓存

新增脚本的输出必须写入 `code/outputs/`，不得散落在 `code/` 根目录。

## 网络现实（东财接口）

- `push2his.eastmoney.com` 有突发限流：连续请求触发 60 秒级直接断连封锁窗。
  重试+退避+限速已内置于 `data.py::call_with_retry`，不要绕过它另起裸 requests 循环
- 系统代理（127.0.0.1:7897）不转发东财时，先 `$env:NO_PROXY='eastmoney.com'`
- 限流失败是**环境问题不是代码回归**：等几分钟重跑，或用 research 的 `--offline`
  走本地缓存。判断回归看缓存数据上的可复现结果

## pandas 3.x 兼容陷阱

- Copy-on-Write 已默认开启，`DataFrame.values` 可能是**只读视图**：
  `np.fill_diagonal(df.values, ...)` 会抛 `ValueError: underlying array is read-only`，
  必须 `to_numpy(copy=True)` 后重建 DataFrame（见 `model.py::build_distance`）

## 资金迁移包结构约定

- `config / data / features / model / backtest / report` 按职责分层，新增功能先看归属
- `research.py` 通过 `SimpleNamespace` shim 以 `base.X` 前缀引用基线符号，
  正文保持历史写法；改基线函数签名时同步检查 shim 的符号清单

## 变更验收流程

改动资金迁移包后，按序执行：

1. `py_compile` 所有改动模块
2. 导入包并核对符号完整性（`from stock_capital_migration import ...`）
3. CLI 冒烟：`python -m stock_capital_migration --help`（research 同理）
4. 合成数据端到端：构造 6 只 × 130 日假面板，走
   `add_features → backtest → build_snapshot → flow_edges → save_results`，
   校验迁移矩阵资金守恒（流入总和 == 流出总和）
5. 真实数据运行受东财限流约束，失败时明确区分"网络封锁"与"代码回归"，
   不得把限流失败当成模型结论

## 边界

- 不要修改/提交 `.venv/`
- 不要手动删除 `code/data/` 里的缓存（那是长回测期的数据积累）
- 清理"中间产物"指生成物与缓存目录内容；**源码、learning/ 笔记、`.gitignore` 不属于中间产物**
