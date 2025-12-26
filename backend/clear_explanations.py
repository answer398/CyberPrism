#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
清空question_bank.json中所有题目的explanation字段
"""
import json
import sys
import io

# 设置输出编码为UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def clear_explanations():
    """清空所有题目的explanation字段"""
    # 读取题库
    with open('question_bank.json', 'r', encoding='utf-8') as f:
        question_bank = json.load(f)

    cleared_count = 0

    # 遍历所有类别
    for category, skills in question_bank.items():
        print(f"\n处理类别: {category}")

        # 遍历每个技能
        for skill_name, questions in skills.items():
            print(f"  处理技能: {skill_name}")

            # 遍历该技能下的所有题目
            for q in questions:
                # 删除explanation字段
                if 'explanation' in q:
                    del q['explanation']
                    cleared_count += 1

    # 写回文件
    with open('question_bank.json', 'w', encoding='utf-8') as f:
        json.dump(question_bank, f, ensure_ascii=False, indent=2)

    print(f"\n✓ 成功清空 {cleared_count} 道题目的explanation字段!")

if __name__ == '__main__':
    print("开始清空explanation字段...")
    print("=" * 60)
    clear_explanations()
