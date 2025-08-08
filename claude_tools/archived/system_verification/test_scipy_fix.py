#!/usr/bin/env python
"""测试scipy修复是否成功"""

import sys
print("测试scipy兼容性...")

try:
    # 测试导入路径
    print("1. 测试scipy导入...")
    from scipy.sparse import eye_array
    print("   ✅ scipy.sparse.eye_array导入成功!")
except ImportError as e:
    print(f"   ⚠️ scipy导入失败: {e}")
    # 尝试替代方案
    try:
        from scipy.sparse import eye
        print("   ✅ 使用scipy.sparse.eye替代")
    except:
        print("   ❌ scipy完全不兼容")

try:
    print("\n2. 测试qlib策略模块...")
    from qlib.contrib.strategy import TopkDropoutStrategy
    print("   ✅ qlib策略模块导入成功!")
except Exception as e:
    print(f"   ❌ qlib策略模块导入失败: {e}")

try:
    print("\n3. 测试cvxpy...")
    import cvxpy as cp
    print(f"   ✅ cvxpy导入成功! 版本: {cp.__version__}")
except Exception as e:
    print(f"   ❌ cvxpy导入失败: {e}")

print("\n" + "="*50)
import scipy
print(f"当前scipy版本: {scipy.__version__}")

try:
    import qlib
    print(f"当前qlib版本: {qlib.__version__}")
except:
    print("qlib版本未定义")

print("="*50)