from vocode.streaming.telephony.config_manager.in_memory_config_manager import (
    InMemoryConfigManager,
)
from vocode.streaming.telephony.config_manager.redis_config_manager import RedisConfigManager

# CONFIG_MANAGER = InMemoryConfigManager()  # RedisConfigManager()
CONFIG_MANAGER = RedisConfigManager()
