import pandas as pd

# 读取文本文件
df = pd.read_csv('dist.txt', header=None, names=['data'])

# 将 "data" 列拆分成两列
df[['distance', 'timestamp']] = df.data.str.split(',', expand=True)

# 按时间戳对数据进行排序
df = df.sort_values(by='timestamp')

# 删除 "data" 列
df.drop(['data'], axis=1, inplace=True)

# 将结果保存到 CSV 文件中
df.to_csv('output.csv', index=False)