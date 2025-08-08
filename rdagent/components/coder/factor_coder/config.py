from pydantic_settings import SettingsConfigDict

from rdagent.components.coder.CoSTEER.config import CoSTEERSettings


class FactorCoSTEERSettings(CoSTEERSettings):
    model_config = SettingsConfigDict(env_prefix="FACTOR_CoSTEER_")

    # 新增代码：配置ETF数据源路径 (原官方数据源已注释保留)
    # data_folder: str = "git_ignore_folder/factor_implementation_source_data"
    data_folder: str = "/Users/handsomedoge/Documents/CITIC_quant/qlib_etf_data_h5"
    """Path to the folder containing ETF financial data in HDF5 format (2015-2025, 中证1000基准) - 通过qlib标准方法从qlib_etf_data_final生成"""

    # data_folder_debug: str = "git_ignore_folder/factor_implementation_source_data_debug"  
    data_folder_debug: str = "/Users/handsomedoge/Documents/CITIC_quant/qlib_etf_data_h5"
    """Path to the folder containing ETF financial data in HDF5 format (for debugging, same as main data)"""

    simple_background: bool = False
    """Whether to use simple background information for code feedback"""

    file_based_execution_timeout: int = 3600
    """Timeout in seconds for each factor implementation execution"""

    select_method: str = "random"
    """Method for the selection of factors implementation"""
    
    # 新增代码：增加因子多样性参数
    temperature: float = 0.9
    """Temperature for LLM generation to increase diversity"""
    
    mutation_rate: float = 0.5
    """Mutation rate for factor evolution"""

    python_bin: str = "python"
    """Path to the Python binary"""


FACTOR_COSTEER_SETTINGS = FactorCoSTEERSettings()
