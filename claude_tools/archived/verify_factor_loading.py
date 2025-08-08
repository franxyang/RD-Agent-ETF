#!/usr/bin/env python3
"""
验证自定义因子是否被正确加载到qlib中
根据专家建议的三步验证流程
"""
import yaml
import pandas as pd
import numpy as np
import qlib
from qlib.utils import init_instance_by_config
import sys
import os

def verify_factor_loading(config_file="conf_combined_factors.yaml"):
    """
    验证因子是否被正确加载
    
    Returns:
        bool: 验证是否成功
    """
    print("🔍 开始验证因子加载情况...")
    print("=" * 60)
    
    try:
        # 1. 初始化qlib
        print("\n1️⃣ 初始化Qlib...")
        qlib.init(
            provider_uri="/Users/handsomedoge/Documents/CITIC_quant/qlib_etf_data_final",
            region="cn"
        )
        print("   ✅ Qlib初始化成功")
        
        # 2. 加载配置文件
        print(f"\n2️⃣ 加载配置文件：{config_file}")
        config_path = f"/opt/anaconda3/envs/rdagent/lib/python3.10/site-packages/rdagent/scenarios/qlib/experiment/factor_template/{config_file}"
        
        with open(config_path, 'r') as f:
            cfg = yaml.safe_load(f)
        
        # 3. 获取handler配置
        handler_cfg = cfg["task"]["dataset"]["kwargs"]["handler"]
        print(f"   Handler类型：{handler_cfg['class']}")
        
        # 4. 初始化handler
        print("\n3️⃣ 初始化Handler并加载数据...")
        dh = init_instance_by_config(handler_cfg)
        
        # 5. 获取特征数据
        print("\n4️⃣ 获取特征数据...")
        df_feat = dh.fetch(col_set="feature", data_key=dh.DK_I)
        
        # 6. 打印验证结果
        print("\n" + "=" * 60)
        print("📊 验证结果：")
        print("=" * 60)
        
        num_features = len(df_feat.columns)
        print(f"✅ 特征总数：{num_features}")
        
        if num_features > 158:
            print(f"✅ 成功！特征数 ({num_features}) > 158")
            print("   说明自定义因子已被加载")
            
            # 显示前10个特征名
            print(f"\n📋 前10个特征：")
            for i, col in enumerate(df_feat.columns[:10]):
                print(f"   {i+1:2}. {col}")
            
            # 显示后5个特征（应该包含自定义因子）
            print(f"\n📋 后5个特征（可能包含自定义因子）：")
            for i, col in enumerate(df_feat.columns[-5:]):
                print(f"   {num_features-4+i:3}. {col}")
                
            # 检查是否有Momentum相关的特征
            momentum_features = [col for col in df_feat.columns if 'Momentum' in str(col)]
            if momentum_features:
                print(f"\n🎯 找到自定义Momentum因子：")
                for feat in momentum_features:
                    print(f"   - {feat}")
            
            # 计算简单的IC验证
            print("\n5️⃣ 计算IC分布（抽样验证）...")
            try:
                # 获取label数据
                df_label = dh.fetch(col_set="label", data_key=dh.DK_L)
                
                # 计算每个特征与label的相关性（抽样前100个时间点）
                sample_dates = df_feat.index.get_level_values(0).unique()[:100]
                correlations = []
                
                for date in sample_dates[:10]:  # 只算前10个日期作为示例
                    try:
                        feat_day = df_feat.loc[date]
                        label_day = df_label.loc[date]
                        if len(feat_day) > 0 and len(label_day) > 0:
                            corr = feat_day.corrwith(label_day.iloc[:, 0])
                            correlations.append(corr)
                    except:
                        pass
                
                if correlations:
                    ic_df = pd.DataFrame(correlations)
                    ic_mean = ic_df.mean()
                    ic_std = ic_df.std()
                    
                    print(f"\n📈 IC统计（前10个交易日）：")
                    print(f"   平均IC范围：{ic_mean.min():.6f} ~ {ic_mean.max():.6f}")
                    print(f"   IC标准差范围：{ic_std.min():.6f} ~ {ic_std.max():.6f}")
                    
                    # 检查IC是否有差异
                    if ic_mean.std() > 0.0001:
                        print(f"   ✅ IC值有差异，说明不同特征表现不同")
                    else:
                        print(f"   ⚠️ IC值差异很小，可能仍有问题")
            except Exception as e:
                print(f"   ⚠️ IC计算失败：{e}")
            
            return True
        else:
            print(f"❌ 失败！特征数 ({num_features}) <= 158")
            print("   自定义因子可能没有被加载")
            print("\n🔧 可能的原因：")
            print("   1. combined_factors_df.pkl文件不存在或路径错误")
            print("   2. 配置文件中StaticDataLoader配置错误")
            print("   3. pkl文件格式有问题")
            return False
            
    except Exception as e:
        print(f"\n❌ 验证失败：{e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # 支持命令行参数指定配置文件
    config = sys.argv[1] if len(sys.argv) > 1 else "conf_combined_factors.yaml"
    
    success = verify_factor_loading(config)
    
    if success:
        print("\n" + "=" * 60)
        print("🎉 验证成功！自定义因子已被正确加载")
        print("下一步：运行rdagent fin_factor验证IC值不再相同")
    else:
        print("\n" + "=" * 60)
        print("⚠️ 验证失败，请检查配置和文件")