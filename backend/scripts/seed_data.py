#!/usr/bin/env python3
"""Seed data for New Concept English Book 1 — Lessons 1-10 sample."""
from __future__ import annotations

import sys
from pathlib import Path

# Add backend to path so we can import app modules
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlmodel import Session, select

from app.db.database import engine, init_db
from app.db.models import Lesson, Vocabulary, GrammarPoint, Exercise


def seed():
    init_db()

    with Session(engine) as session:
        # Check if already seeded
        existing = session.exec(select(Lesson)).first()
        if existing:
            print("⚠️  Database already has data. Skipping seed.")
            return

        # ── Lessons 1-10 (sample) ─────────────────────────────────
        lessons_data = [
            (1, "Excuse me!", "Excuse me!\nYes?\nIs this your handbag?\nPardon?\nIs this your handbag?\nYes, it is.\nThank you very much.", "对不起！\n什么事？\n这是您的手提包吗？\n对不起，请再说一遍。\n这是您的手提包吗？\n是的，它是。\n非常感谢。"),
            (2, "Is this your…?", "Is this your…?\nYes, it is.\nNo, it isn't.\nIs this your book?\nYes, it is.\nIs this your watch?\nNo, it isn't.\nIs this your pen?\nYes, it is.", "这是你的……吗？\n是的，它是。\n不，它不是。\n这是你的书吗？\n是的，它是。\n这是你的手表吗？\n不，它不是。\n这是你的钢笔吗？\n是的，它是。"),
            (3, "Sorry, sir.", "My coat and my umbrella please.\nHere is my ticket.\nThank you, sir.\nNumber five.\nHere's your umbrella and your coat.\nThis is not my umbrella.\nSorry, sir.\nIs this your umbrella?\nNo, it isn't.\nIs this it?\nYes, it is.\nThank you very much.", "请拿我的大衣和雨伞。\n这是我的票。\n谢谢您，先生。\n第五号。\n这是您的雨伞和大衣。\n这不是我的雨伞。\n对不起，先生。\n这把是您的雨伞吗？\n不，它不是。\n这把是吗？\n是的，它是。\n非常感谢。"),
            (4, "Is this your…?", "Is this your pen?\nYes, it is.\nIs this your pencil?\nYes, it is.\nIs this your book?\nYes, it is.\nIs this your watch?\nNo, it isn't.\nIs this your coat?\nNo, it isn't.\nIs this your handbag?\nYes, it is.", "这是你的……吗？\n是的，它是。\n这是你的铅笔吗？\n是的，它是。\n这是你的书吗？\n是的，它是。\n这是你的手表吗？\n不，它不是。\n这是你的大衣吗？\n不，它不是。\n这是你的手提包吗？\n是的，它是。"),
            (5, "Nice to meet you.", "Good morning.\nGood morning, Mr. Blake.\nThis is Miss Sophie Dupont.\nSophie is a new student.\nShe is a French.\nSophie, this is Hans.\nHe is German.\nNice to meet you.\nAnd this is Naoko.\nShe's Japanese.\nNice to meet you.\nAnd this is Changwoo.\nHe's Korean.\nNice to meet you.\nAnd this is Luming.\nHe's Chinese.\nNice to meet you.\nAnd this is Xiaohui.\nShe's Chinese, too.", "早上好。\n早上好，布莱克先生。\n这位是苏菲·杜邦小姐。\n苏菲是一名新学生。\n她是法国人。\n苏菲，这是汉斯。\n他是德国人。\n很高兴认识你。\n这是直子。\n她是日本人。\n很高兴认识你。\n这是昌宇。\n他是韩国人。\n很高兴认识你。\n这是鲁明。\n他是中国人。\n很高兴认识你。\n这是晓慧。\n她也是中国人。"),
            (6, "What nationality are you?", "What nationality are you?\nI'm French.\nWhat about Hans?\nHe's German.\nAre you French, too?\nNo, I'm not.\nI'm Korean.\nWhat nationality is Changwoo?\nHe's Korean.\nIs Naoko Japanese?\nYes, she is.\nIs she a teacher?\nNo, she isn't.\nShe's a student.", "你是哪国人？\n我是法国人。\n汉斯呢？\n他是德国人。\n你也是法国人吗？\n不，我不是。\n我是韩国人。\n昌宇是哪国人？\n他是韩国人。\n直子是日本人吗？\n是的，她是。\n她是老师吗？\n不，她不是。\n她是学生。"),
            (7, "Are you a teacher?", "What's your job?\nI'm a teacher.\nWhat about you?\nI'm a student.\nAre you a teacher?\nNo, I'm not.\nI'm a keyboard operator.\nWhat's his job?\nHe's an engineer.", "你的工作是什么？\n我是一名老师。\n你呢？\n我是一名学生。\n你是老师吗？\n不，我不是。\n我是电脑操作员。\n他的工作是什么？\n他是一名工程师。"),
            (8, "What's your job?", "What's your job?\nI'm a teacher.\nAre you a student?\nYes, I am.\nWhat's his job?\nHe's a policeman.\nWhat's her job?\nShe's a nurse.\nWhat nationality is he?\nHe's French.", "你的工作是什么？\n我是一名老师。\n你是学生吗？\n是的，我是。\n他的工作是什么？\n他是一名警察。\n她的工作是什么？\n她是一名护士。\n他是哪国人？\n他是法国人。"),
            (9, "How are you today?", "Hello, Helen.\nHi, Steven.\nHow are you today?\nI'm very well, thank you.\nAnd how are you?\nI'm fine, thanks.\nHow's Tony?\nHe's fine, thanks.\nHow's Emma?\nShe's very well, too, Helen.", "你好，海伦。\n嗨，史蒂文。\n你今天好吗？\n我很好，谢谢。\n你呢？\n我也很好，谢谢。\n托尼好吗？\n他很好，谢谢。\n埃玛好吗？\n她也很好，海伦。"),
            (10, "Look at…", "Look at that fat boy!\nWhich boy?\nThat fat boy, Paul.\nHe's very big.\nLook at that girl!\nWhich girl?\nThat thin girl, Lucy.\nShe's very pretty.\nLook at that man!\nWhich man?\nThat tall man, Mr. Smith.\nHe's very funny.", "看那个胖男孩！\n哪个男孩？\n那个胖男孩，保罗。\n他很大。\n看那个女孩！\n哪个女孩？\n那个瘦女孩，露西。\n她很漂亮。\n看那个男人！\n哪个男人？\n那个高个子男人，史密斯先生。\n他很有趣。"),
        ]

        for num, title, text, translation in lessons_data:
            lesson = Lesson(
                lesson_number=num,
                title=title,
                level="第一册",
                text=text,
                translation=translation,
                image_url=f"/resources/images/lesson_{num}.jpg",
                audio_url=f"/resources/audio/lesson_{num}.mp3",
            )
            session.add(lesson)
        session.commit()

        # ── Vocabulary for Lesson 1 ──────────────────────────────
        vocab_data = [
            (1, "excuse", "/ɪkˈskjuːz/", "v. 原谅"),
            (1, "me", "/miː/", "pron. 我（宾格）"),
            (1, "handbag", "/ˈhændbæɡ/", "n. 手提包"),
            (1, "pardon", "/ˈpɑːdn/", "int. 对不起，请再说一遍"),
            (1, "thank", "/θæŋk/", "v. 感谢"),
            (1, "very", "/ˈveri/", "adv. 非常"),
            (1, "much", "/mʌtʃ/", "adv. 许多，很"),
        ]

        for lesson_id, word, phonetic, meaning in vocab_data:
            v = Vocabulary(
                lesson_id=lesson_id,
                word=word,
                phonetic=phonetic,
                meaning=meaning,
            )
            session.add(v)

        # ── Grammar for Lesson 1 ─────────────────────────────────
        gp1 = GrammarPoint(
            lesson_id=1,
            name="一般疑问句 Is this…?",
            explanation="Is this + 名词? 用来确认某物是否属于对方。肯定回答: Yes, it is. 否定回答: No, it isn't.",
        )
        gp1.examples = ["Is this your handbag?", "Is this your pen?", "Is this your book?"]
        session.add(gp1)

        # ── Exercises for Lesson 1 ───────────────────────────────
        exercises_data = [
            (1, gp1.id, "mc", "— Is this your handbag?\n— ______, it is.", "Yes", ["Yes", "No", "OK"]),
            (1, gp1.id, "mc", "— Is this your pen?\n— No, it ______.", "isn't", ["is", "isn't", "are"]),
            (1, gp1.id, "fill_blank", "Is this ______ handbag?", "your", []),
        ]

        for lesson_id, gp_id, ex_type, question, answer, options in exercises_data:
            ex = Exercise(
                lesson_id=lesson_id,
                grammar_point_id=gp_id,
                type=ex_type,
                question=question,
                answer=answer,
            )
            ex.options = options
            session.add(ex)

        session.commit()
        print(f"✅ Seeded {len(lessons_data)} lessons, {len(vocab_data)} vocabulary words, "
              f"1 grammar point, {len(exercises_data)} exercises.")


if __name__ == "__main__":
    seed()
