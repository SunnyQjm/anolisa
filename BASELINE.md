# Issue #2543 FAIL 基线报告（S2）

- Issue: https://github.com/alibaba/anolisa/issues/2543
- Worktree: `anolisa/.worktrees/cosh-2543-rpm-shells-scriptlet`（分支 `fix/cosh-2543-rpm-shells-scriptlet`）
- base_commit: `385a098b136b8fb3e2ddc414ae83e71258ab50bd`（origin/main）
- 被测 spec: `src/cosh-ng/cosh-ng.spec.in` sha256 `c36f1f4df83ae69030a41c0d34d450930f452cb19cbeae9626592e5c2bf77e83`
- 执行环境: Apple `container` CLI 1.0.0 + alinux3 镜像
  （`alibaba-cloud-linux-3-registry.cn-hangzhou.cr.aliyuncs.com/alinux3/alinux3:latest`），
  真实 rpm 内嵌 lua 解释器（`rpm --eval '%{lua:…}'`）。

## 子项 A：PKG-007.shells-no-newline（%post 尾换行不幂等）

- 复现命令：
  `container run --rm -v <worktree>:/work -v <baseline>:/out <alinux3> /bin/bash /out/repro_pkg007.sh`
- 脚本：`repro_pkg007.sh`（权威源在本目录）；从未修改的 spec 提取 %post lua，
  按 rpmbuild 构包语义展开 `%{_bindir}`→`/usr/bin`，对无尾换行 fixture
  （`/bin/sh\n/bin/bash`）执行两轮。
- 结果（`pkg007-fail-baseline.log`）：
  - 第一轮后：`/bin/bash/usr/bin/cosh`（粘连，与 issue 报告逐字一致）
  - 第二轮后：追加重复 `/usr/bin/cosh` 行（非幂等增长）
  - 判定：`VERDICT: FAIL (glued=1 entries=1)`，container_exit=1

## 子项 B：PKG-010（erase 无 %preun fail-closed）

- 检查（`pkg010-fail-baseline.log`）：spec 无任何 `%preun` 段（grep rc=1），
  仅有 `%post`(L101)/`%postun`(L111)。
- 真机全包证据（issue 附带、本地归档）：
  `artifacts/cosh-login-shell-full-execution-20260811/execution/x86_64/system-package/cases/PKG-010.erase-with-user/operation-00/result.json`
  —— 存在 shell=/usr/bin/cosh 用户时 `rpm -e cosh-ng` rc=0、无输出无阻断。

## 基线用途

验收时以同一 `repro_pkg007.sh`（含 missing/empty 变体扩展）与 %preun 行为
检查做 FAIL→PASS 直接对照。
