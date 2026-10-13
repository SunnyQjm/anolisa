独立复核通过：候选 `2e7fc1720511479c25374246b0ff50a38596aee4` 的干净target真实Core前置构建及全部19条UI测试实际成功，未预建Shell/worker。本报告不覆盖旧c855报告，也不替代新canonical的独立验收。

主证据 `ui/final-clean-core-ui-19.json` 对应实际run `20261013T205259Z-b42fa23a`。独立比对实际run的result.json与该汇总JSON，command/stdout精确一致；ok=true、exit0。实际run repo.commit为最终HEAD；host只读Git核对得到tree `da56e154adf7b3c953948580c84f49de62dbaed2`。原run repo.dirty=true保留不改写，审核时tracked源码无改动，仅`.cosh-lab/`未跟踪。

同一条set-e命令在Rust1.97.1下执行完整顺序：

1. 断言 `/tmp/cosh-ui-core-artifact-clean-20261014-final-startup` 不存在，再mkdir。
2. 只执行 `cargo build --locked -p cosh-core --bin cosh-core`。
3. 断言Core文件存在，Shell及worker文件均不存在。
4. `cargo test --locked -p cosh-shell --test raw_cli ui_approval_slice -- --list` 首次构建Shell/worker，并断言库存恰为19。
5. 相同target执行全部19条测试，最后读取实际三ELF SHA。

独立解析stdout得到19个库存名称和19个实际 `... ok` 名称，两个集合精确一致，包含18条ui_approval_slice与1条reflow。summary为19 passed、0 failed、0 ignored，执行321.67秒。保留的oracle负控按其原测试目的通过，没有拿假Core替代真实Core正控。

实际补充target的SHA：

| 产物 | SHA256 |
| --- | --- |
| cosh-shell | 790f049fc20f863dbf8c37de0d393d456cac020d9d1f5adb22cfa8f6c7488b36 |
| cosh-core | 64f052761468f6077b17aed79a4e6dceecd1418f1615c9360cc3355971a57fe9 |
| cosh-ui-worker | cfe30b7de19165edd0883cd9f2aa1b9b993e8659f0a73d0c2bc7dac8c2127787 |

另只读核对正常矩阵 `ui/final-source-candidate-matrix.json`（run `20261013T205259Z-21c6afea`）：exit0，25 passed/0 failed/0 ignored。正常矩阵Shell和worker与上述SHA相同；正常Core是 `9c73f00310b66dea10302e101009edc6dfffa425fe36f3703c6f8d1b80cc2ee9`。clean Core64f是独立补充产物，不将它替换正常矩阵及随后canonical的Core9c73。

旧c855日志已另存 `ui/c855-clean-core-ui-19.json`，旧复核报告保留。本次只进行host读取和该独立outputs报告写入，没有source/env/cargo操作。
