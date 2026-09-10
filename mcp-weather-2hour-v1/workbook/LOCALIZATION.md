# Student-guide localization notes

Author: **Rajkumar Rajagobalan**

The Japanese (`ja`) and Simplified Chinese (`zh-CN`) editions adapt the English v1.0 student workbook for technical learners. Explanations and task instructions use local writing conventions while preserving the teaching sequence and meaning. These are localized drafts; no independent human linguistic review has been performed.

- All 38 numbered steps, 11 sections, exercises, timing blocks and cautions are retained.
- Executable code, command-line flags, filenames, environment variables, model IDs, protocol methods and trace labels remain exact.
- English notebook headings and displayed messages remain searchable against the common Colab notebook. Surrounding text explains them in the learner's language.
- The shared architecture text diagram stays in English; its components and responsibilities are explained in the localized table immediately below it.
- Synthetic weather, fixed model simulations and actual inference remain distinct. Neither translation changes the pending live-rehearsal status.

| Concept | Japanese | Simplified Chinese |
|---|---|---|
| Agent | エージェント | 智能体 |
| Host | ホスト | 宿主 |
| Client / server | クライアント／サーバー | 客户端／服务器 |
| Tool discovery | ツール検出 | 工具发现 |
| Tool request / execution | ツール実行の要求／実行 | 工具调用请求／实际执行 |
| Schema | スキーマ | 模式定义（schema） |
| Synthetic data | 合成データ | 合成数据 |
| Standard input/output | 標準入出力（stdio） | 标准输入／输出（stdio） |

## Rebuild localized PDFs

Install `reportlab` and `fonttools` in a separate document-build environment. Set `WORKBOOK_FONT_DIR` to a directory containing `DejaVuSansMono.ttf`, then run:

```bash
python scripts/build_localized_workbooks.py
```

The builder downloads Noto Sans JP and Noto Sans SC from the [Google Fonts repository](https://github.com/google/fonts), creates static font instances in the ignored `.course-build/` cache, and embeds font subsets in the PDFs. Noto fonts use the [SIL Open Font License](https://openfontlicense.org/); see the upstream [JP license](https://github.com/google/fonts/blob/main/ofl/notosansjp/OFL.txt) and [SC license](https://github.com/google/fonts/blob/main/ofl/notosanssc/OFL.txt). License notices are included under `licenses/fonts/` at the repository root. Full font binaries are not included in the ZIP. Rebuilding needs network access if they are not cached.

Run `python scripts/check_localized_workbooks.py` to verify the structural correspondence. Render and inspect the PDF pages after any language or layout edit; structural comparison does not replace language or visual review.
