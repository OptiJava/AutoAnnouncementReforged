import threading
from time import sleep

from mcdreforged.api.all import *

from auto_ann.config import Configuration, Announcement

config: Configuration

isAnnounceActive = False


def auto_announcement_thread(server: PluginServerInterface):
    num = 0
    
    while True:
        if isAnnounceActive:
            show_announcement(list(config.announcement_list.keys())[num])
            num += 1
        
        for _ in range(config.interval):
            sleep(1)
            if threading.current_thread().isRunning is False:
                server.logger.warning(f'auto_ann thread: "{threading.current_thread()}" stopped because auto_ann '
                                      f'plugin was unloaded.')
                break


auto_ann_thread: threading.Thread


@new_thread('[auto_ann] create')
def create_announcement(server: PluginServerInterface, name: str, value: str, src: CommandSource):
    if name not in config.announcement_list:
        config.announcement_list[name] = Announcement(value)
        src.reply(RText(f'Add announcement "{name}" successfully.', color=RColor.green))
        server.logger.info(f'[auto_ann] Add announcement "{name}" successfully.')
    else:
        src.reply(RText(f'"{name}" is already in the list!', color=RColor.red))


@new_thread('[auto_ann] delete')
def del_announcement(server: PluginServerInterface, name: str, src: CommandSource):
    if name in config.announcement_list:
        config.announcement_list.pop(name)
        src.reply(RText(f'Delete announcement "{name}" successfully.', color=RColor.green))
        server.logger.info(f'[auto_ann] Delete announcement "{name}" successfully.')
    else:
        src.reply(RText(f'"{name}" is not in the list!', color=RColor.red))


@new_thread('[auto_ann] show')
def show_announcement(server: PluginServerInterface, name: str):
    if name in config.announcement_list:
        if not config.announcement_list.get(name).enabled:
            return
        
        server.tell('@a', config.announcement_list.get(name).content)
        server.logger.info(f'[auto_ann] Successfully showed announcement {name}.')


def set_interval(server: PluginServerInterface, interval: int):
    config.interval = interval
    server.logger.info(f'[auto_ann] Set auto announcement interval to {interval}')


def start_auto_announcement(server: PluginServerInterface, src: CommandSource):
    global isAnnounceActive
    if isAnnounceActive:
        src.reply(RText('Auto announcement has already started.', color=RColor.red))
        return
    
    isAnnounceActive = True
    server.logger.info('Auto announcement started.')
    src.reply(RText('Auto announcement started.', color=RColor.green))


def stop_auto_announcement(server: PluginServerInterface, src: CommandSource):
    global isAnnounceActive
    if isAnnounceActive:
        src.reply(RText('Auto announcement has already stopped.', color=RColor.red))
        return
    
    isAnnounceActive = False
    server.logger.info('Auto announcement stopped.')
    src.reply(RText('Auto announcement stopped.', color=RColor.green))


def enable_announcement(server: PluginServerInterface, name: str, src: CommandSource):
    config.announcement_list.get(name).enabled = True
    src.reply(f'Announcement {config.announcement_list.get(name)} enabled successfully.')
    server.logger.info(f'Announcement {config.announcement_list.get(name)} enabled successfully.')


def disable_announcement(server: PluginServerInterface, name: str, src: CommandSource):
    config.announcement_list.get(name).enabled = False
    src.reply(f'Announcement {config.announcement_list.get(name)} disabled successfully.')
    server.logger.info(f'Announcement {config.announcement_list.get(name)} disabled successfully.')


@new_thread('[auto_ann] save')
def save_config(server: PluginServerInterface, src: CommandSource):
    server.save_config_simple(config)
    src.reply('Config saved!')


def reload_config(server: PluginServerInterface, src: CommandSource):
    server.load_config_simple(target_class=Configuration)
    src.reply('Config reloaded!')


def on_load(server: PluginServerInterface, old_module):
    global config
    
    config = server.load_config_simple(target_class=Configuration)
    
    server.register_command(
        Literal('!!auto_ann')
        .then(
            Literal('create')
            .requires(lambda src: src.has_permission(config.permission['create']))
            .then(
                GreedyText('name')
                .then(
                    GreedyText('content')
                    .runs(lambda src, ctx: create_announcement(server, ctx['name'], ctx['content'], src))
                )
            )
        )
        .then(
            Literal('del')
            .requires(lambda src: src.has_permission(config.permission['del']))
            .then(
                GreedyText('name')
                .runs(lambda src, ctx: del_announcement(server, ctx['name'], src))
            )
        )
        
        .then(
            Literal('show')
            .requires(lambda src: src.has_permission(config.permission['show']))
            .then(
                GreedyText('name')
                .runs(lambda src, ctx: show_announcement(server, ctx['name']))
            )
        )
        
        .then(
            Literal('set_interval')
            .requires(lambda src: src.has_permission(config.permission['set_interval']))
            .then(
                Integer('interval')
                .runs(lambda src, ctx: set_interval(server, ctx['interval']))
            )
        )
        
        .then(
            Literal('start')
            .requires(lambda src: src.has_permissions(config.permission['start']))
            .runs(lambda src: start_auto_announcement(server, src))
        )
        .then(
            Literal('stop')
            .requires(lambda src: src.has_permissions(config.permission['stop']))
            .runs(lambda src: stop_auto_announcement(server, src))
        )
        
        .then(
            Literal('enable')
            .then(
                GreedyText('name')
                .requires(lambda src: src.has_permissions(config.permission['enable']))
                .runs(lambda src, ctx: enable_announcement(server, ctx['name'], src))
            )
        )
        .then(
            Literal('disable')
            .then(
                GreedyText('name')
                .requires(lambda src: src.has_permissions(config.permission['disable']))
                .runs(lambda src, ctx: disable_announcement(server, ctx['name'], src))
            )
        )
        
        .then(Literal('save'))
        .then(Literal('reload'))
    )
    
    global auto_ann_thread
    auto_ann_thread = threading.Thread(target=auto_announcement_thread(server), name='[auto_ann] daemon', daemon=True)
    auto_ann_thread.isRunning = True
    auto_ann_thread.start()


def on_unload(server: PluginServerInterface):
    global auto_ann_thread
    auto_ann_thread.isRunning = False
