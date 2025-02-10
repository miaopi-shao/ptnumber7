# -*- coding: utf-8 -*-
"""
Created on Sat Feb  8 15:02:16 2025

@author: OAP-0001
"""
import pandas as pd
import matplotlib.pyplot as plt
import datetime

# 設定 matplotlib 可顯示中文（根據作業系統調整字型）
plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei']  # Windows
plt.rcParams['axes.unicode_minus'] = False

# 讀取 CSV，請確認檔案編碼正確
schedule = pd.read_csv("成員出沒時間表.csv", encoding="utf-8")

# 為每位成員指定一個顏色
member_colors = {
    "黃國豪": "red",
    "邵妙齊": "green",
    "JRU": "blue",
    "RJ-捷": "purple",
    "凱莉Kelly": "orange"
}

# 定義解析時間的函式
def parse_time(time_str):
    # 若儲存格內容包含「實體課」，則固定顯示 09:00 到 17:00，
    # 並以 type 標記為 "class" 以便後續區分
    if "實體課" in time_str:
        return {"type": "class", "start": datetime.time(9, 0), "end": datetime.time(17, 0)}
    elif time_str == "不明":
        return None
    else:
        try:
            # 正常情況下，假設格式為 "HH:MM-HH:MM"
            start, end = time_str.split("-")
            start_time = datetime.datetime.strptime(start, "%H:%M").time()
            end_time = datetime.datetime.strptime(end, "%H:%M").time()
            return {"type": "normal", "start": start_time, "end": end_time}
        except ValueError:
            return None

# 讓使用者選擇顯示模式
print("請選擇時間顯示模式: ")
print("1: 單日")
print("2: 一週 (7 天)")
print("3: 一個月 (4 週，每週 7 天)")
mode = input("請輸入 1、2 或 3: ")

members = schedule["成員"].tolist()

if mode == "1":
    # 單日模式：僅顯示使用者指定那一天
    day = input("請輸入要查看的星期 (例如: 星期一): ")
    if day not in schedule.columns:
        print("輸入錯誤，請檢查欄位名稱！")
        exit()
    
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.set_xlim(0, 24)
    ax.set_title(f"{day} 成員出沒時間")
    
    for i, member in enumerate(members):
        time_str = schedule.loc[i, day]
        parsed = parse_time(time_str)
        if parsed is not None:
            start, end = parsed["start"], parsed["end"]
            start_hour = start.hour + start.minute / 60
            end_hour = end.hour + end.minute / 60
            duration = end_hour - start_hour
            color = member_colors.get(member, "gray")
            if parsed["type"] == "class":
                # 針對實體課，使用半透明與條紋表示
                ax.barh(i, duration, left=start_hour, height=0.5, color=color,
                        alpha=0.5, hatch="//", edgecolor="black")
            else:
                ax.barh(i, duration, left=start_hour, height=0.5, color=color)
            ax.text(start_hour + duration/2, i, member, va='center', ha='center', fontsize=9, color="black")
    ax.set_yticks(range(len(members)))
    ax.set_yticklabels(members)
    ax.set_xlabel("時間 (24 小時制)")
    ax.grid(axis="x", linestyle="--", alpha=0.7)
    plt.tight_layout()
    plt.show()

elif mode == "2":
    # 一週模式：依據 CSV 中除「成員」外的所有星期建立子圖
    days = schedule.columns[1:]
    n_days = len(days)
    
    fig, axes = plt.subplots(nrows=n_days, ncols=1, sharex=True, figsize=(12, 3 * n_days))
    if n_days == 1:
        axes = [axes]
    
    for ax, day in zip(axes, days):
        ax.set_xlim(0, 24)
        ax.set_title(day)
        for i, member in enumerate(members):
            time_str = schedule.loc[i, day]
            parsed = parse_time(time_str)
            if parsed is not None:
                start, end = parsed["start"], parsed["end"]
                start_hour = start.hour + start.minute / 60
                end_hour = end.hour + end.minute / 60
                duration = end_hour - start_hour
                color = member_colors.get(member, "gray")
                if parsed["type"] == "class":
                    ax.barh(i, duration, left=start_hour, height=0.5, color=color,
                            alpha=0.5, hatch="//", edgecolor="black")
                else:
                    ax.barh(i, duration, left=start_hour, height=0.5, color=color)
                ax.text(start_hour + duration/2, i, member, va='center', ha='center', fontsize=9, color="black")
        ax.set_yticks(range(len(members)))
        ax.set_yticklabels(members)
        ax.grid(axis="x", linestyle="--", alpha=0.7)
    
    axes[-1].set_xlabel("時間 (24 小時制)")
    plt.tight_layout()
    plt.show()

elif mode == "3":
    # 一個月模式：假設每週排程相同，將排程複製 4 週，以 4x7 的方式呈現
    weeks = range(1, 5)
    days = schedule.columns[1:]
    n_days = len(days)
    
    fig, axes = plt.subplots(nrows=4, ncols=n_days, sharex=True, sharey=True, figsize=(3*n_days, 3*4))
    
    for w_idx, week in enumerate(weeks):
        for d_idx, day in enumerate(days):
            ax = axes[w_idx, d_idx]
            ax.set_xlim(0, 24)
            ax.set_title(f"第{week}週 {day}", fontsize=10)
            for i, member in enumerate(members):
                time_str = schedule.loc[i, day]
                parsed = parse_time(time_str)
                if parsed is not None:
                    start, end = parsed["start"], parsed["end"]
                    start_hour = start.hour + start.minute / 60
                    end_hour = end.hour + end.minute / 60
                    duration = end_hour - start_hour
                    color = member_colors.get(member, "gray")
                    if parsed["type"] == "class":
                        ax.barh(i, duration, left=start_hour, height=0.5, color=color,
                                alpha=0.5, hatch="//", edgecolor="black")
                    else:
                        ax.barh(i, duration, left=start_hour, height=0.5, color=color)
                    ax.text(start_hour + duration/2, i, member, va='center', ha='center', fontsize=8, color="black")
            ax.set_yticks(range(len(members)))
            ax.set_yticklabels(members, fontsize=8)
            ax.grid(axis="x", linestyle="--", alpha=0.7)
    
    axes[-1, 0].set_ylabel("成員")
    for ax in axes[-1]:
        ax.set_xlabel("時間 (24 小時制)")
    plt.tight_layout()
    plt.show()

else:
    print("輸入錯誤，請重新執行程式！")
