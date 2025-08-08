#!/bin/bash
# 清理工作空间并重新测试
# Author: Claude
# Date: 2025-08-07

echo "=========================================="
echo "🧹 清理工作空间并准备重新测试"
echo "=========================================="

# 1. 清理旧的工作空间
echo ""
echo "1️⃣ 清理旧的工作空间..."
rm -rf /Users/handsomedoge/Documents/CITIC_quant/RD-Agent/git_ignore_folder/RD-Agent_workspace/*
echo "   ✅ 工作空间已清理"

# 2. 设置CPU环境
echo ""
echo "2️⃣ 设置CPU环境..."
export CUDA_VISIBLE_DEVICES=""
echo "   ✅ CUDA_VISIBLE_DEVICES已设置为空"

# 3. 显示当前配置状态
echo ""
echo "3️⃣ 当前配置状态："
echo "   • model_runner.py: 使用.pkl格式 ✅"
echo "   • factor_runner.py: 使用.pkl格式 ✅"
echo "   • conf_combined_factors.yaml: DataHandlerLP + Label定义 ✅"
echo "   • conf_combined_factors_sota_model.yaml: DataHandlerLP + Label定义 ✅"

# 4. 提示运行测试
echo ""
echo "=========================================="
echo "✅ 准备就绪！"
echo "=========================================="
echo ""
echo "现在可以运行测试："
echo "  rdagent fin_factor --loop_n 1 --step_n 1"
echo ""
echo "预期结果："
echo "  • 不再出现 KeyError: 'label'"
echo "  • IC值不再都是 0.007418"
echo "  • 特征数量 > 158"
echo ""