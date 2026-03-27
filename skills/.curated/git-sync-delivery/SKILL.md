---
name: git-sync-delivery
description: 基于当前代码改动执行提交、推理目标分支、创建GitLab MR，并自动完成多分支cherry-pick同步。适用于前端多版本分支同步场景。
---

# git-sync-delivery

## 一、用途（Purpose）

该 skill 用于在代码准备就绪后，自动完成以下流程：

- 生成或确认 commit message
- 创建 commit
- 推理并确认目标合并分支（merge target）
- 进行本地预合并检查（pre-merge validation）
- 推送代码并创建主 MR（GitLab）
- 推理并执行多分支 cherry-pick
- 为每个分支创建对应 MR
- 汇总并输出所有 MR 链接，供最终 review

该 skill 是一个执行型 workflow，默认代码已经准备好，不负责代码正确性检查。
skill 在开始执行时，应记录当前原始工作分支名称
后续所有临时 checkout / cherry-pick 完成后，必须恢复到该原始分支

## 二、使用时机（When to use）

在以下场景使用：

- 本地代码修改完成，准备提交 MR
- 需要将修改同步到多个版本分支
- 需要批量创建多个 MR（GitLab）
- 需要自动完成 cherry-pick 分发流程

## 三、前置假设（Assumptions）

默认认为：

- 当前代码已经开发完成并本地验证通过
- 项目可以正常编译
- 当前 git 工作区状态清晰（无未预期改动）
- 用户已准备进入提交和分发流程

该 skill 不负责：

- 功能正确性验证
- lint / test / build
- 代码风格检查

## 四、执行规则
除以下场景外，其余 git / 脚本执行默认直接继续，不逐步询问用户确认：
- 确认 commit message
- 确认 merge target 推理结果
- 确认 cherry-pick 目标分支列表
- 遭遇 merge / cherry-pick 冲突
- 出现无法可靠推理、可能误操作的异常情况

优先使用 `scripts/` 下的小脚本执行高频 git 操作，避免拼接带动态分支名和 commit hash 的超长命令，降低重复授权提示。

当前内置脚本：

- `scripts/sync-target-branch.sh <branch> [remote]`
- `scripts/sync-current-branch.sh <branch> [remote]`
- `scripts/prepare-cherry-pick-branch.sh <target-branch> <temp-branch> [remote]`

## 五、整体流程（Workflow）
用户调用 skill 时，可以附带一段前置 message，用于说明本次提交的语义上下文
- 例如：
- fix: V8-23243
- feat: 新增xxx能力
- refactor: 优化xxx逻辑

用途说明：
- 这段前置 message 作为 commit message 生成的重要上下文
- 它会影响：
- commit message 生成
- MR title 生成
- 对改动类型的理解（bugfix / feat / refactor 等）
- 若用户提供前置 message，自动生成 commit message 时必须优先参考该 message
- 若用户提供的前置 message 已足够完整，可直接将其作为 commit message 候选内容，而不是重新自由发挥

### Step 1：生成并确认 commit message

1. 默认根据当前 diff 自动生成 commit message
2. 展示给用户确认
3. 用户可以：
   - 直接使用
   - 修改内容
   - 完全手动输入

确认后继续。

### Step 2：创建 commit

- 使用确认后的 commit message 创建 commit

### Step 3：推理并确认目标分支（merge target）

1. 根据当前分支名称推理目标分支

推理规则示例：

- `test_bugfix/xxx` -> `test`
- `hotfix/5.0-xxx-user` -> `hotfix/5.0-xxx`

2. 输出推理结果：

```text
推测目标分支为：xxx
推理依据：xxx
```

3. 用户选择：

- 确认使用
- 手动修改
- 取消流程

### Step 4：预合并检查（pre-merge validation）

目的：提前发现冲突。

流程：

- 优先执行 `scripts/sync-target-branch.sh <target-branch>`
- 基于同步后的目标分支创建临时校验分支
- 在临时校验分支上尝试将当前分支 merge 到目标分支
- 若无冲突 -> 继续
- 若发生冲突：
  - 暂停流程
  - 告知冲突分支及原因
  - 等待用户手动解决

要求：

- 不允许直接基于可能落后的本地目标分支做预合并检查
- 若本地目标分支不存在，应从远程目标分支创建
- 校验完成后删除本次创建的临时校验分支，并切回原始工作分支

用户确认“已解决”后继续执行。

### Step 5：同步远程同名工作分支

目的：避免当前本地工作分支与远程同名分支分叉，导致 push 被拒绝。

流程：

- 优先执行 `scripts/sync-current-branch.sh <current-branch>`
- 检查当前工作分支是否存在远程同名分支
- 若不存在远程同名分支 -> 直接进入下一步
- 若存在远程同名分支：
  - 先判断本地与远程是否已经一致或仅本地领先
  - 若远程领先或双方分叉，则先将远程同名分支 merge 到当前本地工作分支
  - merge 成功后再继续
  - 若发生冲突：
    - 暂停流程
    - 告知当前工作分支、远程同名分支、冲突文件
    - 等待用户手动解决

要求：

- 不允许在远程同名分支领先或分叉时直接 push
- 这里的同步对象是“当前工作分支的远程同名分支”，不是目标合并分支
- 若远程同名分支不存在，不应额外创建同步分支，直接按首次推送处理
- 完成该步骤后，当前工作分支应具备可直接 push 的状态

用户确认“已解决”后继续。

### Step 6：推送并创建主 MR

- 推送当前分支到远程
- 在 GitLab 创建 MR：
  - MR title = commit message
  - 不强制生成 description

### Step 7：是否进行 cherry-pick 推理

询问用户：

- 是否需要进行多分支同步（cherry-pick）

用户选择后继续。

### Step 8：推理 cherry-pick 目标分支

推理原则：

1. 当前分支为低版本时，应向更高版本分支同步
2. test 分支视为高版本分支之一
3. 基于版本号向上推理（如 5.0 -> 5.1 -> test）

输出：

建议 cherry-pick 到以下分支：

- xxx
- xxx

用户可：

- 确认全部
- 删除部分
- 手动补充
- 取消

未确认前，不执行任何 cherry-pick。

### Step 9：执行 cherry-pick
对每个目标分支执行：
1. 优先执行 `scripts/prepare-cherry-pick-branch.sh <target-branch> <temp-branch>`
2. 该脚本内部负责同步远程目标分支，并基于最新目标分支创建本次 cherry-pick 使用的临时分支
3. 在临时分支上执行 cherry-pick
4. 若成功 -> 继续
5. 若冲突：
   - 暂停流程
   - 告知当前目标分支、临时分支、冲突文件
   - 等待用户解决

要求：

- 不允许直接从可能落后的本地目标分支 checkout 后执行 cherry-pick
- 临时分支必须明确标识来源目标分支，便于冲突恢复和清理
- 若用户终止流程，必须先中止 cherry-pick，再切回原始工作分支，并删除本次创建的临时分支

用户确认后继续执行剩余流程。

### Step 10：为每个分支创建 MR

- 每个 cherry-pick 分支创建对应 MR
- MR title 默认使用 commit message
- 所有 cherry-pick 执行完成后，删除本次为 cherry-pick 创建的本地临时分支
- 将当前分支切回到 Step 2 创建 commit 时所在的原始工作分支
- 最终保证本地仓库回到用户最初发起流程时的主工作分支
- 删除的仅限本次 workflow 创建的 cherry-pick 临时分支
- 不删除用户原有分支
- 若删除失败，需要告知用户，但不影响已创建的 MR 结果输出

### Step 11：输出最终结果

输出结构如下：

```text
MR创建结果：

主MR：
源分支 -> 目标分支
链接：xxx

Cherry-pick MR：
1.
源分支 -> 目标分支
链接：xxx

2.
源分支 -> 目标分支
链接：xxx

状态：
全部成功 / 部分失败（列出原因）
```

## 六、关键规则（Decision Rules）

1. commit message
- 默认自动生成
- 必须用户确认后执行

2. merge target
- 必须先推理，再确认
- 不允许直接自动执行

3. 当前工作分支与远程同名分支
- push 前必须先检查是否分叉
- 若远程领先或已分叉，必须先 merge 远程同名分支
- 若冲突，暂停并等待用户处理

4. cherry-pick 分支
- 保守推理
- 必须用户确认
- 不确认不执行

## 七、冲突处理（Conflict Handling）

统一规则：

- 一旦 merge 或 cherry-pick 发生冲突：
  - 立即暂停流程
  - 明确当前卡在哪一步、哪个分支
  - 不自动尝试解决冲突
- 在提示中说明该操作是基于远程最新目标分支执行，还是在同步远程同名工作分支时发生，避免用户误判冲突来源

恢复方式：

- 用户手动解决冲突
- 用户确认“已解决”
- 从中断点继续执行（不重复前面步骤）

## 八、执行风格（Execution Style）

该 skill 应具备以下特性：

- 强交互（每个关键决策点都需确认）
- 保守执行（不乱推理、不自动冒进）
- 清晰状态（每一步都说明当前在做什么）
- 可恢复（冲突后能继续）

## 九、禁止行为（Do Not）

- 未经确认自动执行 merge 或 cherry-pick
- 自动解决冲突
- 自动创建错误分支 MR
- 推理不明确时强行继续流程
- 输出模糊或不完整结果

## 十、成功标准（Success Criteria）

该 skill 成功的标志是：

- 用户只需少量确认即可完成整个提交流程
- 多分支 MR 自动创建成功
- 冲突可控且不会误操作
- 最终输出清晰完整的 MR 列表
