"""
StepWright - A powerful web scraping library built with Playwright

A declarative, step-by-step approach to web automation and data extraction.
"""

__version__ = "2.0.0"
__author__ = "Muhammad Umer Farooq"
__email__ = "umer@lablnet.com"

# Import main API
from .parser import (
    run_scraper,
    run_scraper_with_callback,
    run_scraper_with_metrics,
    load_template,
    save_template,
    template_to_json,
    template_from_json,
)

# Import validator functions
from .validator import validate_template_format, validate_template_data

# Import types
from .step_types import (
    BaseStep,
    NextButtonConfig,
    ScrollConfig,
    PaginationConfig,
    TabTemplate,
    ParallelTemplate,
    ParameterizedTemplate,
    RunOptions,
    SelectorType,
    DataType,
    EngineType,
    ProxyConfig,
    ValidationError,
    ValidationResult,
    StepMetric,
    ExecutionMetrics,
    parse_template_from_dict,
)

# Import proxy pool
from .proxy_pool import ProxyPool, ProxyEntry, ProxyStatus

# Import stealth handlers
from .handlers import apply_stealth_scripts, check_and_handle_captcha

# Import helpers (for advanced usage)
from .helpers import (
    replace_index_placeholders,
    replace_data_placeholders,
    locator_for,
    flatten_nested_foreach_results,
)

# Import executor functions (for advanced usage)
from .executor import (
    execute_step,
    execute_step_list,
    execute_tab,
)

# Import Driver Architecture
from .drivers import BaseDriver, PlaywrightDriver, get_driver

# Import Storage Adapters Architecture
from .adapters import (
    BaseStorageAdapter,
    JSONFileAdapter,
    CSVFileAdapter,
    XMLFileAdapter,
    SQLiteAdapter,
    PostgreSQLAdapter,
    MySQLAdapter,
    MongoDBAdapter,
    DynamoDBAdapter,
    ElasticsearchAdapter,
    S3StorageAdapter,
    GCSStorageAdapter,
    AzureBlobAdapter,
    RabbitMQAdapter,
    KafkaAdapter,
    get_adapter,
    register_adapter,
)

# Import low-level scraper functions (for advanced usage)
from .scraper import (
    get_browser,
    get_device_preset,
    navigate,
    elem,
    input,
    click,
    double_click,
    click_check_box,
    get_data,
    _shutdown_playwright,
)

__all__ = [
    # Version
    "__version__",
    # Main API
    "run_scraper",
    "run_scraper_with_callback",
    "run_scraper_with_metrics",
    "load_template",
    "save_template",
    "template_to_json",
    "template_from_json",
    "parse_template_from_dict",
    # Validation
    "validate_template_format",
    "validate_template_data",
    # Drivers
    "BaseDriver",
    "PlaywrightDriver",
    "get_driver",
    # Storage Adapters
    "BaseStorageAdapter",
    "JSONFileAdapter",
    "CSVFileAdapter",
    "XMLFileAdapter",
    "SQLiteAdapter",
    "PostgreSQLAdapter",
    "MySQLAdapter",
    "MongoDBAdapter",
    "DynamoDBAdapter",
    "ElasticsearchAdapter",
    "S3StorageAdapter",
    "GCSStorageAdapter",
    "AzureBlobAdapter",
    "RabbitMQAdapter",
    "KafkaAdapter",
    "get_adapter",
    "register_adapter",
    # Types
    "BaseStep",
    "NextButtonConfig",
    "ScrollConfig",
    "PaginationConfig",
    "TabTemplate",
    "ParallelTemplate",
    "ParameterizedTemplate",
    "RunOptions",
    "SelectorType",
    "DataType",
    "EngineType",
    "ProxyConfig",
    "ValidationError",
    "ValidationResult",
    "StepMetric",
    "ExecutionMetrics",
    # Proxy Pool
    "ProxyPool",
    "ProxyEntry",
    "ProxyStatus",
    # Stealth
    "apply_stealth_scripts",
    "check_and_handle_captcha",
    # Helpers",
    "replace_index_placeholders",
    "replace_data_placeholders",
    "locator_for",
    "flatten_nested_foreach_results",
    # Executor
    "execute_step",
    "execute_step_list",
    "execute_tab",
    # Low-level scraper
    "get_browser",
    "get_device_preset",
    "navigate",
    "elem",
    "input",
    "click",
    "double_click",
    "click_check_box",
    "get_data",
    "_shutdown_playwright",
]
