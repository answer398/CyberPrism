#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量更新题目标题和描述
- 标题: 只保留"-"之前的内容,删除"-"及之后的部分
- 描述: 清空所有描述信息
"""
import sys
import os
import io

# 设置输出编码为UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from app.models import Challenge

def batch_update_challenges():
    """批量更新选择题的标题和描述"""
    with app.app_context():
        # 获取所有选择题
        challenges = Challenge.query.filter_by(type='choice').all()

        updated_count = 0

        for challenge in challenges:
            # 处理标题 - 只保留"-"之前的内容
            original_title = challenge.title
            if '-' in original_title:
                # 找到第一个"-"的位置,取之前的内容并去除首尾空格
                new_title = original_title.split('-')[0].strip()
            else:
                # 如果没有"-",保持原标题
                new_title = original_title.strip()

            # 清空描述
            new_description = ''

            # 如果有变化,则更新
            if challenge.title != new_title or challenge.description != new_description:
                print(f"更新题目 ID {challenge.id}:")
                print(f"  原标题: {original_title}")
                print(f"  新标题: {new_title}")
                print(f"  描述: 已清空")
                print()

                challenge.title = new_title
                challenge.description = new_description
                updated_count += 1

        # 提交更改
        try:
            db.session.commit()
            print(f"\n✓ 成功更新 {updated_count} 道题目!")
            print(f"总题目数: {len(challenges)}")
        except Exception as e:
            db.session.rollback()
            print(f"\n✗ 更新失败: {e}")
            return False

        return True

if __name__ == '__main__':
    print("开始批量更新题目...")
    print("=" * 60)
    batch_update_challenges()
