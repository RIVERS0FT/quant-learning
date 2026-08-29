# 第 1 周第 1 天：Python 开发环境与项目初始化

## 今日目标

- 理解 Python 解释器、包管理器和虚拟环境的职责。
- 创建一个可重复使用的量化研究项目环境。
- 配置编辑器使用正确的 Python 解释器。
- 运行第一个量化研究脚本。

---

## 一、开发环境由什么组成

一个基础 Python 量化环境通常包括：

| 组成 | 作用 |
|---|---|
| Python 解释器 | 执行 `.py` 程序 |
| `pip` | 安装第三方库 |
| 虚拟环境 | 隔离不同项目的依赖 |
| 编辑器或 IDE | 编写、运行和调试代码 |
| Git | 记录学习内容与代码变化 |

量化研究最重要的不是“安装最多的软件”，而是保证环境能够重复创建。

---

## 二、检查 Python

在终端中运行：

```bash
python --version
```

部分系统需要使用：

```bash
python3 --version
```

建议使用 Python 3.11 或更新的稳定版本。

检查 `pip`：

```bash
python -m pip --version
```

优先使用 `python -m pip`，因为它能明确使用当前解释器对应的包管理器。

---

## 三、创建项目目录

```bash
mkdir quant-research
cd quant-research
```

建议的初始结构：

```text
quant-research/
├── README.md
├── src/
├── tests/
├── data/
└── notebooks/
```

目录含义：

- `src/`：可复用的 Python 模块；
- `tests/`：单元测试；
- `data/`：本地研究数据，不应默认全部提交到 Git；
- `notebooks/`：探索性研究；
- `README.md`：记录项目目标、环境和运行方法。

---

## 四、创建虚拟环境

```bash
python -m venv .venv
```

虚拟环境会在项目中创建 `.venv` 目录。

### Windows PowerShell

```powershell
.\.venv\Scripts\Activate.ps1
```

### macOS 或 Linux

```bash
source .venv/bin/activate
```

激活后，终端提示符通常会出现：

```text
(.venv)
```

退出虚拟环境：

```bash
deactivate
```

---

## 五、安装基础工具

```bash
python -m pip install --upgrade pip
python -m pip install numpy pytest
```

查看当前环境中的包：

```bash
python -m pip list
```

记录依赖：

```bash
python -m pip freeze > requirements.txt
```

以后可以通过以下命令恢复环境：

```bash
python -m pip install -r requirements.txt
```

学习阶段应理解：`requirements.txt` 是环境说明，不是代码本身。

---

## 六、配置编辑器

使用 VS Code 时：

1. 安装 Python 扩展；
2. 打开项目目录；
3. 选择项目内 `.venv` 的解释器；
4. 在集成终端确认 `python --version`；
5. 确认运行脚本时使用的是同一解释器。

常见错误是：终端激活了虚拟环境，但编辑器运行按钮仍使用系统 Python。

---

## 七、第一个量化脚本

创建：

```text
src/first_return.py
```

内容：

```python
previous_price = 10.0
current_price = 10.5

simple_return = current_price / previous_price - 1

print(f"前一日价格：{previous_price:.2f}")
print(f"当前价格：{current_price:.2f}")
print(f"简单收益率：{simple_return:.2%}")
```

运行：

```bash
python src/first_return.py
```

简单收益率公式：

$$
R_t=\frac{P_t}{P_{t-1}}-1
$$

---

## 八、环境验证

创建：

```text
src/check_environment.py
```

```python
import platform
import sys

import numpy as np

print("Python版本：", sys.version)
print("操作系统：", platform.platform())
print("NumPy版本：", np.__version__)
print("解释器路径：", sys.executable)
```

重点检查 `sys.executable` 是否指向项目中的 `.venv`。

---

## 九、常见问题

### `python` 命令不存在

尝试：

```bash
python3 --version
```

或重新安装 Python，并确保加入系统环境变量。

### 无法激活 PowerShell 脚本

可能需要调整当前用户的执行策略。应先理解系统安全策略，再执行相应设置，不要盲目复制管理员命令。

### 安装成功但无法导入

检查：

```bash
python -m pip --version
python -c "import numpy; print(numpy.__version__)"
```

确保安装包和运行程序使用同一个解释器。

---

## 今日练习

1. 创建 `quant-research` 项目目录。
2. 创建并激活 `.venv`。
3. 安装 `numpy` 和 `pytest`。
4. 运行 `first_return.py`。
5. 使用 `sys.executable` 确认解释器路径。
6. 生成 `requirements.txt`。

---

## 今日检查清单

- [ ] 能解释解释器、`pip` 和虚拟环境的区别。
- [ ] 能创建、激活和退出虚拟环境。
- [ ] 编辑器与终端使用同一个解释器。
- [ ] 能运行第一个收益率程序。
- [ ] 能通过依赖文件重建环境。
