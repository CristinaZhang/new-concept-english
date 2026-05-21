# 资源文件存放规范

## 目录结构

```
resources/
├── audio/                    # 音频文件
│   ├── lesson_001.mp3        # 第1课课文朗读
│   ├── lesson_002.mp3
│   ├── ...
│   └── lesson_144.mp3        # 第144课
│
├── images/                   # 插图
│   ├── lesson_001.jpg        # 第1课配图
│   ├── lesson_002.jpg
│   ├── ...
│   └── lesson_144.jpg
│
└── data/                     # 数据源文件（用于批量导入）
    ├── lessons.xlsx          # 课文：lesson_number, title, text, translation
    ├── vocabulary.xlsx       # 词汇：lesson_number, word, phonetic, meaning, example_sentence
    ├── grammar.xlsx          # 语法：lesson_number, name, explanation, examples
    └── exercises.xlsx        # 练习：lesson_number, type, question, answer, options
```

## 命名规则

- **三位数编号**：`lesson_001.mp3`（不是 `lesson_1.mp3`），方便排序
- **文件后缀**：音频用 `.mp3`，图片用 `.jpg` 或 `.png`
- **小写英文**：文件名全小写，不要中文

## Excel 表格格式

### lessons.xlsx

| lesson_number | title | text | translation |
|---|---|---|---|
| 1 | Excuse me! | Excuse me!\nYes?\nIs this your handbag? | 对不起！\n什么事？\n这是您的手提包吗？ |
| 2 | Is this your…? | ... | ... |

### vocabulary.xlsx

| lesson_number | word | phonetic | meaning | example_sentence |
|---|---|---|---|---|
| 1 | excuse | /ɪkˈskjuːz/ | v. 原谅 | Excuse me! |
| 1 | handbag | /ˈhændbæɡ/ | n. 手提包 | Is this your handbag? |

### grammar.xlsx

| lesson_number | name | explanation | examples |
|---|---|---|---|
| 1 | 一般疑问句 Is this…? | Is this + 名词? 用来确认某物是否属于对方。 | ["Is this your handbag?", "Is this your pen?"] |

> `examples` 列存 JSON 数组字符串

### exercises.xlsx

| lesson_number | type | question | answer | options |
|---|---|---|---|---|
| 1 | mc | — Is this your handbag?\n— ______, it is. | Yes | ["Yes", "No", "OK"] |
| 1 | fill_blank | Is this ______ handbag? | your | [] |

> - `type`：`mc`（选择题）、`fill_blank`（填空）、`error_correction`（改错）
> - `options`：选择题选项，填空题留空数组 `[]`

## 注意事项

1. **课文文本换行**：Excel 里按 `Alt+Enter` 换行
2. **音频格式**：MP3，每个文件 2-5MB 左右
3. **图片格式**：JPG 优先，分辨率 800×600 左右即可
4. **不强制完整**：有多少课就放多少，脚本自动识别

## 上传方式

把百度网盘的文件下载后按上面的结构放好：

```bash
# 示例：你下载后应该长这样
ls resources/audio/
lesson_001.mp3  lesson_002.mp3  lesson_003.mp3  ...

ls resources/images/
lesson_001.jpg  lesson_002.jpg  lesson_003.jpg  ...

ls resources/data/
lessons.xlsx  vocabulary.xlsx  grammar.xlsx  exercises.xlsx
```

准备好后告诉我，我写批量导入脚本。
