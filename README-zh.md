# AutoAnnouncementReforged

中文 | [English](https://github.com/OptiJava/AutoAnnouncementReforged/blob/master/README.md)

> 更加简单、方便地在服务器中发布公告~

## 用法

### 指令

`!!auto_ann`:

- 打印帮助信息&公告列表

`!!auto_ann create <name>`:

- 创建一个以`公告模板`为默认值的公告
- 默认公告模板可以在配置文件中进行配置
- `<name>`是你的公告的唯一识别符（不可带有空格）

`!!auto_ann create <name> content <content>`:

- 创建一个以`公告模板`为默认值的公告
- `<name>`是你的公告的唯一识别符（不可带有空格）
- `<content>` 是公告内容

`!!auto_ann del <name>`

- 删除一个公告

`!!auto_ann show <name>`

- 手动向所有人发布公告

`!!auto_ann start`

- 启用自动公告

`!!auto_ann stop`

- 禁用自动公告

`!!auto_ann set_interval <interval>`

- 设置自动公告的间隔
- 例如：有公告A、B、C，间隔为120s，则效果为：播放A，等待120s，播放B，等待120s，播放C，等待120s，再播放A，等待120s......
- 这会被保存到配置文件

`!!auto_ann enable <name>`

- 启用一个公告，被启用的公告会被自动公告，被禁用的公告可以手动进行公告

`!!auto_ann disable <name>`

- 禁用一个公告, 被启用的公告会被自动公告，被禁用的公告可以手动进行公告

`!!auto_ann save`

- 手动保存配置文件
- 插件会在服务器关闭时自动保存配置文件

`!!auto_ann reload`

- 重载配置文件

`!!auto_ann list`

- 展示所有公告及其内容

`!!auto_ann modify <name> <content>`
- 编辑公告内容

`!!auto_ann set_prefix <prefix>`
- 更改公告前缀（%name会被替换为公告名字）

`!!auto_ann rename <p_name> <u_name>`
- 更改公告名字

### 配置

**这是默认的配置文件**
```
 {
    # 默认的新创建的公告（公告模板）
    "default_announcement_configuration": {
        "content": "",
        "enabled": true
    },
    
    # 是否启用自动公告
    "is_auto_announcer_active": false,
    
    # 自动公告前缀，例如：[公告]（%name会被替换成公告名字）
    "prefix": "[%name]",
    
    # 公告内容列表（轮播）
    "announcement_list": {},
    
    # 轮播间隔
    # 例如：有公告A、B、C，间隔为120s，则效果为：播放A，等待120s，播放B，等待120s，播放C，等待120s，再播放A，等待120s......
    "interval": 120,
    
    # 指令最低权限要求
    "permission": {
        # 创建新的公告
        "create": 3,
        
        # 删除一个公告
        "del": 3,
        
        # 向所有成员展示一个公告
        "show": 3,
        
        # 停止自动公告轮播
        "stop": 3,
        
        # 启动自动公告轮播
        "start": 3,
        
        # 启用一个公告
        "enable": 3,
        
        # 禁用一个公告
        "disable": 3,
        
        # 修改公告轮播间隔
        "set_interval": 3,
        
        # 将目前的配置保存到磁盘配置文件中
        "save": 3,
        
        # 重载配置文件
        "reload": 3,
        
        # 显示公告列表
        "list": 1,
        
        # 重命名
        "rename": 3,
        
        # 设置公告前缀
        "set_prefix": 3,
        
        # 修改公告内容
        "modify": 3
    }
}
```