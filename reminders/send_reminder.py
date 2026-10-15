#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
每月10号：发工资提醒，通过 WxPusher 推送到微信。

只依赖 Python 标准库，不需要 pip install。

需要的环境变量（在 GitHub 仓库的 Secrets 里配置）：
  WXPUSHER_APP_TOKEN  —— WxPusher 应用的 AppToken（AT_ 开头）
  WXPUSHER_UID        —— 接收提醒的微信用户 UID（UID_ 开头）

要改提醒文案，只改下面 CONTENT 这一段就行。
"""

import json
import os
import sys
import urllib.request

# ---- 想改提醒内容，改这里（这中间的换行会原样保留） ----
CONTENT = """【数据更新提醒】今天10号，发的是上个月的工资。

把这三个数报一下，方便更新档案：
1) 到手工资金额
2) 当月课消（上完的课对应的金额）
3) 当月课包销售（新签的单）

不方便拆那么细，报一个到手总额也行。
"""

SUMMARY = "数据更新提醒"
API = "https://wxpusher.zjiecode.com/api/send/message"


def main() -> int:
    app_token = os.environ.get("WXPUSHER_APP_TOKEN", "").strip()
    uid = os.environ.get("WXPUSHER_UID", "").strip()

    if not app_token or not uid:
        print("缺少环境变量 WXPUSHER_APP_TOKEN 或 WXPUSHER_UID", file=sys.stderr)
        return 2

    payload = {
        "appToken": app_token,
        "content": CONTENT,
        "summary": SUMMARY,
        "contentType": 1,          # 1=纯文本
        "uids": [uid],
    }

    req = urllib.request.Request(
        API,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urllib.request.urlopen(req, timeout=30) as resp:
        body = resp.read().decode("utf-8")

    print(body)

    try:
        result = json.loads(body)
    except json.JSONDecodeError:
        print("返回不是合法 JSON，推送结果未知", file=sys.stderr)
        return 1

    if result.get("code") != 1000:
        print(f"接口失败：{result.get('msg')}", file=sys.stderr)
        return 1

    # 逐条检查每个 uid 的发送状态
    for item in result.get("data", []):
        if item.get("code") != 1000:
            print(f"给 {item.get('uid')} 发送失败：{item.get('status')}", file=sys.stderr)
            return 1

    print("推送成功")
    return 0


if __name__ == "__main__":
    sys.exit(main())
