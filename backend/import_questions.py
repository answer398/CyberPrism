#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
题目导入脚本 - 将question_bank.json中的题目批量导入数据库
"""
import json
import sys
import os
import io

# 设置输出编码为UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from app.models import Challenge

def import_questions():
    """从question_bank.json导入题目"""
    with app.app_context():
        # 读取题库
        with open('question_bank.json', 'r', encoding='utf-8') as f:
            question_bank = json.load(f)

        added_count = 0

        # 遍历所有类别
        for category, skills in question_bank.items():
            print(f"\n处理类别: {category}")

            # 遍历每个技能
            for skill_name, questions in skills.items():
                print(f"  处理技能: {skill_name}")

                # 遍历该技能下的所有题目
                for q in questions:
                    # 检查题目是否已存在（通过标题判断）
                    existing = Challenge.query.filter_by(
                        title=q.get('title', f"{skill_name}题目"),
                        question=q['question']
                    ).first()

                    if existing:
                        print(f"    跳过重复题目: {q['question'][:30]}...")
                        continue

                    # 创建新题目
                    challenge = Challenge(
                        title=skill_name,  # 只使用技能名称作为标题
                        description='',  # 描述为空
                        category=category,
                        type='choice',
                        difficulty=q['difficulty'],
                        points=q['points'],
                        question=q['question'],
                        options=json.dumps(q['options'], ensure_ascii=False),
                        correct_answer=q['correct_answer'],
                        skill_tags=json.dumps(q.get('skill_tags', {}), ensure_ascii=False),
                        is_active=True
                    )

                    db.session.add(challenge)
                    added_count += 1
                    print(f"    ✓ 添加题目: {q['question'][:40]}...")

        # 提交所有更改
        try:
            db.session.commit()
            print(f"\n✓ 成功导入 {added_count} 道题目!")
        except Exception as e:
            db.session.rollback()
            print(f"\n✗ 导入失败: {e}")
            return False

        # 显示统计信息
        total_challenges = Challenge.query.filter_by(type='choice').count()
        print(f"\n数据库中选择题总数: {total_challenges}")

        # 按类别统计
        print("\n各类别题目统计:")
        for category in question_bank.keys():
            count = Challenge.query.filter_by(category=category, type='choice').count()
            print(f"  {category}: {count} 道")

        return True

if __name__ == '__main__':
    import_questions()
