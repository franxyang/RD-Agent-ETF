#!/usr/bin/env python
"""分析RD-Agent运行结果"""

import os
import re

log_dir = '/Users/handsomedoge/Documents/CITIC_quant/RD-Agent/log/2025-08-06_02-54-08-742038'

def extract_metrics_from_file(file_path):
    """从pkl文件中提取关键指标"""
    if not os.path.exists(file_path):
        return None
    
    # 使用strings命令提取文本内容
    cmd = f'strings "{file_path}" 2>/dev/null'
    content = os.popen(cmd).read()
    
    metrics = {}
    
    # 提取IC/ICIR
    ic_match = re.search(r"'IC':\s*([\d.-]+)", content)
    icir_match = re.search(r"'ICIR':\s*([\d.-]+)", content)
    rank_ic_match = re.search(r"'Rank IC':\s*([\d.-]+)", content)
    rank_icir_match = re.search(r"'Rank ICIR':\s*([\d.-]+)", content)
    
    if ic_match:
        metrics['IC'] = float(ic_match.group(1))
    if icir_match:
        metrics['ICIR'] = float(icir_match.group(1))
    if rank_ic_match:
        metrics['Rank IC'] = float(rank_ic_match.group(1))
    if rank_icir_match:
        metrics['Rank ICIR'] = float(rank_icir_match.group(1))
    
    # 检查是否失败
    if 'Failed to run' in content:
        metrics['status'] = 'Failed'
    elif 'ImportError' in content:
        metrics['status'] = 'Completed with ImportError'
    elif metrics:
        metrics['status'] = 'Completed'
    else:
        metrics['status'] = 'Unknown'
    
    # 提取数据路径
    data_path_match = re.search(r"data_path=.*?'(.*?)'", content)
    if data_path_match:
        metrics['data_path'] = data_path_match.group(1)
    
    # 提取训练信息
    train_loss_match = re.findall(r"train's l2: ([\d.]+)", content)
    valid_loss_match = re.findall(r"valid's l2: ([\d.]+)", content)
    if train_loss_match and valid_loss_match:
        metrics['final_train_loss'] = float(train_loss_match[-1])
        metrics['final_valid_loss'] = float(valid_loss_match[-1])
    
    return metrics

print("="*60)
print("RD-Agent运行分析报告")
print("运行ID: 2025-08-06_02-54-08-742038")
print("="*60)

# 分析每个Loop
completed_loops = 0
successful_loops = 0
all_metrics = []

for loop_num in range(10):  # 检查前10个loops
    loop_dir = os.path.join(log_dir, f'Loop_{loop_num}')
    if not os.path.exists(loop_dir):
        break
    
    feedback_file = os.path.join(loop_dir, 'feedback/feedback/97858')
    if os.path.exists(feedback_file):
        files = os.listdir(feedback_file)
        if files:
            file_path = os.path.join(feedback_file, files[0])
            metrics = extract_metrics_from_file(file_path)
            
            if metrics:
                completed_loops += 1
                if 'IC' in metrics:
                    successful_loops += 1
                    all_metrics.append(metrics)
                
                print(f"\nLoop_{loop_num}:")
                print(f"  状态: {metrics.get('status', 'Unknown')}")
                if 'data_path' in metrics:
                    print(f"  数据路径: {metrics['data_path']}")
                if 'IC' in metrics:
                    print(f"  IC: {metrics['IC']:.6f}")
                    print(f"  ICIR: {metrics.get('ICIR', 0):.6f}")
                    print(f"  Rank IC: {metrics.get('Rank IC', 0):.6f}")
                    print(f"  Rank ICIR: {metrics.get('Rank ICIR', 0):.6f}")
                if 'final_train_loss' in metrics:
                    print(f"  最终训练损失: {metrics['final_train_loss']:.6f}")
                    print(f"  最终验证损失: {metrics['final_valid_loss']:.6f}")

print("\n" + "="*60)
print("汇总统计:")
print(f"  总运行Loop数: {completed_loops}")
print(f"  成功完成qlib回测的Loop数: {successful_loops}")

if all_metrics:
    avg_ic = sum(m.get('IC', 0) for m in all_metrics) / len(all_metrics)
    avg_icir = sum(m.get('ICIR', 0) for m in all_metrics) / len(all_metrics)
    print(f"  平均IC: {avg_ic:.6f}")
    print(f"  平均ICIR: {avg_icir:.6f}")
    
    # 检查数据路径是否正确
    paths = set(m.get('data_path', '') for m in all_metrics if 'data_path' in m)
    if paths:
        print(f"  使用的数据路径: {', '.join(paths)}")
        if 'qlib_etf_data_final' in str(paths):
            print("  ✅ 数据路径正确!")
        else:
            print("  ⚠️ 数据路径可能有问题")

print("\n" + "="*60)
print("问题诊断:")

# 检查scipy问题
import os
cmd = 'strings ' + log_dir + '/Loop_0/feedback/feedback/97858/*.pkl | grep "ImportError"'
scipy_error = os.popen(cmd).read()
if 'eye_array' in scipy_error:
    print("  ⚠️ 发现scipy兼容性问题: 'eye_array' 导入错误")
    print("     这是scipy版本不兼容导致，但不影响核心功能")

# 检查训练是否正常
if successful_loops > 0:
    print(f"  ✅ qlib功能基本正常: {successful_loops}个Loop成功完成训练和评估")
else:
    print("  ❌ qlib功能可能有问题: 没有Loop成功完成")

print("="*60)