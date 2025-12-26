#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
更新题目的skill_tags - 将题目与正确的技能代码关联
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

# 技能标签矩阵（与前端保持一致）
SKILL_MATRIX = {
    "信息收集与侦察": {
        "信息收集": "T1071",
        "网络扫描": "T1046",
        "子域枚举": "T1071",
        "网络拓扑分析": "T1027"
    },
    "漏洞利用与攻击": {
        "利用公共漏洞": "T1203",
        "提权与横向移动": "T1075",
        "社会工程学攻击": "T1071",
        "恶意软件": "T1053"
    },
    "后渗透": {
        "横向移动": "T1021",
        "后门植入": "T1012",
        "权限提升": "T1088"
    },
    "防御规避与反侦察": {
        "权限提升": "T1088",
        "文件/日志清理": "T1070",
        "命令与控制": "T1071"
    }
}

# 技能名称到题目标题关键词的映射
SKILL_KEYWORDS = {
    "信息收集": ["信息收集", "WHOIS", "Google Hacking", "DNS记录", "社会工程学攻击中最常用"],
    "网络扫描": ["Nmap", "端口", "TCP", "扫描"],
    "子域枚举": ["子域", "Sublist3r", "Certificate Transparency", "Zone Transfer"],
    "网络拓扑分析": ["traceroute", "DMZ", "路由"],
    "利用公共漏洞": ["CVE", "CVSS", "Exploit-DB", "Web漏洞"],
    "提权与横向移动": ["su", "PsExec", "SUID", "Pass-the-Hash"],
    "社会工程学攻击": ["钓鱼", "SET", "社会工程学"],
    "恶意软件": ["勒索软件", "APT", "Rootkit", "沙箱"],
    "横向移动": ["Mimikatz", "Golden Ticket", "SMB"],
    "后门植入": ["持久化", "Webshell", "反向Shell"],
    "权限提升": ["Administrator", "UAC", "内核漏洞", "进程注入", "DLL劫持", "应用程序白名单"],
    "文件/日志清理": ["事件日志", "history", "Timestomping", "sdelete"],
    "命令与控制": ["C2", "Domain Fronting", "DNS隧道", "Beacon"]
}

def update_skill_tags():
    """更新所有题目的skill_tags"""
    with app.app_context():
        # 获取所有选择题
        challenges = Challenge.query.filter_by(type='choice').all()

        updated_count = 0

        for challenge in challenges:
            category = challenge.category
            if category not in SKILL_MATRIX:
                print(f"警告: 未知类别 {category}")
                continue

            # 根据题目内容匹配技能标签
            matched_skills = {}
            question_text = (challenge.title or "") + " " + (challenge.question or "")

            for skill_name, keywords in SKILL_KEYWORDS.items():
                # 检查该技能是否属于当前类别
                if skill_name in SKILL_MATRIX[category]:
                    # 检查题目中是否包含该技能的关键词
                    for keyword in keywords:
                        if keyword in question_text:
                            skill_code = SKILL_MATRIX[category][skill_name]
                            matched_skills[skill_code] = skill_name
                            break

            if matched_skills:
                # 更新skill_tags
                challenge.skill_tags = json.dumps(matched_skills, ensure_ascii=False)
                updated_count += 1
                print(f"✓ 更新题目: {challenge.title[:30]}... -> {list(matched_skills.values())}")

        # 提交更改
        try:
            db.session.commit()
            print(f"\n✓ 成功更新 {updated_count} 道题目的skill_tags!")
        except Exception as e:
            db.session.rollback()
            print(f"\n✗ 更新失败: {e}")
            return False

        # 验证统计
        print("\n验证结果:")
        for category, skills in SKILL_MATRIX.items():
            print(f"\n{category}:")
            for skill_name, skill_code in skills.items():
                # 查询包含该技能代码的题目数
                count = Challenge.query.filter(
                    Challenge.category == category,
                    Challenge.skill_tags.like(f'%{skill_code}%')
                ).count()
                print(f"  {skill_name} ({skill_code}): {count} 道题目")

        return True

if __name__ == '__main__':
    update_skill_tags()
