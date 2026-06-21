import os, re, sys, json

root = sys.argv[1]
if not root.endswith("/") and not root.endswith("\\"):
    root += os.sep

# 扫描所有日期序号文件夹，提取趋势数据
folders = sorted(
    [f for f in os.listdir(root) if os.path.isdir(os.path.join(root, f))],
    key=lambda x: (x.split("_")[0], int(x.split("_")[1]) if "_" in x and x.split("_")[1].isdigit() else 0)
)

trend_data = []   # [{date, label, sub_score, total_score}]
latest_wrq = None

for f in folders:
    folder_path = os.path.join(root, f)
    eval_path = os.path.join(folder_path, "EvaluateQuestions.md")
    wrq_path = os.path.join(folder_path, "WrQuestions.md")
    if not os.path.exists(eval_path):
        continue
    text = open(eval_path, encoding="utf-8").read()
    # 提取总分：找到包含"综合得分"或"加权总分"的行，取最后一个数字
    total_score = None
    for line in text.split("\n"):
        if "综合得分" in line or "加权总分" in line:
            nums = re.findall(r"\d+(?:\.\d+)?", line)
            if nums:
                total_score = float(nums[-1])
            break
    # 提取四个维度子分
    dims = {}
    for dim_name in ["完整性", "深度", "逻辑性", "一致性"]:
        dm = re.search(rf"{dim_name}\s*\|\s*\d+%\s*\|\s*(\d+(?:\.\d+)?)", text)
        if dm:
            dims[dim_name] = float(dm.group(1))
    date_part = f.split("_")[0]
    trend_data.append({
        "date": date_part,
        "label": f"{date_part[:4]}-{date_part[4:6]}-{date_part[6:8]} #{f.split('_')[1] if '_' in f else '1'}",
        "folder": f,
        "total_score": total_score,
        "dims": dims
    })
    # 取最新的 WrQuestions
    wrq_path = os.path.join(folder_path, "WrQuestions.md")
    if os.path.exists(wrq_path):
        latest_wrq = wrq_path

# 解析最新 WrQuestions 维度分布
dim_labels = []
dim_values = []
dim_colors = []
if latest_wrq:
    text = open(latest_wrq, encoding="utf-8").read()
    lines = text.split("\n")
    table_start = False
    from collections import Counter
    dim_counter = Counter()
    for line in lines:
        if line.startswith("| 题号"):
            table_start = True
            continue
        if table_start and line.startswith("|"):
            cols = [c.strip() for c in line.split("|") if c.strip()]
            if len(cols) >= 2 and (cols[0].startswith("Q") or cols[0].startswith("**Q")):
                # 去掉标记符号 {不满意}
                dim_name = re.sub(r"\s*\{[^}]*\}", "", cols[1])
                dim_counter[dim_name] += 1
        elif table_start and not line.startswith("|"):
            break
    dim_labels = list(dim_counter.keys())
    dim_values = list(dim_counter.values())
    # 预定义颜色池
    color_pool = ["#FF6384", "#36A2EB", "#FFCE56", "#4BC0C0", "#9966FF", "#FF9F40", "#C9CBCF", "#7BC8A4"]
    dim_colors = color_pool[:len(dim_labels)]

# 生成 HTML
labels_json = json.dumps([d["label"] for d in trend_data])
scores_json = json.dumps([d["total_score"] for d in trend_data])
dim_labels_json = json.dumps(dim_labels)
dim_values_json = json.dumps(dim_values)
dim_colors_json = json.dumps(dim_colors)
sub_dims_json = json.dumps({d["label"]: d["dims"] for d in trend_data})

html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>模拟面试报告</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ font-family: "Microsoft YaHei", "PingFang SC", sans-serif; background: #f5f7fa; color: #333; padding: 24px; }}
h1 {{ text-align: center; margin-bottom: 24px; color: #1a1a2e; }}
.container {{ display: flex; gap: 24px; max-width: 1200px; margin: 0 auto; flex-wrap: wrap; }}
.card {{ background: #fff; border-radius: 12px; box-shadow: 0 2px 12px rgba(0,0,0,0.08); padding: 24px; flex: 1; min-width: 420px; }}
.card h2 {{ font-size: 18px; margin-bottom: 16px; color: #555; border-bottom: 2px solid #e8ecf1; padding-bottom: 10px; }}
.chart-wrap {{ position: relative; width: 100%; }}
.no-data {{ text-align: center; color: #999; padding: 60px 0; font-size: 16px; }}
.timestamp {{ text-align: center; color: #aaa; font-size: 13px; margin-top: 24px; }}
</style>
</head>
<body>
<h1>📊 模拟面试报告</h1>
<div class="container">
  <div class="card">
    <h2>📈 分数趋势</h2>
    <div class="chart-wrap">
      <canvas id="trendChart"></canvas>
    </div>
  </div>
  <div class="card">
    <h2>📌 最新错误维度分布</h2>
    <div class="chart-wrap">
      <canvas id="dimChart"></canvas>
    </div>
  </div>
</div>
<p class="timestamp">生成时间：自动 | 数据来源：my-interview/</p>
<script>
const trendLabels = {labels_json};
const trendScores = {scores_json};
const dimLabels = {dim_labels_json};
const dimValues = {dim_values_json};
const dimColors = {dim_colors_json};
const subDims = {sub_dims_json};

// 分数趋势图
if (trendLabels.length > 0) {{
  new Chart(document.getElementById('trendChart'), {{
    type: 'line',
    data: {{
      labels: trendLabels,
      datasets: [{{
        label: '面试总评分',
        data: trendScores,
        borderColor: '#36A2EB',
        backgroundColor: 'rgba(54,162,235,0.1)',
        fill: true,
        tension: 0.3,
        pointRadius: 5,
        pointHoverRadius: 7,
        pointBackgroundColor: '#36A2EB'
      }}]
    }},
    options: {{
      responsive: true,
      plugins: {{
        legend: {{ display: true, position: 'bottom' }},
        tooltip: {{
          callbacks: {{
            label: ctx => `总分: ${{ctx.parsed.y}}`
          }}
        }}
      }},
      scales: {{
        y: {{ min: 0, max: 100, title: {{ display: true, text: '分数' }} }},
        x: {{ title: {{ display: true, text: '面试轮次' }} }}
      }}
    }}
  }});
}} else {{
  document.getElementById('trendChart').parentElement.innerHTML = '<div class="no-data">暂无面试数据</div>';
}}

// 错误维度饼图
if (dimLabels.length > 0) {{
  new Chart(document.getElementById('dimChart'), {{
    type: 'pie',
    data: {{
      labels: dimLabels,
      datasets: [{{
        data: dimValues,
        backgroundColor: dimColors
      }}]
    }},
    options: {{
      responsive: true,
      plugins: {{
        legend: {{ display: true, position: 'bottom', labels: {{ padding: 16 }} }},
        tooltip: {{
          callbacks: {{
            label: ctx => `${{ctx.label}}: ${{ctx.parsed}} 题 (${{((ctx.parsed / dimValues.reduce((a,b) => a+b, 0)) * 100).toFixed(1)}}%)`
          }}
        }}
      }}
    }}
  }});
}} else {{
  document.getElementById('dimChart').parentElement.innerHTML = '<div class="no-data">暂无错题数据</div>';
}}
</script>
</body>
</html>"""

output_path = os.path.join(root, "report.html")
with open(output_path, "w", encoding="utf-8") as f:
    f.write(html)

print(f"report.html 已生成 → {output_path}")
print(f"趋势数据: {len(trend_data)} 轮")
print(f"错题维度: {len(dim_labels)} 个维度")
