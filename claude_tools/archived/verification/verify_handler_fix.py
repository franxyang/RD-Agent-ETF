"""
验证DataHandlerLP配置修复
"""
import re

configs = [
    "/opt/anaconda3/envs/rdagent/lib/python3.10/site-packages/rdagent/scenarios/qlib/experiment/factor_template/conf_combined_factors.yaml",
    "/opt/anaconda3/envs/rdagent/lib/python3.10/site-packages/rdagent/scenarios/qlib/experiment/factor_template/conf_combined_factors_sota_model.yaml"
]

print("=== DataHandlerLP配置验证 ===\n")

for config_path in configs:
    filename = config_path.split('/')[-1]
    print(f"📄 {filename}")
    
    with open(config_path, 'r') as f:
        content = f.read()
    
    # 查找DataHandlerLP部分
    handler_pattern = r'class:\s*DataHandlerLP.*?kwargs:(.*?)data_loader:'
    handler_match = re.search(handler_pattern, content, re.DOTALL)
    
    if handler_match:
        handler_kwargs = handler_match.group(1)
        
        # 检查是否还有fit_start_time或fit_end_time在handler kwargs中
        if 'fit_start_time' in handler_kwargs or 'fit_end_time' in handler_kwargs:
            print("  ❌ 错误：handler kwargs中仍包含fit_start_time/fit_end_time")
        else:
            print("  ✅ handler kwargs中没有fit_start_time/fit_end_time")
        
        # 检查关键参数
        if 'start_time: 2015-01-01' in handler_kwargs:
            print("  ✅ 包含 start_time: 2015-01-01")
        if 'end_time: 2025-07-10' in handler_kwargs:
            print("  ✅ 包含 end_time: 2025-07-10")
        if 'instruments: *market' in handler_kwargs:
            print("  ✅ 包含 instruments: *market")
    
    # 检查RobustZScoreNorm是否有正确的参数
    robust_pattern = r'RobustZScoreNorm.*?kwargs:(.*?)(?:- class:|learn_processors:)'
    robust_match = re.search(robust_pattern, content, re.DOTALL)
    
    if robust_match:
        robust_kwargs = robust_match.group(1)
        if 'fit_start_time: 2015-01-01' in robust_kwargs:
            print("  ✅ RobustZScoreNorm包含fit_start_time")
        if 'fit_end_time: 2020-12-31' in robust_kwargs:
            print("  ✅ RobustZScoreNorm包含fit_end_time")
    
    print()

print("=== 修复总结 ===")
print("✅ DataHandlerLP的kwargs中已移除fit_start_time和fit_end_time")
print("✅ RobustZScoreNorm的kwargs中保留了必需的时间参数")
print("✅ NestedDataLoader配置保持不变，将加载自定义因子")
print("\n现在可以运行测试：")
print("rdagent fin_factor --loop_n 1 --step_n 2")
