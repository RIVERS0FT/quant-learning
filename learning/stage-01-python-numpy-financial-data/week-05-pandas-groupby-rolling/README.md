# 第 5 周：pandas 分组与滚动计算

## 本周目标

- 掌握 `groupby`、`shift`、`rolling`、`rank` 和 `merge`。
- 完成多股票分组计算。
- 构造未来收益标签与截面排名。

## 核心成果

计算 5 日、20 日收益、均线、波动率和截面排名。

## 每日安排

每日学习内容与索引均直接保存在当前周目录。

## 完成标准

- 所有指标按股票分组计算。
- 不发生未来数据泄漏。
- 结果通过抽样手工核验。

## 每日学习路径

| 天 | 主题 | 学习与实践 | 当天输出 |
|---:|---|---|---|
| 1 | [`groupby` 多股票分组计算](day-01-groupby.md) | 排序、按股票分组、收益率与 `transform` | `group_features.py` |
| 2 | [`shift` 与时间序列对齐](day-02-shift.md) | 滞后价格、未来价格与未来收益标签 | `add_future_return()` |
| 3 | [`rolling` 与移动平均线](day-03-rolling-moving-average.md) | 5 日与 20 日均线、均线偏离度 | `add_moving_average()` |
| 4 | [滚动收益率与滚动波动率](day-04-returns-volatility.md) | 多周期收益、20 日波动率与年化 | `add_return_features()` |
| 5 | [`rank` 与股票截面排名](day-05-cross-sectional-rank.md) | 每日动量、成交额与波动率百分位排名 | `add_cross_sectional_rank()` |
| 6 | [`merge` 与多表合并](day-06-merge-data.md) | 行情、行业与因子表合并，主键检查 | `safe_merge()` |
| 7 | [多股票特征工程综合项目](day-07-feature-pipeline-project.md) | 整合特征、标签、检查与数据输出 | `daily_features.parquet` |

## 本周核心函数

```python
df.sort_values()
df.groupby()
df.transform()
df.shift()
df.pct_change()
df.rolling()
df.rank()
df.merge()
df.duplicated()
df.dropna()
df.reset_index()
```

## 本周检查清单

- [ ] 时间序列计算前按股票代码和交易日期排序。
- [ ] 收益率、均线和波动率按股票分组计算。
- [ ] 截面排名按交易日期分组计算。
- [ ] 标签可以使用未来价格，特征只使用当时可见数据。
- [ ] 每只股票最后 $N$ 行的未来 $N$ 日收益率为空。
- [ ] 合并前检查主键是否重复。
- [ ] 合并后行数符合预期。
- [ ] 缺失值来源可以解释。
- [ ] 关键计算经过手工核验和单元测试。

## 本周最终成果

```text
data/processed/daily_features.parquet
```

最终特征表至少包含：

```text
trade_date
symbol
close
volume
amount
return_1d
return_5d
return_20d
ma_5
ma_20
close_ma20_ratio
volatility_20d
annual_volatility_20d
return_20d_rank_pct
amount_rank_pct
volatility_rank_pct
future_return_1d
future_return_5d
```
