#!/usr/bin/env python3
"""Seed data for New Concept English Book 1 — Lessons 1-20."""
from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlmodel import Session, select

from app.config import settings
from app.db.database import engine, init_db
from app.db.models import Lesson, Vocabulary, GrammarPoint, Exercise


# ── Audio file mapping (paired files from wychl/nce repo) ────────────
_AUDIO_MAP = {
    (1, 2): "001&002.Excuse Me",
    (3, 4): "003&004.Sorry, Sir",
    (5, 6): "005&006.Nice to Meet You",
    (7, 8): "007&008.Are You a Teacher",
    (9, 10): "009&010.How Are You Today",
    (11, 12): "011&012.Is This Your Shirt",
    (13, 14): "013&014.A New Dress",
    (15, 16): "015&016.Your Passports, Please",
    (17, 18): "017&018.How do you do",
    (19, 20): "019&020.Tired and Thirsty",
}


def _audio_filename(lesson_num: int) -> str:
    """Get the audio filename for a given lesson number (paired files)."""
    for (start, end), name in _AUDIO_MAP.items():
        if start <= lesson_num <= end:
            return name
    return f"lesson_{lesson_num:03d}"


# ── Lessons ──────────────────────────────────────────────────────────
LESSONS = [
    # (lesson_number, title, text, translation)
    (1, "Excuse me!",
     "Excuse me!\nYes?\nIs this your handbag?\nPardon?\nIs this your handbag?\nYes, it is.\nThank you very much.",
     "对不起！\n什么事？\n这是您的手提包吗？\n对不起，请再说一遍。\n这是您的手提包吗？\n是的，它是。\n非常感谢。"),

    (2, "Is this your…?",
     "Is this your…?\nYes, it is.\nNo, it isn't.\nIs this your book?\nYes, it is.\nIs this your watch?\nNo, it isn't.\nIs this your pen?\nYes, it is.",
     "这是你的……吗？\n是的，它是。\n不，它不是。\n这是你的书吗？\n是的，它是。\n这是你的手表吗？\n不，它不是。\n这是你的钢笔吗？\n是的，它是。"),

    (3, "Sorry, sir.",
     "My coat and my umbrella please.\nHere is my ticket.\nThank you, sir.\nNumber five.\nHere's your umbrella and your coat.\nThis is not my umbrella.\nSorry, sir.\nIs this your umbrella?\nNo, it isn't.\nIs this it?\nYes, it is.\nThank you very much.",
     "请拿我的大衣和雨伞。\n这是我的票。\n谢谢您，先生。\n第五号。\n这是您的雨伞和大衣。\n这不是我的雨伞。\n对不起，先生。\n这把是您的雨伞吗？\n不，它不是。\n这把是吗？\n是的，它是。\n非常感谢。"),

    (4, "Is this your…?",
     "Is this your pen?\nYes, it is.\nIs this your pencil?\nYes, it is.\nIs this your book?\nYes, it is.\nIs this your watch?\nNo, it isn't.\nIs this your coat?\nNo, it isn't.\nIs this your handbag?\nYes, it is.",
     "这是你的……吗？\n是的，它是。\n这是你的铅笔吗？\n是的，它是。\n这是你的书吗？\n是的，它是。\n这是你的手表吗？\n不，它不是。\n这是你的大衣吗？\n不，它不是。\n这是你的手提包吗？\n是的，它是。"),

    (5, "Nice to meet you.",
     "Good morning.\nGood morning, Mr. Blake.\nThis is Miss Sophie Dupont.\nSophie is a new student.\nShe is French.\nSophie, this is Hans.\nHe is German.\nNice to meet you.\nAnd this is Naoko.\nShe's Japanese.\nNice to meet you.\nAnd this is Changwoo.\nHe's Korean.\nNice to meet you.\nAnd this is Luming.\nHe's Chinese.\nNice to meet you.\nAnd this is Xiaohui.\nShe's Chinese, too.",
     "早上好。\n早上好，布莱克先生。\n这位是苏菲·杜邦小姐。\n苏菲是一名新学生。\n她是法国人。\n苏菲，这是汉斯。\n他是德国人。\n很高兴认识你。\n这是直子。\n她是日本人。\n很高兴认识你。\n这是昌宇。\n他是韩国人。\n很高兴认识你。\n这是鲁明。\n他是中国人。\n很高兴认识你。\n这是晓慧。\n她也是中国人。"),

    (6, "What nationality are you?",
     "What nationality are you?\nI'm French.\nWhat about Hans?\nHe's German.\nAre you French, too?\nNo, I'm not.\nI'm Korean.\nWhat nationality is Changwoo?\nHe's Korean.\nIs Naoko Japanese?\nYes, she is.\nIs she a teacher?\nNo, she isn't.\nShe's a student.",
     "你是哪国人？\n我是法国人。\n汉斯呢？\n他是德国人。\n你也是法国人吗？\n不，我不是。\n我是韩国人。\n昌宇是哪国人？\n他是韩国人。\n直子是日本人吗？\n是的，她是。\n她是老师吗？\n不，她不是。\n她是学生。"),

    (7, "Are you a teacher?",
     "What's your job?\nI'm a teacher.\nWhat about you?\nI'm a student.\nAre you a teacher?\nNo, I'm not.\nI'm a keyboard operator.\nWhat's his job?\nHe's an engineer.",
     "你的工作是什么？\n我是一名老师。\n你呢？\n我是一名学生。\n你是老师吗？\n不，我不是。\n我是电脑操作员。\n他的工作是什么？\n他是一名工程师。"),

    (8, "What's your job?",
     "What's your job?\nI'm a teacher.\nAre you a student?\nYes, I am.\nWhat's his job?\nHe's a policeman.\nWhat's her job?\nShe's a nurse.\nWhat nationality is he?\nHe's French.",
     "你的工作是什么？\n我是一名老师。\n你是学生吗？\n是的，我是。\n他的工作是什么？\n他是一名警察。\n她的工作是什么？\n她是一名护士。\n他是哪国人？\n他是法国人。"),

    (9, "How are you today?",
     "Hello, Helen.\nHi, Steven.\nHow are you today?\nI'm very well, thank you.\nAnd how are you?\nI'm fine, thanks.\nHow's Tony?\nHe's fine, thanks.\nHow's Emma?\nShe's very well, too, Helen.",
     "你好，海伦。\n嗨，史蒂文。\n你今天好吗？\n我很好，谢谢。\n你呢？\n我也很好，谢谢。\n托尼好吗？\n他很好，谢谢。\n埃玛好吗？\n她也很好，海伦。"),

    (10, "Look at…",
     "Look at that fat boy!\nWhich boy?\nThat fat boy, Paul.\nHe's very big.\nLook at that girl!\nWhich girl?\nThat thin girl, Lucy.\nShe's very pretty.\nLook at that man!\nWhich man?\nThat tall man, Mr. Smith.\nHe's very funny.",
     "看那个胖男孩！\n哪个男孩？\n那个胖男孩，保罗。\n他很大。\n看那个女孩！\n哪个女孩？\n那个瘦女孩，露西。\n她很漂亮。\n看那个男人！\n哪个男人？\n那个高个子男人，史密斯先生。\n他很有趣。"),

    (11, "Is this your shirt?",
     "What colour is your new dress?\nIt's green.\nCome upstairs and see it.\nThanks.\nLook!\nIt's the same colour!\nYes, and it's the same size too.",
     "你的新裙子是什么颜色的？\n它是绿色的。\n上楼看看吧。\n谢谢。\n看！\n颜色一样！\n是的，而且尺码也一样。"),

    (12, "What colour is it?",
     "What colour is my new hat?\nIs it blue?\nNo, it isn't.\nIt's green.\nIs this your hat?\nYes, it is.\nIt's very nice.",
     "我的新帽子是什么颜色的？\n它是蓝色的吗？\n不，它不是。\n它是绿色的。\n这是你的帽子吗？\n是的，它是。\n它很漂亮。"),

    (13, "A new dress",
     "What colour is Anna's new dress?\nHer new dress is green.\nIs this her dress?\nNo, it isn't.\nHer dress is blue.\nOh, that one is very pretty.",
     "安娜的新裙子是什么颜色的？\n她的新裙子是绿色的。\n这是她的裙子吗？\n不，它不是。\n她的裙子是蓝色的。\n哦，那条非常漂亮。"),

    (14, "Whose is this?",
     "Whose shirt is this?\nIs it Tim's?\nYes, it's his.\nTim!\nYes?\nYour shirt's dirty.\nLook!\nIt's not my shirt!\nMy shirt's blue.\nThat's my old shirt.\nMy new shirt's here.",
     "这是谁的衬衫？\n是蒂姆的吗？\n是的，是他的。\n蒂姆！\n什么事？\n你的衬衫脏了。\n看！\n那不是我的衬衫！\n我的衬衫是蓝色的。\n那是我的旧衬衫。\n我的新衬衫在这里。"),

    (15, "Your passports, please.",
     "Are you Swedish?\nNo, we are not.\nWe are Danish.\nAre you Danish?\nYes, we are.\nAre your friends Danish too?\nNo, they aren't.\nThey are Norwegian.\nYour passports, please.\nHere they are.\nAre these your cases?\nNo, they aren't.\nOur cases are brown.",
     "你们是瑞典人吗？\n不，我们不是。\n我们是丹麦人。\n你们是丹麦人吗？\n是的，我们是。\n你们的朋友也是丹麦人吗？\n不，他们不是。\n他们是挪威人。\n请出示你们的护照。\n在这里。\n这些是你们的箱子吗？\n不，它们不是。\n我们的箱子是棕色的。"),

    (16, "Are they…?",
     "Are you tourists?\nYes, we are.\nAre your friends tourists too?\nYes, they are.\nAre they Danish?\nNo, they aren't.\nThey are English.\nAre they American?\nNo, they aren't.\nThey are English.",
     "你们是游客吗？\n是的，我们是。\n你们的朋友也是游客吗？\n是的，他们是。\n他们是丹麦人吗？\n不，他们不是。\n他们是英国人。\n他们是美国人吗？\n不，他们不是。\n他们是英国人。"),

    (17, "How do you do?",
     "Come and meet our new staff.\nHow do you do, Mr. Jackson?\nNice to meet you.\nThis is Hans.\nHe's our new assistant.\nHe's German.\nHe comes from Berlin.\nHow do you do?",
     "来见见我们的新员工。\n你好，杰克逊先生？\n很高兴认识你。\n这是汉斯。\n他是我们的新助理。\n他是德国人。\n他来自柏林。\n你好吗？"),

    (18, "What are their jobs?",
     "What are their jobs?\nThey are keyboard operators.\nThey are very busy.\nAre they hard-working?\nYes, they are.\nWhat about the typists?\nThey are hard-working too.",
     "他们的工作是什么？\n他们是电脑操作员。\n他们很忙。\n他们工作努力吗？\n是的，他们很努力。\n那些打字员呢？\n他们也很努力。"),

    (19, "Tired and thirsty.",
     "Mum!\nYes?\nWe're tired and thirsty.\nSit down here.\nHere you are.\nThank you.\nAre you tired?\nNo, we aren't.\nBut we are thirsty.",
     "妈妈！\n什么事？\n我们又累又渴。\n在这里坐下。\n给你们。\n谢谢。\n你们累吗？\n不，我们不累。\n但是我们很渴。"),

    (20, "Big and small",
     "Look at those people!\nThey are very busy.\nWhat are they doing?\nThey are looking at the shops.\nWhich shops?\nThe big shops.\nThey are very nice.\nAre they expensive?\nYes, they are.",
     "看那些人！\n他们很忙。\n他们在做什么？\n他们在看商店。\n哪些商店？\n那些大商店。\n它们很漂亮。\n它们贵吗？\n是的，很贵。"),
]

# ── Vocabulary ───────────────────────────────────────────────────────
# (lesson_number, word, phonetic, meaning, example_sentence)
VOCABULARY = [
    # Lesson 1
    (1, "excuse", "/ɪkˈskjuːz/", "v. 原谅", "Excuse me, is this your bag?"),
    (1, "handbag", "/ˈhændbæɡ/", "n. 手提包", "This is my handbag."),
    (1, "pardon", "/ˈpɑːdn/", "int. 请再说一遍", "Pardon? I can't hear you."),
    (1, "thank", "/θæŋk/", "v. 感谢", "Thank you very much."),

    # Lesson 2
    (2, "book", "/bʊk/", "n. 书", "Is this your book?"),
    (2, "pen", "/pen/", "n. 钢笔", "I have a new pen."),
    (2, "watch", "/wɒtʃ/", "n. 手表", "My watch is on the table."),
    (2, "pencil", "/ˈpensl/", "n. 铅笔", "She has a red pencil."),
    (2, "ruler", "/ˈruːlər/", "n. 尺子", "The ruler is long."),

    # Lesson 3
    (3, "coat", "/kəʊt/", "n. 大衣", "Put on your coat."),
    (3, "umbrella", "/ʌmˈbrelə/", "n. 雨伞", "Take your umbrella."),
    (3, "ticket", "/ˈtɪkɪt/", "n. 票", "Here is my ticket."),
    (3, "number", "/ˈnʌmbər/", "n. 号码", "My number is five."),
    (3, "sorry", "/ˈsɒri/", "adj. 对不起", "Sorry, it's not mine."),

    # Lesson 5
    (5, "new", "/njuː/", "adj. 新的", "She is a new student."),
    (5, "student", "/ˈstjuːdənt/", "n. 学生", "I am a student."),
    (5, "French", "/frentʃ/", "adj. 法国的", "She is French."),
    (5, "German", "/ˈdʒɜːmən/", "adj. 德国的", "He is German."),
    (5, "meet", "/miːt/", "v. 遇见", "Nice to meet you."),

    # Lesson 6
    (6, "nationality", "/ˌnæʃəˈnæləti/", "n. 国籍", "What nationality are you?"),
    (6, "Japanese", "/ˌdʒæpəˈniːz/", "adj. 日本的", "She is Japanese."),
    (6, "Korean", "/kəˈriːən/", "adj. 韩国的", "He is Korean."),
    (6, "Chinese", "/ˌtʃaɪˈniːz/", "adj. 中国的", "They are Chinese."),
    (6, "teacher", "/ˈtiːtʃər/", "n. 老师", "Is she a teacher?"),

    # Lesson 7
    (7, "job", "/dʒɒb/", "n. 工作", "What's your job?"),
    (7, "engineer", "/ˌendʒɪˈnɪər/", "n. 工程师", "He is an engineer."),
    (7, "operator", "/ˈɒpəreɪtər/", "n. 操作员", "She is an operator."),
    (7, "keyboard", "/ˈkiːbɔːd/", "n. 键盘", "This is a keyboard."),

    # Lesson 8
    (8, "policeman", "/pəˈliːsmən/", "n. 警察", "He is a policeman."),
    (8, "nurse", "/nɜːs/", "n. 护士", "She is a nurse."),
    (8, "driver", "/ˈdraɪvər/", "n. 司机", "My father is a driver."),
    (8, "mechanic", "/mɪˈkænɪk/", "n. 机械师", "He is a mechanic."),

    # Lesson 9
    (9, "hello", "/həˈləʊ/", "int. 你好", "Hello, how are you?"),
    (9, "well", "/wel/", "adj. 健康的", "I am very well."),
    (9, "fine", "/faɪn/", "adj. 好的", "I'm fine, thanks."),
    (9, "today", "/təˈdeɪ/", "adv. 今天", "How are you today?"),

    # Lesson 10
    (10, "fat", "/fæt/", "adj. 胖的", "The fat boy is Paul."),
    (10, "thin", "/θɪn/", "adj. 瘦的", "The thin girl is Lucy."),
    (10, "tall", "/tɔːl/", "adj. 高的", "He is very tall."),
    (10, "pretty", "/ˈprɪti/", "adj. 漂亮的", "She is very pretty."),
    (10, "funny", "/ˈfʌni/", "adj. 有趣的", "He is very funny."),

    # Lesson 11
    (11, "colour", "/ˈkʌlər/", "n. 颜色", "What colour is it?"),
    (11, "green", "/ɡriːn/", "adj. 绿色的", "The dress is green."),
    (11, "dress", "/dres/", "n. 裙子", "Her new dress is pretty."),
    (11, "same", "/seɪm/", "adj. 相同的", "It's the same colour."),
    (11, "size", "/saɪz/", "n. 尺码", "It's the same size."),

    # Lesson 12
    (12, "hat", "/hæt/", "n. 帽子", "What colour is your hat?"),
    (12, "blue", "/bluː/", "adj. 蓝色的", "My hat is blue."),
    (12, "nice", "/naɪs/", "adj. 好的", "It's very nice."),
    (12, "whose", "/huːz/", "pron. 谁的", "Whose hat is this?"),

    # Lesson 13
    (13, "pretty", "/ˈprɪti/", "adj. 漂亮的", "That dress is pretty."),
    (13, "blue", "/bluː/", "adj. 蓝色的", "Her dress is blue."),

    # Lesson 14
    (14, "shirt", "/ʃɜːt/", "n. 衬衫", "This is Tim's shirt."),
    (14, "dirty", "/ˈdɜːti/", "adj. 脏的", "Your shirt is dirty."),
    (14, "old", "/əʊld/", "adj. 旧的", "That's my old shirt."),
    (14, "new", "/njuː/", "adj. 新的", "My new shirt is here."),

    # Lesson 15
    (15, "Swedish", "/ˈswiːdɪʃ/", "adj. 瑞典的", "Are you Swedish?"),
    (15, "Danish", "/ˈdeɪnɪʃ/", "adj. 丹麦的", "We are Danish."),
    (15, "Norwegian", "/nɔːˈwiːdʒən/", "adj. 挪威的", "They are Norwegian."),
    (15, "passport", "/ˈpɑːspɔːt/", "n. 护照", "Your passports, please."),
    (15, "case", "/keɪs/", "n. 箱子", "Our cases are brown."),
    (15, "brown", "/braʊn/", "adj. 棕色的", "The box is brown."),

    # Lesson 16
    (16, "tourist", "/ˈtʊərɪst/", "n. 游客", "Are you tourists?"),
    (16, "English", "/ˈɪŋɡlɪʃ/", "adj. 英国的", "They are English."),
    (16, "American", "/əˈmerɪkən/", "adj. 美国的", "Are they American?"),

    # Lesson 17
    (17, "staff", "/stɑːf/", "n. 员工", "Meet our new staff."),
    (17, "assistant", "/əˈsɪstənt/", "n. 助理", "He's our new assistant."),
    (17, "come", "/kʌm/", "v. 来", "Come and meet us."),

    # Lesson 18
    (18, "busy", "/ˈbɪzi/", "adj. 忙碌的", "They are very busy."),
    (18, "hard-working", "/ˌhɑːdˈwɜːkɪŋ/", "adj. 努力的", "They are hard-working."),
    (18, "typist", "/ˈtaɪpɪst/", "n. 打字员", "The typists are busy."),

    # Lesson 19
    (19, "tired", "/taɪəd/", "adj. 疲倦的", "We are tired."),
    (19, "thirsty", "/ˈθɜːsti/", "adj. 渴的", "We are thirsty."),
    (19, "sit", "/sɪt/", "v. 坐", "Sit down here."),

    # Lesson 20
    (20, "people", "/ˈpiːpl/", "n. 人们", "Look at those people!"),
    (20, "shop", "/ʃɒp/", "n. 商店", "They are looking at the shops."),
    (20, "expensive", "/ɪkˈspensɪv/", "adj. 昂贵的", "They are expensive."),
    (20, "big", "/bɪɡ/", "adj. 大的", "The big shops are nice."),
    (20, "small", "/smɔːl/", "adj. 小的", "The small shop is cute."),
]

# ── Grammar Points ───────────────────────────────────────────────────
GRAMMAR = [
    (1, "一般疑问句 Is this…?",
     "Is this + 名词? 用来确认某物是否属于对方。肯定回答: Yes, it is. 否定回答: No, it isn't.",
     ["Is this your handbag?", "Is this your pen?", "Is this your book?"]),

    (2, "一般疑问句 Is this your…?（复习）",
     "Is this your + 物品? 确认物品的归属。Yes, it is. / No, it isn't.",
     ["Is this your watch?", "Is this your coat?", "Is this your pencil?"]),

    (3, "祈使句与礼貌用语",
     "用 please 表示礼貌，如 My coat and my umbrella please. 以及 Thank you / Sorry sir.",
     ["My coat and my umbrella please.", "Thank you, sir.", "Sorry, sir."]),

    (5, "介绍他人 — This is…",
     "This is + 人名. 用于向别人介绍某人。She is / He is + 国籍/职业.",
     ["This is Miss Sophie Dupont.", "Sophie, this is Hans.", "She is French."]),

    (6, "询问国籍 — What nationality…?",
     "What nationality are you? — I'm + 国籍. 询问和回答国籍的表达方式.",
     ["What nationality are you?", "I'm French.", "He's German."]),

    (7, "询问职业 — What's your job?",
     "What's your job? — I'm a/an + 职业. 注意元音前用 an.",
     ["What's your job?", "I'm a teacher.", "He's an engineer."]),

    (9, "问候语 — How are you?",
     "How are you today? — I'm very well / fine, thank you. 日常问候用语.",
     ["How are you today?", "I'm very well, thank you.", "How's Tony?"]),

    (10, "Look at… + 形容词",
     "Look at + 名词! 用来引起注意。后面可以跟形容词描述特征。",
     ["Look at that fat boy!", "Look at that girl!", "She's very pretty."]),

    (11, "What colour is…?",
     "What colour is/are…? 用来询问颜色。回答用 It's/They're + 颜色.",
     ["What colour is your dress?", "It's green.", "What colour is my hat?"]),

    (12, "物主代词 — whose / my / your / his / her",
     "Whose is this? — It's + 名词's / his / hers. 询问物品归属.",
     ["Whose shirt is this?", "It's Tim's.", "Her dress is blue."]),

    (14, "名词所有格",
     "名词 + 's 表示所属关系，如 Tim's shirt, Anna's dress.",
     ["Tim's shirt is blue.", "Anna's dress is green.", "Whose passport is this?"]),

    (15, "一般疑问句复数 — Are you/they…?",
     "Are you/they + 国籍/身份? 复数形式的一般疑问句。Yes, we/they are. / No, we/they aren't.",
     ["Are you Swedish?", "No, we are not.", "Are they Danish?"]),

    (17, "How do you do?",
     "How do you do? 是正式场合初次见面的问候语，回答同样是 How do you do?",
     ["How do you do, Mr. Jackson?", "How do you do?"]),

    (18, "What are their jobs?",
     "What are their jobs? — They are + 复数职业名词。复数形式的职业询问.",
     ["What are their jobs?", "They are keyboard operators.", "What about the typists?"]),

    (19, "be + 形容词 — 描述状态",
     "We're tired and thirsty. 用 be + 形容词描述人的身体状态或感觉.",
     ["We're tired and thirsty.", "But we are thirsty.", "Are you tired?"]),

    (20, "Look at those… / 指示代词复数",
     "those 指代远处的复数事物，对应单数 that。those + 复数名词.",
     ["Look at those people!", "Which shops?", "The big shops."]),
]

# ── Exercises ────────────────────────────────────────────────────────
# (lesson_number, question, type, answer, options)
EXERCISES = [
    # Lesson 1
    (1, "— Is this your handbag?\n— ______, it is.", "mc", "Yes", ["Yes", "No", "OK"]),
    (1, "— Is this your pen?\n— No, it ______.", "mc", "isn't", ["is", "isn't", "are"]),
    (1, "Is this ______ handbag?", "fill_blank", "your", []),

    # Lesson 2
    (2, "— Is this your book?\n— Yes, ______.", "mc", "it is", ["it is", "it isn't", "I am"]),
    (2, "— ______ this your watch?\n— No, it isn't.", "fill_blank", "Is", []),
    (2, "— Is this your pencil?\n— No, it ______.", "mc", "isn't", ["isn't", "is", "am"]),

    # Lesson 3
    (3, "My coat and my umbrella ______.", "mc", "please", ["please", "thank", "sorry"]),
    (3, "______ is my ticket.", "mc", "Here", ["Here", "There", "Where"]),
    (3, "This is ______ my umbrella.", "mc", "not", ["not", "no", "isn't"]),

    # Lesson 5
    (5, "She is a ______ student.", "mc", "new", ["new", "old", "big"]),
    (5, "Sophie is ______.", "mc", "French", ["French", "France", "France's"]),
    (5, "Nice ______ meet you.", "mc", "to", ["to", "for", "of"]),

    # Lesson 6
    (6, "— What ______ are you?\n— I'm French.", "mc", "nationality", ["nationality", "job", "name"]),
    (6, "He is ______.", "mc", "German", ["German", "Germany", "Germany's"]),
    (6, "— Is she a teacher?\n— No, she ______.", "mc", "isn't", ["isn't", "is", "aren't"]),

    # Lesson 7
    (7, "— What's your ______?\n— I'm a teacher.", "mc", "job", ["job", "name", "age"]),
    (7, "He's ______ engineer.", "mc", "an", ["an", "a", "the"]),
    (7, "I'm a keyboard ______.", "mc", "operator", ["operator", "operate", "operation"]),

    # Lesson 9
    (9, "— How are you ______?\n— I'm fine.", "mc", "today", ["today", "yesterday", "tomorrow"]),
    (9, "I'm very ______, thank you.", "mc", "well", ["well", "good", "nice"]),
    (9, "— How's Tony?\n— ______ fine.", "mc", "He's", ["He's", "She's", "They're"]),

    # Lesson 10
    (10, "Look ______ that fat boy!", "mc", "at", ["at", "on", "in"]),
    (10, "That ______ girl, Lucy.", "mc", "thin", ["thin", "thick", "wide"]),
    (10, "He's very ______.", "mc", "funny", ["funny", "fun", "funnier"]),

    # Lesson 11
    (11, "— What ______ is your dress?\n— It's green.", "mc", "colour", ["colour", "size", "shape"]),
    (11, "It's the ______ colour.", "mc", "same", ["same", "some", "similar"]),
    (11, "What colour is ______ new dress?", "mc", "your", ["your", "you", "you're"]),

    # Lesson 12
    (12, "______ hat is this?", "mc", "Whose", ["Whose", "Who", "Who's"]),
    (12, "It's very ______.", "mc", "nice", ["nice", "nasty", "not"]),
    (12, "Is it blue? — No, it ______.", "mc", "isn't", ["isn't", "is", "not"]),

    # Lesson 14
    (14, "______ shirt is this? — It's Tim's.", "mc", "Whose", ["Whose", "Who", "Which"]),
    (14, "Your shirt's ______.", "mc", "dirty", ["dirty", "clean", "new"]),
    (14, "My ______ shirt's here.", "mc", "new", ["new", "old", "big"]),

    # Lesson 15
    (15, "— Are you Swedish?\n— No, we ______.", "mc", "aren't", ["aren't", "isn't", "am not"]),
    (15, "We are ______.", "mc", "Danish", ["Danish", "Denmark", "Denmarks"]),
    (15, "______ passports, please.", "mc", "Your", ["Your", "You", "You're"]),

    # Lesson 17
    (17, "______ and meet our new staff.", "mc", "Come", ["Come", "Go", "Run"]),
    (17, "How do you ______, Mr. Jackson?", "mc", "do", ["do", "are", "is"]),
    (17, "He's our new ______.", "mc", "assistant", ["assistant", "assist", "assisting"]),

    # Lesson 19
    (19, "We're ______ and thirsty.", "mc", "tired", ["tired", "tiring", "tire"]),
    (19, "______ down here.", "mc", "Sit", ["Sit", "Stand", "Sleep"]),
    (19, "But we ______ thirsty.", "mc", "are", ["are", "is", "am"]),

    # Lesson 20
    (20, "Look at ______ people!", "mc", "those", ["those", "this", "that"]),
    (20, "They are looking at the ______.", "mc", "shops", ["shops", "shop", "shopping"]),
    (20, "Are they expensive? — Yes, they ______.", "mc", "are", ["are", "is", "do"]),
]


def seed():
    db_url = settings.database_url
    if db_url.startswith("sqlite:///") and not db_url.startswith("sqlite:///:memory:"):
        db_path = db_url.replace("sqlite:///", "")
        os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)

    init_db()

    with Session(engine) as session:
        # Remove all existing data for a clean re-seed
        from sqlmodel import delete
        session.exec(delete(Exercise))
        session.exec(delete(GrammarPoint))
        session.exec(delete(Vocabulary))
        session.exec(delete(Lesson))
        session.commit()
        print("🧹 Cleared existing data.")

        # ── Lessons ──────────────────────────────────────────────
        for num, title, text, translation in LESSONS:
            lesson = Lesson(
                lesson_number=num,
                title=title,
                level="第一册",
                text=text,
                translation=translation,
                image_url=f"/resources/images/lesson_{num:03d}.svg",
                audio_url=f"/resources/audio/{_audio_filename(num)}.mp3",
            )
            session.add(lesson)
        session.commit()

        # Build lesson_id map: lesson_number -> id
        all_lessons = session.exec(select(Lesson)).all()
        lesson_id_map = {l.lesson_number: l.id for l in all_lessons}

        # ── Vocabulary ───────────────────────────────────────────
        vocab_count = 0
        for lesson_num, word, phonetic, meaning, example in VOCABULARY:
            v = Vocabulary(
                lesson_id=lesson_id_map[lesson_num],
                word=word,
                phonetic=phonetic,
                meaning=meaning,
                example_sentence=example,
            )
            session.add(v)
            vocab_count += 1
        session.commit()

        # ── Grammar Points ───────────────────────────────────────
        grammar_count = 0
        gp_map = {}  # (lesson_number, name) -> id
        for lesson_num, name, explanation, examples in GRAMMAR:
            gp = GrammarPoint(
                lesson_id=lesson_id_map[lesson_num],
                name=name,
                explanation=explanation,
            )
            gp.examples = examples
            session.add(gp)
            grammar_count += 1
        session.commit()

        # Build grammar point map
        all_gp = session.exec(select(GrammarPoint)).all()
        for gp in all_gp:
            lesson = session.get(Lesson, gp.lesson_id)
            gp_map[(lesson.lesson_number, gp.name)] = gp.id

        # ── Exercises ────────────────────────────────────────────
        exercise_count = 0
        for lesson_num, question, ex_type, answer, options in EXERCISES:
            # Find the grammar point for this lesson
            gp_id = None
            for (ln, gn), gid in gp_map.items():
                if ln == lesson_num:
                    gp_id = gid
                    break

            ex = Exercise(
                lesson_id=lesson_id_map[lesson_num],
                grammar_point_id=gp_id,
                type=ex_type,
                question=question,
                answer=answer,
            )
            ex.options = options
            session.add(ex)
            exercise_count += 1
        session.commit()

        print(f"✅ Seeded {len(LESSONS)} lessons, {vocab_count} vocabulary words, "
              f"{grammar_count} grammar points, {exercise_count} exercises.")


if __name__ == "__main__":
    seed()
