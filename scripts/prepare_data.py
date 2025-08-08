#!/usr/bin/env python
"""
RD-Agent ETF数据准备工具
功能：将CSV格式的ETF数据转换为RD-Agent所需的格式
支持：批量处理、数据验证、格式转换
"""

import os
import sys
import argparse
import pandas as pd
import numpy as np
from pathlib import Path
import struct
from datetime import datetime
from tqdm import tqdm
import warnings
warnings.filterwarnings('ignore')

class ETFDataPreparer:
    """ETF数据准备器"""
    
    def __init__(self, input_path, output_dir, verbose=True):
        """
        参数:
            input_path: 输入CSV文件或目录路径
            output_dir: 输出目录路径
            verbose: 是否显示详细信息
        """
        self.input_path = Path(input_path)
        self.output_dir = Path(output_dir)
        self.verbose = verbose
        
        # 创建输出目录
        self.qlib_dir = self.output_dir / "qlib_etf_data_final"
        self.h5_dir = self.output_dir / "qlib_etf_data_h5"
        
        # 数据统计
        self.stats = {
            'total_records': 0,
            'total_etfs': 0,
            'date_range': None,
            'missing_data': {},
            'errors': []
        }
        
    def prepare(self):
        """执行完整的数据准备流程"""
        try:
            self._print_header()
            
            # 1. 读取数据
            self._print_step("1. 读取数据")
            df = self._read_data()
            
            # 2. 验证数据
            self._print_step("2. 验证数据")
            df = self._validate_data(df)
            
            # 3. 数据清洗
            self._print_step("3. 数据清洗")
            df = self._clean_data(df)
            
            # 4. 转换为Qlib格式
            self._print_step("4. 转换为Qlib格式")
            self._convert_to_qlib(df)
            
            # 5. 生成HDF5格式
            self._print_step("5. 生成HDF5格式")
            self._create_hdf5(df)
            
            # 6. 验证结果
            self._print_step("6. 验证结果")
            self._verify_results()
            
            # 7. 生成报告
            self._print_step("7. 生成报告")
            self._generate_report()
            
            self._print_success()
            return True
            
        except Exception as e:
            self._print_error(f"数据准备失败: {str(e)}")
            return False
    
    def _print_header(self):
        """打印头部信息"""
        if self.verbose:
            print("=" * 60)
            print("   RD-Agent ETF数据准备工具")
            print("=" * 60)
            print()
    
    def _print_step(self, message):
        """打印步骤信息"""
        if self.verbose:
            print(f"\n{'='*10} {message} {'='*10}")
    
    def _print_info(self, message):
        """打印信息"""
        if self.verbose:
            print(f"  ℹ️  {message}")
    
    def _print_success(self):
        """打印成功信息"""
        if self.verbose:
            print("\n" + "=" * 60)
            print("✅ 数据准备成功完成！")
            print("=" * 60)
    
    def _print_error(self, message):
        """打印错误信息"""
        print(f"\n❌ 错误: {message}", file=sys.stderr)
    
    def _read_data(self):
        """读取CSV数据"""
        if self.input_path.is_file():
            # 单个文件
            self._print_info(f"读取文件: {self.input_path}")
            df = pd.read_csv(self.input_path)
        else:
            # 目录下所有CSV文件
            csv_files = list(self.input_path.glob("*.csv"))
            if not csv_files:
                raise ValueError(f"未找到CSV文件: {self.input_path}")
            
            self._print_info(f"找到 {len(csv_files)} 个CSV文件")
            
            all_dfs = []
            for csv_file in tqdm(csv_files, desc="读取文件"):
                try:
                    df_temp = pd.read_csv(csv_file)
                    all_dfs.append(df_temp)
                except Exception as e:
                    self.stats['errors'].append(f"读取失败 {csv_file.name}: {str(e)}")
            
            df = pd.concat(all_dfs, ignore_index=True)
        
        # 更新统计
        self.stats['total_records'] = len(df)
        self.stats['total_etfs'] = df['instrument'].nunique() if 'instrument' in df.columns else 0
        
        self._print_info(f"总记录数: {self.stats['total_records']:,}")
        self._print_info(f"ETF数量: {self.stats['total_etfs']}")
        
        return df
    
    def _validate_data(self, df):
        """验证数据格式"""
        # 必需列
        required_columns = ['datetime', 'instrument', 'open', 'high', 'low', 'close', 'volume']
        
        # 检查列名（不区分大小写）
        df.columns = df.columns.str.lower()
        
        # 映射可能的列名变体
        column_mapping = {
            'date': 'datetime',
            'time': 'datetime',
            'symbol': 'instrument',
            'ticker': 'instrument',
            'code': 'instrument',
            'vol': 'volume',
        }
        
        # 重命名列
        df = df.rename(columns=column_mapping)
        
        # 检查必需列
        missing_cols = set(required_columns) - set(df.columns)
        if missing_cols:
            raise ValueError(f"缺少必需列: {missing_cols}")
        
        # 转换数据类型
        df['datetime'] = pd.to_datetime(df['datetime'], errors='coerce')
        
        # 数值列
        numeric_columns = ['open', 'high', 'low', 'close', 'volume']
        for col in numeric_columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # 统计缺失值
        null_counts = df[required_columns].isnull().sum()
        if null_counts.any():
            self.stats['missing_data'] = null_counts[null_counts > 0].to_dict()
            self._print_info(f"发现缺失值: {self.stats['missing_data']}")
        
        # 更新日期范围
        self.stats['date_range'] = (df['datetime'].min(), df['datetime'].max())
        self._print_info(f"日期范围: {self.stats['date_range'][0].date()} 至 {self.stats['date_range'][1].date()}")
        
        return df
    
    def _clean_data(self, df):
        """清洗数据"""
        original_len = len(df)
        
        # 1. 删除完全重复的行
        df = df.drop_duplicates()
        
        # 2. 删除关键列缺失的行
        df = df.dropna(subset=['datetime', 'instrument'])
        
        # 3. 前向填充价格数据
        price_columns = ['open', 'high', 'low', 'close']
        df[price_columns] = df.groupby('instrument')[price_columns].fillna(method='ffill')
        
        # 4. 成交量缺失填0
        df['volume'] = df['volume'].fillna(0)
        
        # 5. 标准化股票代码格式
        df['instrument'] = df['instrument'].str.upper()
        
        # 确保没有.SH/.SZ后缀的股票代码添加后缀
        def add_suffix(code):
            if '.' in code:
                return code
            # 简单规则：6开头为上海，其他为深圳
            if code.startswith('6'):
                return f"{code}.SH"
            else:
                return f"{code}.SZ"
        
        df['instrument'] = df['instrument'].apply(add_suffix)
        
        # 6. 排序
        df = df.sort_values(['instrument', 'datetime'])
        
        cleaned_len = len(df)
        self._print_info(f"清洗前: {original_len:,} 条，清洗后: {cleaned_len:,} 条")
        self._print_info(f"删除了 {original_len - cleaned_len:,} 条无效数据")
        
        return df
    
    def _convert_to_qlib(self, df):
        """转换为Qlib格式"""
        # 创建目录结构
        self.qlib_dir.mkdir(parents=True, exist_ok=True)
        calendars_dir = self.qlib_dir / "calendars"
        features_dir = self.qlib_dir / "features"
        instruments_dir = self.qlib_dir / "instruments"
        
        for dir_path in [calendars_dir, features_dir, instruments_dir]:
            dir_path.mkdir(exist_ok=True)
        
        # 1. 生成日历文件
        self._generate_calendar(df, calendars_dir)
        
        # 2. 生成股票列表
        self._generate_instruments(df, instruments_dir)
        
        # 3. 生成特征文件
        self._generate_features(df, features_dir)
        
        self._print_info(f"Qlib数据已保存到: {self.qlib_dir}")
    
    def _generate_calendar(self, df, calendars_dir):
        """生成日历文件"""
        calendars = sorted(df['datetime'].dt.date.unique())
        calendars_file = calendars_dir / "day.txt"
        
        with open(calendars_file, 'w') as f:
            for date in calendars:
                f.write(f"{date}\n")
        
        self._print_info(f"生成日历: {len(calendars)} 个交易日")
    
    def _generate_instruments(self, df, instruments_dir):
        """生成股票列表文件"""
        instruments_file = instruments_dir / "all.txt"
        
        with open(instruments_file, 'w') as f:
            for instrument in sorted(df['instrument'].unique()):
                inst_df = df[df['instrument'] == instrument]
                start_date = inst_df['datetime'].min().strftime('%Y-%m-%d')
                end_date = inst_df['datetime'].max().strftime('%Y-%m-%d')
                f.write(f"{instrument}\t{start_date}\t{end_date}\n")
        
        self._print_info(f"生成股票列表: {df['instrument'].nunique()} 个ETF")
    
    def _generate_features(self, df, features_dir):
        """生成特征文件"""
        # 获取所有日期
        all_dates = sorted(df['datetime'].dt.date.unique())
        date_index = {date: i for i, date in enumerate(all_dates)}
        
        # 准备特征列
        feature_columns = ['open', 'high', 'low', 'close', 'volume']
        
        # 检查是否有额外的指标列
        extra_columns = [col for col in df.columns 
                        if col not in ['datetime', 'instrument'] + feature_columns]
        if extra_columns:
            self._print_info(f"发现额外指标: {extra_columns}")
            feature_columns.extend(extra_columns)
        
        # 为每个股票生成特征文件
        instruments = sorted(df['instrument'].unique())
        
        for instrument in tqdm(instruments, desc="生成特征文件"):
            inst_df = df[df['instrument'] == instrument].copy()
            inst_df = inst_df.sort_values('datetime')
            
            # 创建股票目录
            inst_dir = features_dir / instrument.lower()
            inst_dir.mkdir(exist_ok=True)
            
            # 为每个特征生成bin文件
            for feature in feature_columns:
                if feature in inst_df.columns:
                    self._save_bin_file(
                        inst_df,
                        feature,
                        inst_dir / f"{feature}.day.bin",
                        all_dates,
                        date_index
                    )
    
    def _save_bin_file(self, inst_df, feature, output_path, all_dates, date_index):
        """保存为Qlib bin格式"""
        # 创建完整的日期序列
        full_data = np.full(len(all_dates), np.nan, dtype=np.float32)
        
        # 填充实际数据
        for _, row in inst_df.iterrows():
            date = row['datetime'].date()
            if date in date_index:
                idx = date_index[date]
                full_data[idx] = row[feature]
        
        # 前向填充
        mask = ~np.isnan(full_data)
        if mask.any():
            first_valid = np.where(mask)[0][0]
            full_data[:first_valid] = full_data[first_valid]
            
            for i in range(1, len(full_data)):
                if np.isnan(full_data[i]):
                    full_data[i] = full_data[i-1]
        
        # 保存为二进制格式
        with open(output_path, 'wb') as f:
            # 写入起始索引（0）
            f.write(struct.pack('<I', 0))
            # 写入数据
            full_data.astype('<f').tofile(f)
    
    def _create_hdf5(self, df):
        """创建HDF5格式文件"""
        self.h5_dir.mkdir(parents=True, exist_ok=True)
        
        # 准备MultiIndex DataFrame
        df_h5 = df.copy()
        df_h5['datetime'] = pd.to_datetime(df_h5['datetime'])
        df_h5 = df_h5.set_index(['datetime', 'instrument'])
        df_h5 = df_h5.sort_index()
        
        # 选择需要的列
        columns_to_save = ['open', 'high', 'low', 'close', 'volume']
        
        # 添加额外的指标列
        extra_columns = [col for col in df_h5.columns if col not in columns_to_save]
        if extra_columns:
            columns_to_save.extend(extra_columns)
            self._print_info(f"HDF5包含指标: {columns_to_save}")
        
        df_h5 = df_h5[columns_to_save]
        
        # 保存为HDF5
        h5_file = self.h5_dir / "daily_pv.h5"
        df_h5.to_hdf(h5_file, key='data', mode='w', complevel=9)
        
        self._print_info(f"生成HDF5文件: {h5_file}")
        self._print_info(f"数据形状: {df_h5.shape}")
    
    def _verify_results(self):
        """验证转换结果"""
        all_good = True
        
        # 检查文件是否存在
        checks = {
            "日历文件": self.qlib_dir / "calendars/day.txt",
            "股票列表": self.qlib_dir / "instruments/all.txt",
            "HDF5数据": self.h5_dir / "daily_pv.h5"
        }
        
        for name, path in checks.items():
            if path.exists():
                self._print_info(f"✅ {name}: {path}")
            else:
                self._print_info(f"❌ {name}: 未找到")
                all_good = False
        
        # 检查特征文件
        features_dir = self.qlib_dir / "features"
        if features_dir.exists():
            etf_dirs = list(features_dir.iterdir())
            if etf_dirs:
                sample_dir = etf_dirs[0]
                bin_files = list(sample_dir.glob("*.bin"))
                self._print_info(f"✅ 特征文件: {len(etf_dirs)} 个ETF, 每个包含 {len(bin_files)} 个特征")
            else:
                self._print_info("❌ 特征文件: 未找到")
                all_good = False
        
        return all_good
    
    def _generate_report(self):
        """生成数据准备报告"""
        report_file = self.output_dir / "data_preparation_report.txt"
        
        with open(report_file, 'w') as f:
            f.write("RD-Agent ETF数据准备报告\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"输入路径: {self.input_path}\n")
            f.write(f"输出路径: {self.output_dir}\n\n")
            
            f.write("数据统计:\n")
            f.write("-" * 40 + "\n")
            f.write(f"总记录数: {self.stats['total_records']:,}\n")
            f.write(f"ETF数量: {self.stats['total_etfs']}\n")
            if self.stats['date_range']:
                f.write(f"日期范围: {self.stats['date_range'][0].date()} 至 {self.stats['date_range'][1].date()}\n")
            
            if self.stats['missing_data']:
                f.write("\n缺失数据:\n")
                for col, count in self.stats['missing_data'].items():
                    f.write(f"  {col}: {count}\n")
            
            if self.stats['errors']:
                f.write("\n错误信息:\n")
                for error in self.stats['errors']:
                    f.write(f"  - {error}\n")
            
            f.write("\n输出文件:\n")
            f.write("-" * 40 + "\n")
            f.write(f"Qlib数据: {self.qlib_dir}\n")
            f.write(f"HDF5数据: {self.h5_dir}\n")
        
        self._print_info(f"报告已保存: {report_file}")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='RD-Agent ETF数据准备工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 处理单个CSV文件
  python prepare_data.py --input etf_data.csv --output ./data
  
  # 处理目录下所有CSV文件
  python prepare_data.py --input ./csv_files --output ./data
  
  # 静默模式
  python prepare_data.py --input data.csv --output ./data --quiet
        """
    )
    
    parser.add_argument('--input', '-i', required=True,
                       help='输入CSV文件或包含CSV文件的目录')
    parser.add_argument('--output', '-o', required=True,
                       help='输出目录路径')
    parser.add_argument('--quiet', '-q', action='store_true',
                       help='静默模式，减少输出信息')
    
    args = parser.parse_args()
    
    # 创建数据准备器
    preparer = ETFDataPreparer(
        input_path=args.input,
        output_dir=args.output,
        verbose=not args.quiet
    )
    
    # 执行准备
    success = preparer.prepare()
    
    # 返回状态码
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()