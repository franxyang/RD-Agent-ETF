#!/usr/bin/env python
"""
RD-Agent 配置管理器
功能：自动生成和管理所有配置文件
支持：交互式配置、批量更新、配置验证
"""

import os
import sys
import yaml
import json
import shutil
from pathlib import Path
from datetime import datetime
import argparse

class ConfigManager:
    """配置管理器"""
    
    def __init__(self, project_root=None):
        """初始化配置管理器"""
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.config = {}
        self.config_files = []
        
        # 配置文件路径映射
        self.config_paths = {
            '.env': self.project_root / '.env',
            'factor_config': self.project_root / 'rdagent/components/coder/factor_coder/config.py',
            'baseline_yaml': self.project_root / 'rdagent/scenarios/qlib/experiment/factor_template/conf_baseline.yaml',
            'combined_yaml': self.project_root / 'rdagent/scenarios/qlib/experiment/factor_template/conf_combined_factors.yaml',
            'sota_yaml': self.project_root / 'rdagent/scenarios/qlib/experiment/factor_template/conf_combined_factors_sota_model.yaml',
            'model_yaml': self.project_root / 'rdagent/scenarios/qlib/experiment/model_template/conf_sota_factors_model.yaml',
        }
        
    def run_interactive(self):
        """运行交互式配置"""
        print("=" * 60)
        print("   RD-Agent 配置管理器")
        print("=" * 60)
        print()
        
        # 1. 收集配置信息
        self._collect_api_config()
        self._collect_data_config()
        self._collect_market_config()
        self._collect_performance_config()
        
        # 2. 生成配置文件
        self._generate_all_configs()
        
        # 3. 验证配置
        self._validate_configs()
        
        # 4. 生成总结
        self._print_summary()
        
    def load_existing_config(self):
        """加载现有配置"""
        if self.config_paths['.env'].exists():
            self._load_env_config()
            return True
        return False
    
    def update_config(self, updates):
        """更新配置"""
        self.config.update(updates)
        self._generate_all_configs()
    
    def _collect_api_config(self):
        """收集API配置"""
        print("\n📋 API配置")
        print("-" * 40)
        
        # OpenAI配置
        api_key = input("OpenAI API密钥 [必填]: ").strip()
        while not api_key or api_key == "your_api_key_here":
            print("⚠️  API密钥不能为空")
            api_key = input("OpenAI API密钥 [必填]: ").strip()
        
        api_base = input("API基础URL [https://api.openai.com/v1]: ").strip()
        if not api_base:
            api_base = "https://api.openai.com/v1"
        
        model = input("聊天模型 [gpt-4o]: ").strip()
        if not model:
            model = "gpt-4o"
        
        self.config['api'] = {
            'OPENAI_API_KEY': api_key,
            'OPENAI_API_BASE': api_base,
            'CHAT_MODEL': model,
            'EMBEDDING_MODEL': 'text-embedding-3-small',
            'REASONING_THINK_RM': 'True'
        }
        
    def _collect_data_config(self):
        """收集数据配置"""
        print("\n📊 数据路径配置")
        print("-" * 40)
        
        # 默认路径
        default_qlib = str(self.project_root / "data/qlib_etf_data_final")
        default_h5 = str(self.project_root / "data/qlib_etf_data_h5")
        
        print(f"默认Qlib路径: {default_qlib}")
        qlib_path = input("Qlib数据路径 [使用默认]: ").strip()
        if not qlib_path:
            qlib_path = default_qlib
        
        print(f"默认HDF5路径: {default_h5}")
        h5_path = input("HDF5数据路径 [使用默认]: ").strip()
        if not h5_path:
            h5_path = default_h5
        
        self.config['data'] = {
            'qlib_path': qlib_path,
            'h5_path': h5_path
        }
        
    def _collect_market_config(self):
        """收集市场配置"""
        print("\n📈 市场配置")
        print("-" * 40)
        
        market = input("市场范围 [all]: ").strip() or "all"
        benchmark = input("基准指数 [000852.csi]: ").strip() or "000852.csi"
        
        print("\n时间范围设置:")
        train_start = input("训练开始日期 [2015-01-01]: ").strip() or "2015-01-01"
        train_end = input("训练结束日期 [2020-12-31]: ").strip() or "2020-12-31"
        valid_start = input("验证开始日期 [2021-01-01]: ").strip() or "2021-01-01"
        valid_end = input("验证结束日期 [2022-12-31]: ").strip() or "2022-12-31"
        test_start = input("测试开始日期 [2023-01-01]: ").strip() or "2023-01-01"
        test_end = input("测试结束日期 [2025-07-10]: ").strip() or "2025-07-10"
        
        self.config['market'] = {
            'market': market,
            'benchmark': benchmark,
            'train_start': train_start,
            'train_end': train_end,
            'valid_start': valid_start,
            'valid_end': valid_end,
            'test_start': test_start,
            'test_end': test_end
        }
        
    def _collect_performance_config(self):
        """收集性能配置"""
        print("\n⚡ 性能配置")
        print("-" * 40)
        
        workers = input("并行工作线程数 [4]: ").strip() or "4"
        timeout = input("执行超时时间(秒) [3600]: ").strip() or "3600"
        cache = input("启用缓存 [yes/no, 默认yes]: ").strip().lower()
        cache = "true" if cache != "no" else "false"
        
        self.config['performance'] = {
            'MAX_WORKERS': workers,
            'TIMEOUT': timeout,
            'CACHE_ENABLED': cache
        }
        
    def _generate_all_configs(self):
        """生成所有配置文件"""
        print("\n⚙️  生成配置文件...")
        
        # 备份现有配置
        self._backup_existing_configs()
        
        # 生成各个配置文件
        self._generate_env_file()
        self._update_python_config()
        self._update_yaml_configs()
        
        print("✅ 所有配置文件已生成")
        
    def _backup_existing_configs(self):
        """备份现有配置文件"""
        backup_dir = self.project_root / "config_backup" / datetime.now().strftime("%Y%m%d_%H%M%S")
        
        for name, path in self.config_paths.items():
            if path.exists():
                backup_dir.mkdir(parents=True, exist_ok=True)
                backup_path = backup_dir / path.name
                shutil.copy2(path, backup_path)
                
    def _generate_env_file(self):
        """生成.env文件"""
        env_content = f"""# RD-Agent 配置文件
# 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

# ==================== API配置 ====================
OPENAI_API_KEY={self.config['api']['OPENAI_API_KEY']}
OPENAI_API_BASE={self.config['api']['OPENAI_API_BASE']}
CHAT_MODEL={self.config['api']['CHAT_MODEL']}
EMBEDDING_MODEL={self.config['api']['EMBEDDING_MODEL']}
REASONING_THINK_RM={self.config['api'].get('REASONING_THINK_RM', 'True')}

# ==================== 数据路径 ====================
QLIB_DATA_PATH={self.config['data']['qlib_path']}
HDF5_DATA_PATH={self.config['data']['h5_path']}

# ==================== 市场配置 ====================
MARKET={self.config['market']['market']}
BENCHMARK={self.config['market']['benchmark']}
TRAIN_START={self.config['market']['train_start']}
TRAIN_END={self.config['market']['train_end']}
VALID_START={self.config['market']['valid_start']}
VALID_END={self.config['market']['valid_end']}
TEST_START={self.config['market']['test_start']}
TEST_END={self.config['market']['test_end']}

# ==================== 性能配置 ====================
MAX_WORKERS={self.config['performance']['MAX_WORKERS']}
TIMEOUT={self.config['performance']['TIMEOUT']}
CACHE_ENABLED={self.config['performance']['CACHE_ENABLED']}

# ==================== 其他配置 ====================
DS_LOCAL_DATA_PATH="./git_ignore_folder/kaggle_data"
DS_IF_USING_MLE_DATA=True
"""
        
        with open(self.config_paths['.env'], 'w', encoding='utf-8') as f:
            f.write(env_content)
        
        self.config_files.append('.env')
        print("  ✅ 生成 .env")
        
    def _update_python_config(self):
        """更新Python配置文件"""
        config_file = self.config_paths['factor_config']
        
        if not config_file.exists():
            print(f"  ⚠️  {config_file} 不存在，跳过")
            return
        
        # 读取文件
        with open(config_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # 更新数据路径
        updated = False
        for i, line in enumerate(lines):
            if 'data_folder:' in line and 'str =' in line:
                if 'git_ignore_folder' in line or '/Users/' in line:
                    lines[i] = f'    data_folder: str = "{self.config["data"]["h5_path"]}"\n'
                    updated = True
            elif 'data_folder_debug:' in line and 'str =' in line:
                if 'git_ignore_folder' in line or '/Users/' in line:
                    lines[i] = f'    data_folder_debug: str = "{self.config["data"]["h5_path"]}"\n'
                    updated = True
        
        if updated:
            # 写回文件
            with open(config_file, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            self.config_files.append('factor_config.py')
            print("  ✅ 更新 factor_config.py")
        else:
            print("  ⚠️  factor_config.py 无需更新")
    
    def _update_yaml_configs(self):
        """更新YAML配置文件"""
        yaml_files = [
            'baseline_yaml',
            'combined_yaml',
            'sota_yaml'
        ]
        
        for yaml_key in yaml_files:
            yaml_path = self.config_paths[yaml_key]
            if yaml_path.exists():
                self._update_single_yaml(yaml_path)
            else:
                print(f"  ⚠️  {yaml_path.name} 不存在，跳过")
    
    def _update_single_yaml(self, yaml_path):
        """更新单个YAML文件"""
        try:
            with open(yaml_path, 'r', encoding='utf-8') as f:
                content = f.read()
                config = yaml.safe_load(content)
            
            # 保存原始内容用于对比
            original_content = content
            
            # 更新qlib_init
            if 'qlib_init' in config:
                config['qlib_init']['provider_uri'] = self.config['data']['qlib_path']
                config['qlib_init']['region'] = 'cn'
            
            # 更新市场和基准（使用YAML锚点）
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if line.startswith('market:') and '&market' in line:
                    lines[i] = f"market: &market {self.config['market']['market']}"
                elif line.startswith('benchmark:') and '&benchmark' in line:
                    lines[i] = f"benchmark: &benchmark {self.config['market']['benchmark']}"
            
            # 更新时间范围
            if 'data_handler_config' in config:
                config['data_handler_config']['start_time'] = self.config['market']['train_start']
                config['data_handler_config']['end_time'] = self.config['market']['test_end']
                config['data_handler_config']['fit_start_time'] = self.config['market']['train_start']
                config['data_handler_config']['fit_end_time'] = self.config['market']['train_end']
            
            # 更新segments
            if 'task' in config and 'dataset' in config['task']:
                if 'segments' in config['task']['dataset']['kwargs']:
                    config['task']['dataset']['kwargs']['segments'] = {
                        'train': [self.config['market']['train_start'], self.config['market']['train_end']],
                        'valid': [self.config['market']['valid_start'], self.config['market']['valid_end']],
                        'test': [self.config['market']['test_start'], self.config['market']['test_end']]
                    }
            
            # 写回文件
            with open(yaml_path, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
            
            self.config_files.append(yaml_path.name)
            print(f"  ✅ 更新 {yaml_path.name}")
            
        except Exception as e:
            print(f"  ❌ 更新 {yaml_path.name} 失败: {str(e)}")
    
    def _validate_configs(self):
        """验证配置"""
        print("\n🔍 验证配置...")
        
        errors = []
        warnings = []
        
        # 验证API密钥
        if self.config['api']['OPENAI_API_KEY'] == 'your_api_key_here':
            errors.append("API密钥未设置")
        
        # 验证数据路径
        qlib_path = Path(self.config['data']['qlib_path'])
        h5_path = Path(self.config['data']['h5_path'])
        
        if not qlib_path.exists():
            warnings.append(f"Qlib数据目录不存在: {qlib_path}")
        if not h5_path.exists():
            warnings.append(f"HDF5数据目录不存在: {h5_path}")
        
        # 验证日期格式
        try:
            from datetime import datetime
            datetime.strptime(self.config['market']['train_start'], '%Y-%m-%d')
            datetime.strptime(self.config['market']['test_end'], '%Y-%m-%d')
        except ValueError:
            errors.append("日期格式错误，应为YYYY-MM-DD")
        
        # 打印验证结果
        if errors:
            print("❌ 发现错误:")
            for error in errors:
                print(f"  - {error}")
        
        if warnings:
            print("⚠️  警告:")
            for warning in warnings:
                print(f"  - {warning}")
        
        if not errors and not warnings:
            print("✅ 配置验证通过")
        
        return len(errors) == 0
    
    def _print_summary(self):
        """打印配置总结"""
        print("\n" + "=" * 60)
        print("配置总结")
        print("=" * 60)
        
        print("\n已生成/更新的配置文件:")
        for file in self.config_files:
            print(f"  ✅ {file}")
        
        print("\n关键配置:")
        print(f"  📊 数据路径: {self.config['data']['qlib_path']}")
        print(f"  📈 市场范围: {self.config['market']['market']}")
        print(f"  📅 回测期间: {self.config['market']['test_start']} ~ {self.config['market']['test_end']}")
        print(f"  ⚡ 并行线程: {self.config['performance']['MAX_WORKERS']}")
        
        print("\n下一步操作:")
        print("1. 准备数据: python scripts/prepare_data.py")
        print("2. 运行健康检查: rdagent health_check")
        print("3. 开始因子挖掘: rdagent fin_factor --loop_n 1")
        
    def export_config(self, output_file):
        """导出配置到文件"""
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
        print(f"✅ 配置已导出到: {output_file}")
    
    def import_config(self, input_file):
        """从文件导入配置"""
        with open(input_file, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        self._generate_all_configs()
        print(f"✅ 配置已从 {input_file} 导入")
    
    def _load_env_config(self):
        """从.env文件加载配置"""
        env_path = self.config_paths['.env']
        if not env_path.exists():
            return
        
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    # 解析到相应的配置组
                    if 'API' in key:
                        if 'api' not in self.config:
                            self.config['api'] = {}
                        self.config['api'][key] = value
                    elif 'PATH' in key:
                        if 'data' not in self.config:
                            self.config['data'] = {}
                        if 'QLIB' in key:
                            self.config['data']['qlib_path'] = value
                        elif 'HDF5' in key:
                            self.config['data']['h5_path'] = value

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='RD-Agent 配置管理器',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 交互式配置
  python config_manager.py
  
  # 导出配置
  python config_manager.py --export config.json
  
  # 导入配置
  python config_manager.py --import config.json
  
  # 更新特定配置
  python config_manager.py --update-api-key sk-xxx
        """
    )
    
    parser.add_argument('--export', help='导出配置到文件')
    parser.add_argument('--import', dest='import_file', help='从文件导入配置')
    parser.add_argument('--update-api-key', help='更新API密钥')
    parser.add_argument('--project-root', help='项目根目录', default='.')
    
    args = parser.parse_args()
    
    # 创建配置管理器
    manager = ConfigManager(args.project_root)
    
    if args.import_file:
        # 导入配置
        manager.import_config(args.import_file)
    elif args.export:
        # 导出配置
        if manager.load_existing_config():
            manager.export_config(args.export)
        else:
            print("❌ 未找到现有配置，请先运行交互式配置")
    elif args.update_api_key:
        # 更新API密钥
        if manager.load_existing_config():
            manager.config['api']['OPENAI_API_KEY'] = args.update_api_key
            manager._generate_all_configs()
            print(f"✅ API密钥已更新")
        else:
            print("❌ 未找到现有配置")
    else:
        # 交互式配置
        manager.run_interactive()

if __name__ == "__main__":
    main()