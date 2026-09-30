# Bash / tmux / YAML / Git 速查（基于 C2C 复现实操整理）

整理日期：2026-09-27。所有例子都来自第 1 周任务 3、4 的实际操作。

---

## 1. 基本概念

- **终端（terminal）**：显示文字、接收键盘输入的窗口。Ubuntu 窗口和 VS Code 的 Terminal 都是终端，连接的是同一个 WSL 环境，功能等价。
- **Shell**：终端里解释命令的程序。Ubuntu 默认是 **bash**（Bourne Again SHell）。今天写的都是 bash 命令，写成文件就是 shell 脚本。
- `python - <<'EOF' ... EOF` 和 `python -c "..."` 里面写的是 **Python**，bash 只负责把代码交给 Python 执行。

提示符 `(rosetta) shiro@cshi34:~/C2C$`：

| 部分 | 含义 |
|---|---|
| `(rosetta)` | 当前 conda 环境 |
| `shiro@cshi34` | 用户名@机器名 |
| `~/C2C` | 当前目录（`~` = `/home/shiro`） |
| `$` | 普通用户提示符 |

---

## 2. 命令的基本结构

```
命令   选项        参数
ls     -la         local/final_results/task3_receiver_only/
head   -n 40       local/logs/task3_smoke.log
```

- **选项**控制"怎么做"：短选项 `-n`，长选项 `--update=none`；短选项可合写，`-la` = `-l -a`。
- **参数**告诉"对什么做"，通常是文件或目录。
- 查帮助：`命令 --help` 或 `man 命令`（按 `q` 退出）。

---

## 3. 常用命令（按用途）

### 3.1 文件和目录

| 命令 | 例子 | 含义 |
|---|---|---|
| `cd` | `cd ~/C2C` | 进入目录 |
| `pwd` | `pwd` | 显示当前目录 |
| `ls` | `ls -la 目录` | 列出内容；`-l` 详细信息，`-a` 含隐藏文件 |
| `mkdir -p` | `mkdir -p local/logs` | 建目录；父目录不存在时一并创建，已存在不报错 |
| `cp` | `cp --update=none 源 目标` | 复制；目标已存在时不覆盖（旧写法 `-n` 会报 warning） |
| `mv` | `mv 旧名 新名` / `mv 文件 目录/` | 移动或重命名，不删除任何东西 |
| `code` | `code 文件` | 用 VS Code 打开 |

原则：不用 `rm -rf`；需要"清理"时用 `mv` 移到子目录。

### 3.2 查看文件

| 命令 | 例子 | 含义 |
|---|---|---|
| `cat -n` | `cat -n recipe/eval_recipe/unified_eval.yaml` | 显示整个文件，带行号 |
| `head -n N` | `head -n 40 日志` | 前 N 行（启动、加载信息） |
| `tail -n N` | `tail -n 12 日志` | 后 N 行（最终结果、耗时） |
| `sed -n 'a,bp'` | `sed -n '212,262p' rosetta/utils/evaluate.py` | 只显示第 a–b 行（`p` = print） |
| `diff` | `diff 模板 我的` | 逐行比较，只输出不同处 |

**读 diff 输出**：`2,3c2,3` = 左边第 2–3 行被改成（change）右边第 2–3 行；`<` 开头是左文件，`>` 开头是右文件；另有 `a`（add）、`d`（delete）。

### 3.3 搜索

| 命令 | 例子 | 含义 |
|---|---|---|
| `find` | `find ~ -maxdepth 5 -path "*script/evaluation/unified_evaluator.py"` | 按文件名/路径找文件 |
| `grep` | `grep -n "max_new_tokens" 文件` | 在文件内容里找包含某模式的行 |

**grep** 名字来自 `g/re/p`（global / regular expression / print）。

| 用法 | 场景 |
|---|---|
| `grep -c "accuracy:" 日志` | `-c` 计数。每跑完一个学科多一行 accuracy，数到 58 即结束 → **查进度的原理** |
| `grep -n "关键词" 文件` | `-n` 显示行号，接着用 `sed -n` 看上下文 |
| `grep -rln "two_stage" rosetta script` | `-r` 递归目录，`-l` 只列文件名 |
| `grep -oE "evaluated on [0-9]+ ..." 日志` | `-o` 只输出匹配部分，`-E` 扩展正则；`[0-9]+` = 一个或多个数字 |
| `grep "A\|B" 文件` | 匹配 A 或 B |
| `... \| grep -v "\.pyc"` | `-v` 排除匹配的行 |

**排查代码的套路**：`grep -n` 定位关键词所在行 → `sed -n '起,止p'` 打印那一段完整代码。

### 3.4 运行程序

| 写法 | 含义 |
|---|---|
| `python script/evaluation/unified_evaluator.py --config xxx.yaml` | 运行脚本，`--config xxx.yaml` 是传给它的参数 |
| `python -c "代码"` | 执行一行 Python |
| `python - <<'EOF' ... EOF` | 执行多行 Python（见 §6） |
| `time 命令` | 结束后报告耗时；`real` 是实际经过时间（记录这个） |

---

## 4. 变量

```bash
D=local/final_results/task4_t2t
mkdir -p $D/smoke_B_comm256
```

- **`=` 两边不能有空格**（`D = xxx` 会把 `D` 当成命令执行而报错）。
- 使用时加 `$`。
- `${F}_summary.json`：花括号标明变量名到哪里结束。写成 `$F_summary.json` 会去找名为 `F_summary` 的变量（为空）。
- 变量只在当前终端有效。换终端、新开 tmux 会话都要重新定义，也要重新 `cd` 和 `conda activate`。

---

## 5. 连接命令：`&&`、`|`、`2>&1`、`( )`

以全量评测命令为例：

```bash
( time python script/evaluation/unified_evaluator.py --config recipe/eval_recipe/my_receiver.yaml ) 2>&1 | tee local/logs/task3_full.log
```

| 片段 | 含义 |
|---|---|
| `( ... )` | 在子 shell 里运行，这样 `time` 的输出也能被后面的重定向捕获 |
| `2>&1` | 程序有两个输出通道：1 = 标准输出（正常打印），2 = 标准错误（报错、警告、进度条）。把 2 并入 1，使它们也进日志 |
| `\|`（管道） | 左边命令的输出作为右边命令的输入 |
| `tee 文件` | 屏幕照常显示，同时写入文件（T 形三通） |

```bash
cd ~/C2C && conda activate rosetta
```

`&&`：前一个命令成功才执行后一个。`cd` 失败时不会在错误目录里继续操作。

管道组合示例（统计评测题数与跳过题数）：

```bash
grep -oE "evaluated on [0-9]+ samples, skipped [0-9]+" $LOG | awk '{n+=$3; s+=$6} END{print "evaluated:", n, " skipped:", s}'
```

1. `grep` 抽出每行的 "evaluated on 数字 samples, skipped 数字"；
2. `awk` 按空格切列，累加第 3 列和第 6 列，最后打印。`awk` 是处理按列文本的小工具。

---

## 6. heredoc：`<<EOF` 与 `<<'EOF'`

```bash
python - <<EOF          # 不加引号：bash 先把 ${F} 替换成实际值，再交给 Python
df = pd.read_csv("${F}_cot.csv")
EOF

python - <<'EOF'        # 加单引号：内容原样交给 Python，bash 不做替换
f = sorted(glob.glob("local/final_results/task4_t2t/two_stage_*_cot.csv"))[-1]
EOF
```

- `python -` 的 `-` 表示"从标准输入读代码"，heredoc 把两个 `EOF` 之间的内容作为标准输入送进去。
- 需要 bash 变量时用不加引号的写法；推荐在 Python 里用 `glob` 自己找文件，配合加单引号的写法，更稳妥。
- 结尾 `EOF` 必须**单独一行、行首无空格**。粘贴时和下一行粘在一起（如 `EOFnt(...)`）会出错。

---

## 7. 通配符 `*`

```bash
mv $D/two_stage_mmlu-redux_generate_20260927_164310_* $D/smoke_B_comm256/
```

`*` 匹配任意长度文字，一次移动 `_cot.csv`、`_length.json`、`_summary.json` 三个文件。

---

## 8. 省力技巧

| 按键/命令 | 作用 |
|---|---|
| `Tab` | 自动补全文件名和路径，避免拼写错误 |
| `↑` | 调出上一条命令 |
| `Ctrl+C` | 中断当前程序（**tmux 里评测时不要按**） |
| `Ctrl+L` / `clear` | 清屏 |
| `#` | 注释 |

---

## 9. tmux

**终端复用器**（terminal multiplexer）。命令运行在 tmux 后台服务器创建的会话里，终端窗口关闭、VS Code 重启都不影响它。

| 命令 | 作用 |
|---|---|
| `tmux new -s 名字` | 新建会话并进入（`-s` = session name，名字随意，**与 yaml 的 `eval:` 无关**） |
| `Ctrl+B` 然后 `D` | 离开（detach），程序继续后台运行 |
| `tmux ls` | 列出会话 |
| `tmux attach -t 名字` | 回到会话 |
| 会话里输入 `exit` | 结束会话 |
| `Ctrl+B` 然后 `[` | 翻页模式（方向键/PgUp），`q` 退出 |

注意：
- 已存在同名会话时 `tmux new -s eval` 会报 `duplicate session`，先 `tmux ls` 再决定 attach 还是新建。
- tmux 是新 shell，进去后要重新 `cd ~/C2C && conda activate rosetta`。
- Windows 睡眠会让 WSL 暂停。长任务前把睡眠时间调长，并保留一个 Ubuntu 窗口开着。

---

## 10. YAML

YAML 是**配置文件格式**，是写给程序读的"实验参数单"。它本身不做任何事，由 Python 代码读取后决定行为。

```yaml
model:                          # 键后面跟冒号，下一层要缩进
  model_name: Rosetta           # 键: 值
  rosetta_config:
    is_do_alignment: false      # 布尔值
    checkpoints_dir: local/...  # 字符串
  # model_name: two_stage       # # 开头是注释，程序读不到
eval:
  gpu_ids: [0]                  # 列表
```

- **缩进决定层级**，只能用空格，不能用 Tab。
- "注释掉/取消注释" = 行首加/删 `#`。作者用这种方式在模板里切换模式。
- **yaml 里没写的参数不等于不存在**：代码里可能有默认值。例：`communication_max_new_tokens` 没写时，代码默认 1024。

检查配置的两种方式：

| 方式 | 检查什么 |
|---|---|
| `diff 模板 我的` | 文本层面：改了哪几行，有没有误改 |
| `python -c "import yaml; c=yaml.safe_load(open('...')); print(c['eval'].get('limit'))"` | 解析层面：程序实际读到的值（能发现缩进错误） |

`.get('键')` 在键不存在时返回 `None`；`['键']` 会报 `KeyError`。

---

## 11. 分析结果常用的 Python 库

| 库 | 作用 |
|---|---|
| `glob` | 按通配符找文件：`glob.glob("local/.../*_cot.csv")` |
| `pandas`（`pd`） | 把 csv 读成表（DataFrame）；`value_counts()` 看分布，`mean()` 算准确率 |
| `yaml` | 解析 yaml |
| `re` | 正则表达式，如从 `cot_output` 里抽背景文本 |
| `transformers` | 加载 tokenizer 数 token |

`sorted(glob.glob(...))[-1]` 取文件名排序后的最后一个，也就是时间戳最新的结果。这也是冒烟测试结果要 `mv` 走的原因之一。

pred 分布统计模板：

```bash
python - <<'EOF'
import pandas as pd, glob
f = sorted(glob.glob("local/final_results/task4_t2t/two_stage_*_cot.csv"))[-1]
df = pd.read_csv(f); print(f, df.shape)
print("pred:", df["pred"].value_counts(dropna=False).to_dict())
print("true:", df["true_answer"].value_counts(dropna=False).to_dict())
print("acc:", df["is_correct"].mean())
EOF
```

---

## 12. 一个评测任务的标准流程

| 步骤 | 做什么 | 关键命令 |
|---|---|---|
| 1. 准备配置 | 从**原模板**复制，只改本任务需要的行 | `cp --update=none`、`code` |
| 2. 检查配置 | 文本层面 + 解析层面 | `diff`、`python -c "yaml.safe_load..."` |
| 3. 冒烟测试 | `limit: 5`，运行、计时、保存日志 | `( time python ... ) 2>&1 \| tee 日志` |
| 4. 检查冒烟结果 | 看启动日志和最终结果；**抽查数据**（抽取是否正确、实际输入是什么） | `head`、`tail`、`pandas` |
| 5. 整理 | 冒烟结果移到子目录；`limit` 注释回去；重做步骤 2 | `mv` |
| 6. 全量评测 | 在 tmux 里运行 | `tmux ls/new/attach`、`grep -c` |
| 7. 核对与记录 | 与论文对比，统计分布，写周记录，git commit | `tail`、`pandas`、`git` |

说明：
- "冒烟测试"是一种**做法**（先小规模跑通再投入大量时间），不是代码自带的功能。我们借用的是代码支持的 `limit` 参数（每学科最多评测 N 题）。
- 全量评测与冒烟测试的唯一区别是有没有 `limit`。
- **步骤 4 最容易被跳过，但最重要**：T2T 的背景上限问题就是在这一步发现的。分数正常不等于设置正确；日志里记录的内容也不一定是真正参与计算的内容。

---

## 13. Git 常用命令

### 13.1 三个区域

```
工作区（你改的文件） --git add--> 暂存区（准备提交的） --git commit--> 仓库历史（本地） --git push--> 远程（GitHub）
```

### 13.2 查看状态（只读，随时可用）

| 命令 | 作用 |
|---|---|
| `git status` / `git status --short` | 哪些文件改了、哪些是新文件。短格式：`M` 已修改，`??` 未跟踪，`A` 已暂存的新文件 |
| `git branch --show-current` | 当前分支名 |
| `git log --oneline -5` | 最近 5 个提交，每个一行 |
| `git log --format='%h %an %ad %s' --date=short -6` | 带作者和日期 |
| `git log --oneline -- notes/week01.md` | 某个文件的提交历史 |
| `git diff` | 工作区中还没 add 的改动 |
| `git diff --staged` | 已 add、还没 commit 的改动 |
| `git diff --stat HEAD~3 HEAD` | 最近 3 个提交改了哪些文件 |
| `git show 提交号` | 某个提交的完整改动 |
| `git remote -v` | 远程仓库地址（origin = 你的 fork，upstream = 官方） |

`HEAD` = 当前提交；`HEAD~3` = 往前数 3 个提交。
教训：`HEAD~30` 会追溯到作者的上游提交，不能用来判断"我改了什么"。

### 13.3 提交（写入本地历史）

```bash
git add notes/week01.md notes/bash_cheatsheet.md     # 指定文件加入暂存区
git commit -m "notes: week01 add task4 result"       # 提交，-m 后面是说明
git log --oneline -1                                 # 确认
```

- **优先 add 具体文件**，少用 `git add .`（会把所有改动都加进去，容易误提交）。
- 提交说明用"前缀: 做了什么"，如 `notes: ...`、`eval: ...`、`skip: ...`。
- `local/` 已在 `.gitignore` 中，结果、日志、fuser 不会进 git。

### 13.4 撤销（注意风险）

| 命令 | 作用 | 风险 |
|---|---|---|
| `git restore --staged 文件` | 把文件从暂存区撤回，改动保留 | 安全 |
| `git restore 文件` | **丢弃**工作区里对该文件的改动，恢复到上次提交 | 未提交的改动会永久丢失 |
| `git reset --hard` | 丢弃所有未提交改动 | **不要用** |

### 13.5 分支与远程

| 命令 | 作用 |
|---|---|
| `git switch 分支名` | 切换分支 |
| `git switch -c 新分支` | 新建并切换 |
| `git fetch upstream` | 下载官方仓库的最新提交（不改动你的文件） |
| `git push origin skip-c2c` | 推到你的 fork（**公开/私有与导师确认前不要 push**） |
