import pandas as pd
import matplotlib.pyplot as plt
# Đọc dữ liệu
df = pd.read_csv("boston.csv", sep=';', header=None)
df.columns = ['year', 'sea_level_mm', 'uncertainty_1', 'uncertainty_2']

# Tách năm và tháng từ cột year
df['year_int'] = df['year'].astype(int)
df['month_fraction'] = df['year'] - df['year_int']
df['month'] = (df['month_fraction'] * 12 + 1).astype(int)  # +1 vì tháng bắt đầu từ 1
df['date'] = pd.to_datetime(dict(year=df['year_int'], month=df['month'], day=1))

# Hiển thị kết quả
print(df[['date', 'sea_level_mm']].head())


# Vẽ biểu đồ
plt.figure(figsize=(10, 5))
plt.plot(df['date'], df['sea_level_mm'], label='Sea Level (mm)', color='blue')
plt.xlabel('Year')
plt.ylabel('Sea Level (mm)')
plt.title('Sea Level Rise Over Time - Boston')
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()

# In dữ liệu gần các năm có vấn đề
print(df[df['date'].between('1985', '1995')])
print(df[df['date'].between('2005', '2015')])
print(df[df['date'].between('2015', '2020')])
