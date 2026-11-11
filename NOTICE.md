# 数据来源

`data/` 下的词库由 `tools/build_data.py` 从以下开源项目的数据转换而来：

- [Qwerty Learner](https://github.com/RealKai42/qwerty-learner)（GPL-3.0）：初中、高中、四级、六级、考研、托福、雅思、程序员、医学英语词表，以及各级短语。
- 小学三至六年级词表（`data/primary.js`）：由仓库作者对照人教版 PEP（三年级起点）教材附录的单元词汇表整理，按册、按单元排列。
- 初中词库筛除小学基础词时，参考教育部[《义务教育英语课程标准（2022年版）》](https://www.moe.gov.cn/srcsite/A26/s8001/202204/t20220420_619921.html)附录3，以及 [kebiao-english](https://github.com/vickysy/kebiao-english) 的二级词汇整理（MIT，版权及许可见 `tools/level2-reference-LICENSE.txt`）。该整理注明识别得到 501 个词项，课标二级词汇共 505 个，不能视为完整排除所有小学词汇；数词等为单独列出的参考项。

转换时做了筛选、去重、释义截断和音标符号清洗；高中词表打乱了顺序。

单词发音在运行时请求有道词典的公开发音地址，本仓库不包含任何音频文件。
