# 数据来源

`data/` 下的词库由 `tools/build_data.py` 从以下开源项目的数据转换而来：

- [Qwerty Learner](https://github.com/RealKai42/qwerty-learner)（GPL-3.0）：初中、高中、四级、六级、考研、托福、雅思、程序员、医学英语词表，小学四至六年级词表，以及各级短语。
- [EbbWords](https://github.com/XiaoyYuChen/EbbWords)（Apache-2.0）：人教 PEP 2024 新版三年级上、下册单元词表。

转换时做了筛选、去重、释义截断和音标符号清洗；高中词表打乱了顺序。

单词发音在运行时请求有道词典的公开发音地址，本仓库不包含任何音频文件。
