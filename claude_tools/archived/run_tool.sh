#!/bin/bash
# Claude Tools 快速启动脚本

echo "========================================="
echo "     Claude Tools - RD-Agent工具集      "
echo "========================================="
echo ""
echo "请选择要运行的工具："
echo ""
echo "【系统验证】"
echo "  1) 快速系统检查 (quick_test.py)"
echo "  2) scipy兼容性测试 (test_scipy_fix.py)"
echo "  3) 配置修复验证 (verify_fix.py)"
echo "  4) qlib数据验证 (test_qlib_data.py)"
echo ""
echo "【数据转换】"
echo "  5) 转换qlib数据到HDF5 (simple_convert_to_h5.py)"
echo ""
echo "【分析报告】"
echo "  6) 分析运行结果 (analyze_run.py)"
echo ""
echo "【查看文档】"
echo "  7) 查看评估报告"
echo "  8) 查看优化报告"
echo ""
echo "  0) 退出"
echo ""
read -p "请输入选项 (0-8): " choice

case $choice in
    1)
        echo "运行快速系统检查..."
        python system_verification/quick_test.py
        ;;
    2)
        echo "运行scipy兼容性测试..."
        source /opt/anaconda3/bin/activate rdagent4qlib
        python system_verification/test_scipy_fix.py
        ;;
    3)
        echo "运行配置修复验证..."
        python system_verification/verify_fix.py
        ;;
    4)
        echo "运行qlib数据验证..."
        python system_verification/test_qlib_data.py
        ;;
    5)
        echo "转换qlib数据到HDF5..."
        python data_conversion/simple_convert_to_h5.py
        ;;
    6)
        echo "分析运行结果..."
        python analysis_reports/analyze_run.py
        ;;
    7)
        echo "打开评估报告..."
        cat docs/evaluation_report.md
        ;;
    8)
        echo "打开优化报告..."
        cat docs/optimization_report.md
        ;;
    0)
        echo "退出工具集"
        exit 0
        ;;
    *)
        echo "无效选项，请重新运行脚本"
        ;;
esac

echo ""
echo "========================================="
echo "工具执行完成！"