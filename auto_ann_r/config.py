from typing import Dict

from mcdreforged.utils.serializer import Serializable


class Announcement(Serializable):
    # 公告内容
    content: str = ''
    
    # 是否启用
    # 若禁用，则公告不会被自动轮播，但仍可以通过`!!auto_ann show xxx`指令展示此公告
    enabled: bool = True


class Configuration(Serializable):
    # 默认的新创建的公告
    default_announcement_configuration: Announcement = Announcement()
    
    # 是否启用自动公告
    is_auto_announcer_active: bool = False
    
    # 自动公告前缀，例如：[公告]
    prefix: str = ''
    
    # 公告内容列表（轮播）
    announcement_list: Dict[str, Announcement] = {}
    
    # 轮播间隔
    # 例如：有公告A、B、C，间隔为120s，则效果为：播放A，等待120s，播放B，等待120s，播放C，等待120s，再播放A，等待120s......
    interval: int = 120  # 单位为秒
    
    # 指令最低权限要求
    permission: Dict[str, int] = {
        # 创建新的公告
        'create': 3,
        
        # 删除一个公告
        'del': 3,
        
        # 向所有成员展示一个公告
        'show': 3,
        
        # 停止自动公告轮播
        'stop': 3,
        
        # 启动自动公告轮播
        'start': 3,
        
        # 启用一个公告
        'enable': 3,
        
        # 禁用一个公告
        'disable': 3,
        
        # 修改公告轮播间隔
        'set_interval': 3,
        
        # 将目前的配置保存到磁盘配置文件中
        'save': 3,
        
        # 重载配置文件
        'reload': 3,
        
        # 显示公告列表
        'list': 1,
        
        # 重命名
        'rename': 3,
        
        # 设置公告前缀
        'set_prefix': 3,
        
        # 修改内容
        'modify': 3
    }
