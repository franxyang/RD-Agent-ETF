#!/usr/bin/env python
"""测试pickle兼容性"""

import pickle
import numpy as np
import scipy
from scipy.sparse import csr_matrix, eye
import pandas as pd
import tempfile
import os

print("="*60)
print("Pickle兼容性测试")
print("="*60)

# 测试各种数据类型的pickle序列化
test_data = {
    "numpy_array": np.array([1, 2, 3, 4, 5]),
    "numpy_2d": np.random.rand(10, 5),
    "scipy_sparse": csr_matrix(eye(5)),
    "pandas_series": pd.Series([1, 2, 3, 4, 5]),
    "pandas_df": pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]}),
    "multiindex_df": pd.DataFrame(
        {"value": np.random.rand(20)},
        index=pd.MultiIndex.from_product(
            [pd.date_range("2020-01-01", periods=10), ["A", "B"]],
            names=["datetime", "instrument"]
        )
    )
}

# 创建临时文件进行测试
with tempfile.NamedTemporaryFile(suffix=".pkl", delete=False) as tmp:
    tmp_path = tmp.name

try:
    # 测试每种数据类型
    for name, data in test_data.items():
        print(f"\n测试 {name}:")
        print(f"  类型: {type(data)}")
        
        # 序列化
        with open(tmp_path, "wb") as f:
            pickle.dump(data, f, protocol=4)  # 使用protocol 4提高兼容性
        
        # 反序列化
        with open(tmp_path, "rb") as f:
            loaded_data = pickle.load(f)
        
        # 验证
        if isinstance(data, np.ndarray):
            assert np.allclose(data, loaded_data), f"{name} 数据不一致"
        elif isinstance(data, pd.DataFrame) or isinstance(data, pd.Series):
            pd.testing.assert_frame_equal(data, loaded_data) if isinstance(data, pd.DataFrame) else pd.testing.assert_series_equal(data, loaded_data)
        elif scipy.sparse.issparse(data):
            assert (data - loaded_data).nnz == 0, f"{name} 稀疏矩阵不一致"
        
        print(f"  ✅ 序列化/反序列化成功")
        
finally:
    # 清理临时文件
    if os.path.exists(tmp_path):
        os.remove(tmp_path)

print("\n" + "="*60)
print("总结:")
print(f"NumPy版本: {np.__version__}")
print(f"SciPy版本: {scipy.__version__}")
print(f"Pandas版本: {pd.__version__}")
print("✅ 所有pickle兼容性测试通过")
print("="*60)