# 第 1 周第 6 天：Git 基础与规范提交

## 今日目标

- 理解工作区、暂存区和提交历史。
- 掌握 `init`、`status`、`add`、`commit`、`diff` 和 `log`。
- 配置适合 Python 项目的 `.gitignore`。
- 形成小步、可解释、可回退的提交习惯。

---

## 一、Git 解决什么问题

Git 用于记录文件变化。它可以回答：

- 哪些文件发生了变化？
- 谁在什么时候修改了什么？
- 为什么进行这次修改？
- 如何回到之前的状态？

量化研究还需要 Git 记录：

- 数据处理口径；
- 策略参数变化；
- 实验代码版本；
- 学习笔记和研究结论。

大型原始数据通常不直接提交到 Git。

---

## 二、初始化仓库

```bash
git init
git status
```

配置身份：

```bash
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
```

查看配置：

```bash
git config --list
```

---

## 三、三个区域

```text
工作区 → 暂存区 → 提交历史
```

- 工作区：正在编辑的文件；
- 暂存区：准备进入下一次提交的变化；
- 提交历史：已经保存的版本。

查看状态：

```bash
git status
```

加入暂存区：

```bash
git add README.md
git add src/returns.py
```

提交：

```bash
git commit -m "实现简单收益率函数"
```

---

## 四、检查变化

查看尚未暂存的变化：

```bash
git diff
```

查看已暂存的变化：

```bash
git diff --staged
```

提交前推荐流程：

```text
git status
→ git diff
→ git add 指定文件
→ git diff --staged
→ git commit
```

不要在不了解变化范围时机械使用 `git add .`。

---

## 五、查看历史

```bash
git log
git log --oneline
git log --oneline --graph --decorate
```

查看某次提交：

```bash
git show <commit-sha>
```

提交哈希是提交的唯一标识，通常使用前几位即可定位。

---

## 六、`.gitignore`

创建 `.gitignore`：

```gitignore
# Python
__pycache__/
*.py[cod]

# Virtual environment
.venv/

# Test and tool caches
.pytest_cache/
.mypy_cache/
.ruff_cache/

# Editor
.vscode/
.idea/

# Operating system
.DS_Store
Thumbs.db

# Local data and secrets
data/raw/
.env
```

注意：已经被 Git 跟踪的文件，后来加入 `.gitignore` 不会自动停止跟踪。

---

## 七、好的提交信息

推荐使用简洁的动词短语：

```text
添加价格文件读取函数
修复零价格校验
补充收益率函数测试
更新第一周学习笔记
```

避免：

```text
update
修改
test
最终版本2
```

一次提交应尽量只完成一个清晰目的。

---

## 八、撤销工作区修改

查看变化后，确定不要某个文件的未提交修改：

```bash
git restore path/to/file.py
```

取消暂存但保留工作区修改：

```bash
git restore --staged path/to/file.py
```

这些操作可能丢失内容，执行前必须先检查 `git diff`。

不要随意使用危险的强制重置命令。

---

## 九、分支概念

分支是独立的开发线。

查看分支：

```bash
git branch
```

创建并切换分支：

```bash
git switch -c feature/return-function
```

切回主分支：

```bash
git switch main
```

学习项目初期可以先理解分支概念，后续再系统学习合并和 Pull Request。

---

## 十、首次提交建议

```bash
git status
git add README.md .gitignore requirements.txt src tests
git diff --staged
git commit -m "初始化量化研究项目"
git log --oneline
```

提交前确认没有：

- 虚拟环境目录；
- API 密钥；
- 账号密码；
- 大型原始数据；
- 无关临时文件。

---

## 十一、Git 与可重复研究

一个研究结果至少应能关联到：

- 代码提交；
- 参数配置；
- 数据口径；
- 运行日期；
- 输出结果。

Git 能记录代码，但不能自动保证研究正确。仍需配合测试、数据版本和实验日志。

---

## 今日练习

1. 在项目中运行 `git init`。
2. 创建 `.gitignore`。
3. 使用 `git status` 检查变化。
4. 只暂存本次课程相关文件。
5. 使用 `git diff --staged` 检查提交内容。
6. 创建一次清晰提交并查看日志。

---

## 今日检查清单

- [ ] 能解释工作区、暂存区和提交历史。
- [ ] 会在提交前检查差异。
- [ ] `.venv` 和本地敏感数据不会进入仓库。
- [ ] 提交信息能够说明变化目的。
- [ ] 不使用危险命令处理不理解的变化。
