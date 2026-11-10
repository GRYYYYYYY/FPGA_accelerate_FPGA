import matplotlib.pyplot as plt
import numpy as np

# 数据
labels = ['IS18_1', 'IS18_2', 'IS18_3', 'IS18_4', 'IS18_5', 'IS18_6', 'IS18_7', 'IS18_8', 'IS18_9', 'IS18_10',
          'IS19_1', 'IS19_2', 'IS19_3', 'IS19_4', 'IS19_5', 'IS19_6', 'IS19_7', 'IS19_8', 'IS19_9', 'IS19_10', 'average']
gr_values_triton = [4, 15, 19, 67, 85, 83, 197, 221, 89, 190, 3, 42, 6, 1748, 226, 125, 219, 280, 440, 542, 230.05]
dr_values_triton = [20, 152, 634, 328, 422, 588, 1306, 1379, 1004, 1540, 52, 834, 184, 2008, 74, 1795, 3768, 4474, 7205, 8639, 1820.3]
gr_values_cugr =   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 89, 42, 1753, 205, 33, 93, 57, 124, 368, 276.6]
dr_values_cugr =   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 118, 1260, 56, 1328, 115, 2213, 5288, 7401, 10166, 10665, 3861]
# gr_values_cugr =   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 3, 9, 35, 11, 123, 149, 21, 112, 46.6]
# dr_values_cugr =   [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 71, 815, 1984, 1663, 1939, 2964, 6673, 6691, 5588, 8401, 3678.9]
# gr_values_rerun =  [2, 89, 42, 1753, 205, 33, 93, 57, 124, 368, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 276.6]
# dr_values_rerun =  [118, 1260, 56, 1328, 115, 2213, 5288, 7401, 10166, 10665, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3861]

# 设置柱状图的位置
x = np.arange(len(labels))
width = 0.2  # 柱状图的宽度

# 创建图形和轴
fig, ax = plt.subplots(figsize=(16, 8))

# 绘制堆叠柱状图
ax.bar(x - width, dr_values_triton, width, label='TritonRoute-WXL DR', color='#f8cecc')
ax.bar(x - width, gr_values_triton, width, bottom=dr_values_triton, label='TritonRoute-WXL GR', color='#b85450')

ax.bar(x, dr_values_cugr, width, label='CUGR-Dr.CU 2.0  DR', color='#dae8fc')
ax.bar(x, gr_values_cugr, width, bottom=dr_values_cugr, label='CUGR-Dr.CU 2.0  GR', color='#6c8ebf')

# ax.bar(x + width, dr_values_rerun, width, label='rerun TritonRoute-WXL DR', color='#dae8fc')
# ax.bar(x + width, gr_values_rerun, width, bottom=dr_values_rerun, label='rerun TritonRoute-WXL GR', color='#6c8ebf')

# 添加标题和标签
ax.set_title('GR vs DR Time Distribution', fontsize=30, fontweight='bold')
ax.set_xlabel('(a)', fontsize=25)
ax.set_ylabel('Runtime(s)', fontsize=25, fontweight='bold')

# 设置x轴刻度
ax.set_xticks(x)
ax.set_xticklabels(labels, rotation=45, ha='right')

# # 设置坐标轴刻度字体大小
# ax.tick_params(axis='both', which='major', labelsize=16) # 刻度线宽度 # 刻度线长度
# 设置坐标轴属性
# ax.tick_params(axis='x', which='major', 
#                labelsize=16, labelweight='bold',
#                rotation=45, length=6, width=2)
# ax.tick_params(axis='y', which='major',
#                labelsize=16, labelweight='bold',
#                length=6, width=2)

# 设置坐标轴刻度属性（修正版）
ax.tick_params(axis='both', which='major', 
               labelsize=25,  # 字体大小
               width=2,       # 刻度线宽度
               length=6)      # 刻度线长度

# 加粗刻度标签（单独设置）
for label in ax.get_xticklabels() + ax.get_yticklabels():
    label.set_fontweight('bold')


# 添加图例
# ax.legend(fontsize=20, prop={'weight': 'bold', 'size': 20})
ax.legend(prop={'size': 25, 'weight': 'bold'},  # 将 fontsize 合并到 prop 中
          handlelength=3.0,
          handleheight=2.0)

# 添加网格
ax.grid(True, linestyle='--', alpha=0.7)

# 标注DR的占比
for i in range(len(x)):
    total_triton = gr_values_triton[i] + dr_values_triton[i]
    dr_ratio_triton = dr_values_triton[i] / total_triton * 100 if total_triton > 0 else 0
    ax.annotate(f'{dr_ratio_triton:.1f}%',
                xy=(x[i] - width / 2, dr_values_triton[i] / 2),
                xytext=(-2, 3),  # 3 points vertical offset
                textcoords="offset points",
                ha='center', va='center', fontsize=20, color='black', fontweight='bold')

for i in range(len(x)):
    if (i>=11):
        total_cugr = gr_values_cugr[i] + dr_values_cugr[i]
        dr_ratio_cugr = dr_values_cugr[i] / total_cugr * 100 if total_cugr > 0 else 0
        ax.annotate(f'{dr_ratio_cugr:.1f}%',
                    xy=(x[i], (gr_values_cugr[i] + dr_values_cugr[i]) / 2),
                    xytext=(2, 20),  # 3 points vertical offset
                    textcoords="offset points",
                    ha='center', va='center', fontsize=20, color='black', fontweight='bold')

    # total_rerun = gr_values_rerun[i] + dr_values_rerun[i]
    # dr_ratio_rerun = dr_values_rerun[i] / total_rerun * 100 if total_rerun > 0 else 0
    # ax.annotate(f'{dr_ratio_rerun:.1f}%',
    #             xy=(x[i] + width / 2, (gr_values_rerun[i] + dr_values_rerun[i]) / 2),
    #             xytext=(10, 30),  # 3 points vertical offset
    #             textcoords="offset points",
    #             ha='center', va='center', fontsize=10, color='black')
# 加粗坐标轴
for spine in ax.spines.values():
    spine.set_linewidth(2)  # 加粗边框

# 隐藏顶部和右侧的外框
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

# 设置背景颜色为白色
ax.set_facecolor('white')

# 显示图形
plt.tight_layout()  # 自动调整子图参数，使之填充整个图像区域
plt.savefig("Detailed Routing.pdf")
plt.show()