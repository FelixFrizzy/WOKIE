✅: Implemented in WOKIE

❌: Not implemented in WOKIE (see comment for reason)

# Translation Services

While efforts have been made to ensure accuracy, no responsibility is taken for errors or omissions.

| Name | Free? | Comment |
| --- | --- | --- |
| ✅ [Argos](https://translate.argosopentech.com/) | yes | To be used locally with libretranslate (API of Argos) |
| ✅ [Google Translate](https://cloud.google.com/translate/docs/reference/rest) | no  | Uses Cloud Translation API |
| ✅ [Lingvanex](https://lingvanex.com/) | yes |     |
| ✅ [modernMT](https://www.modernmt.com/) | yes |     |
| ✅ [Microsoft Translator](https://www.microsoft.com/en-us/translator/) | no  | Quite low request limits |
| ✅  [PONS](https://de.pons.com/p/ubersetzungsapi) | no  | No latin and serbian in contrast to the [PONS online dictionary](https://de.pons.com/%C3%BCbersetzung) |
| ✅ [Reverso](https://www.reverso.net/) | yes | Sometimes no API response |
| ✅ [Yandex Translate API](https://yandex.com/) | yes |     |
| ❌ [Alibaba](https://www.alibabacloud.com/en/product/machine-translation?_p_lc=1) |     | Very slow |
| ❌ apertium |     | Unexpected exception when using the API |
| ❌ BabelNet |     | Very low request limit |
| ❌ [Bing](https://www.bing.com/translator) |     | Very low request limit |
| ❌ caiyun |     | Very low requests per second |
| ❌ [cloudtranslation](https://online.cloudtranslation.com/) |     | Very low requests per second |
| ❌ [Deepl](https://developers.deepl.com/docs) |     | Very low requests per second |
| ❌ elia |     | Very slow |
| ❌ hujiang |     | Very low requests per second |
| ❌ itranslate |     | Very low requests per second |
| ❌ languageWire |     | Very low requests per second |
| ❌ [Linguee](https://www.linguee.com/) |     | Very low requests per second |
| ❌ [Mymemory](https://mymemory.translated.net/) |     | Very low request limit |
| ❌ [OpenNMT](https://opennmt.net/) |     | Only for full texts |
| ❌ [Papago](https://papago.naver.com/) |     | Very slow, mainly for Korean |
| ❌ [QcriTranslator](https://mt.qcri.org/api/) |     | Obligatory registration failed |
| ❌ qqTranSmart |     | Very slow |
| ❌ [Sogou](https://fanyi.sogou.com/text) |     | Very slow |
| ❌ [Tencent](https://fanyi.qq.com/) |     | Identical to sogou |
| ❌ TranslateCom |     | Very low request limit |

&nbsp;

&nbsp;

# LLM models

Costs as they were at 01.05.2025 using the API provided by the manufacturer. While efforts have been made to ensure accuracy, no responsibility is taken for errors or omissions.

| Model Name | Input Costs (in USD / 1M tokens) | Output costs (in USD / 1M tokens) | Costs for 30,000 Tokens (= small thesaurus) in ¢\* | Comment |
| --- | --- | --- | --- | --- |
| ✅ claude-3-5-haiku | 0.80 | 4   | 2.4 |     |
| ✅ claude-3-5-sonnet | 3   | 15  | 9   |     |
| ✅ claude-3-7-sonnet | 3   | 15  | 9   |     |
| ✅ claude-3-haiku | 0.25 | 1.25 | 0.75 |     |
| ✅ codestral-latest | 0.3 | 0.9 | 0.9 |     |
| ✅ deepseek-chat | 0.27 | 1.10 | 0.81 | 50% discount from 06:30pm to 02:30am |
| ✅ deepseek-reasoner | 0.14 | 2.19 | 0.42 | 75% discount from 06:30pm to 02:30am |
| ✅ gemini-1.5-flash | 0.075 | 0.30 | 0.225 |     |
| ✅ gemini-1.5-flash-8b | 0.0375 | 0.15 | 0.1125 |     |
| ✅ gemini-2.0-flash | 0.10 | 0.40 | 0.3 |     |
| ✅ gemini-2.0-flash-lite | 0.075 | 0.3 | 0.225 |     |
| ✅ gemini-2.5-flash-preview-04-17 | 0.15 | 0.6 | 0.45 |     |
| ✅ gemma3:12b | 0\*\* | 0\*\* | 0\*\* |     |
| ✅ gpt-3.5-turbo | 0.50 | 1.5 | 1.5 |     |
| ✅ gpt-4.1-mini | 0.40 | 3.20 | 1.60 |     |
| ✅ gpt-4.1-nano | 0.10 | 0.40 | 0.3 |     |
| ✅ gpt-4.1 | Unknown | Unknown | Unknown |     |
| ✅ gpt-4o | 2.50 | 10  | 7.5 |     |
| ✅ gpt-4o-mini | 0.15 | 0.60 | 0.45 |     |
| ✅ llama-4-maverick:free | 0\*\* | 0\*\* | 0\*\* |     |
| ✅ ministral-3b-latest | 0.04 | 0.04 | 0.12 |     |
| ✅ mistral-large-latest | 2   | 6   | 6   |     |
| ✅ mistral-medium-latest | 0.4 | 2   | 1.2 |     |
| ✅ mistral-tiny-latest | Unknown   | Unknown   |     |     |
| ✅ mistral-small-latest | 0.15 | 0.15 | 0.45 |     |
| ✅ open-mistral-nemo | 0.15 | 0.15 | 0.45 |     |
| ✅ open-mixtral-8x22b | 2   | 6   | 6   |     |
| ❌ codestral-mamba-latest | Unknown | Unknown | Unknown | Poor performance |
| ❌ llama-4-scout:free | 0\*\* | 0\*\* | 0\*\* | Cannot be reliably constrained to adhere to the expected output format |
| ❌ llama3.2 (ollama) | 0\*\* | 0\*\* | 0\*\* | Returned output is irrelevant and lacks meaningful content |
| ❌ ministral-8b-latest | 0.1 | 0.1 | 0.3 | Poor performance |
| ❌ open-codestral-mamba |     |     |     | Cannot be reliably constrained to adhere to the expected output format, also overly verbose |
| ❌ open-mistral-7b |     |     |     | Cannot be reliably constrained to adhere to the expected output format, also overly verbose |
| ❌ open-mixtral-8x7b | 0.7 | 0.7 | 0.21 | Cannot be reliably constrained to adhere to the expected output format, also overly verbose |

\* The input tokens dominate the costs largely in WOKIE, which is why the total costs for a thesaurus are only calculated with the input costs.

\*\* Free to run locally, licensing might apply.