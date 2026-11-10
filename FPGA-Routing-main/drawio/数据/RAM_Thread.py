import matplotlib.pyplot as plt
import numpy as np

# ---------- 图1数据 ----------
ram_blocks1 = [80, 100, 200, 500, 800, 1000]
ra_tr_times1 = [7.22029704551844, 6.576189077, 5.12898893347305, 3.508180093030388, 3.182610154, 2.947219631]
cora_tr_times1 = [3.5724881443672167, 3.304960813061106, 2.7245289422241528, 2.273860592238633, 2.1276797350130323, 2.0867863995076745]

# ---------- 图2数据 ----------
ram_blocks2 = [1, 2, 4, 8, 16]
ra_tr_times2 = [36, 18.5, 9.6, 5.1, 3]
cora_tr_times2 = [16, 8, 4, 2, 1.1]
speed_up_ratio2=[2.25, 2.3125, 2.4, 2.55, 2.727273]

# 创建一个画布，1行2列的子图
fig, axes = plt.subplots(1, 2, figsize=(20, 6))  # figsize调大一点方便排版

# ================== 子图1 ==================
ax = axes[0]
x = np.arange(len(ram_blocks1))
width = 0.35
rects1 = ax.bar(x - width/2, ra_tr_times1, width, label='RA-TR', color='#6c8ebf')
rects2 = ax.bar(x + width/2, cora_tr_times1, width, label='CoRA-TR', color='#ffcccc')
# rects1 = ax.bar(x - width/2, ra_tr_times1, width, label='RA-TR Avg Time', color='#6c8ebf')
# rects2 = ax.bar(x + width/2, cora_tr_times1, width, label='CoRA-TR Avg Time', color='#ffcccc')
ax.set_title('Average Time vs Number of RAM', fontsize=30, fontweight='bold')
ax.set_xlabel('Number of RAM', fontsize=25, fontweight='bold')
ax.set_ylabel('Average Time (ms)', fontsize=25, fontweight='bold')
# ax.set_ylabel('Average Time (ms/10000 pts)', fontsize=25, fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels(ram_blocks1)
ax.tick_params(axis='both', which='major', labelsize=25, width=2, length=6)
for label in ax.get_xticklabels() + ax.get_yticklabels():
    label.set_fontweight('bold')
# ax.legend(fontsize=25, 
#           prop={'weight': 'bold'},
#           markerscale=3.0,#成倍放大色块（比如 2.0 = 2 倍）
#           )
# 代码中图例字体大小设置没有生效的原因在于 Matplotlib 的 legend()函数中 fontsize参数与 prop参数的优先级问题。
# 当同时使用 prop参数时，它会覆盖 fontsize设置。
# ax.legend(fontsize=60,
#           prop={'size': 25,'weight': 'bold'},
#           handlelength=6.0,   # 控制色块横向长度
#           handleheight=4.0,   # 控制色块纵向高度
#         #   borderpad=1.2,      # 图例边框和内容的距离
#         #   labelspacing=1.2    # 各图例项之间的行间距
#           )
ax.legend(prop={'size':20, 'weight': 'bold'},  # 将 fontsize 合并到 prop 中
          handlelength=3.0,
          handleheight=2.0)

ax.grid(True, linestyle='--', alpha=0.7)
for spine in ax.spines.values():
    spine.set_linewidth(2)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.set_facecolor('white')

# ================== 子图2 ==================
ax = axes[1]
x = np.arange(len(ram_blocks2))
width = 0.25
rects1 = ax.bar(x - width, ra_tr_times2, width, label='CPU', color='#6c8ebf')
rects2 = ax.bar(x, cora_tr_times2, width, label='FPGA', color='#ffcccc')
rects3 = ax.bar(x + width, speed_up_ratio2, width, label='Speed up', color="#fff2cc")

ax.set_title('Average Runtime vs Thread Count', fontsize=30, fontweight='bold')
ax.set_xlabel('Thread Count', fontsize=25, fontweight='bold')
ax.set_ylabel('Average Runtime (ms)', fontsize=25, fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels(ram_blocks2)
ax.tick_params(axis='both', which='major', labelsize=25, width=2, length=6) # labelsize放大坐标轴数字
for label in ax.get_xticklabels() + ax.get_yticklabels():
    label.set_fontweight('bold')
# ax.legend(fontsize=25, 
#           prop={'weight': 'bold'},
#           markerscale=3.0,#成倍放大色块（比如 2.0 = 2 倍）
#           )
# ax.legend(fontsize=40,
#           prop={'size'25,'weight': 'bold'},
#           handlelength=6.0,   # 控制色块横向长度
#           handleheight=4.0,   # 控制色块纵向高度
#         #   borderpad=1.2,      # 图例边框和内容的距离
#         #   labelspacing=1.2    # 各图例项之间的行间距
#           )
ax.legend(prop={'size': 20, 'weight': 'bold'},  # 将 fontsize 合并到 prop 中
          handlelength=3.0,
          handleheight=2.0)

ax.grid(True, linestyle='--', alpha=0.7)
for spine in ax.spines.values():
    spine.set_linewidth(2)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.set_facecolor('white')

# ================== 输出到同一个PDF ==================
plt.tight_layout()
plt.savefig("RAM_Thread.pdf", format="pdf")
plt.show()
