import threading
from time import sleep

from mcdreforged.api.all import *

from auto_ann.config import Configuration, Announcement

config: Configuration


class AnnouncerThread(threading.Thread):
    server_inst: PluginServerInterface
    
    def __init__(self, server: PluginServerInterface):
        super().__init__(name='[auto_ann] - daemon', daemon=True)
        self.server_inst = server
        self.stop_event = threading.Event()
    
    def break_thread(self):
        self.stop_event.set()
    
    def run(self):
        global config
        num = 0
        
        while True:
            if config.is_auto_announcer_active and self.server_inst.is_server_running():
                key_list = list(config.announcement_list.keys())
                
                try:
                    while not config.announcement_list.get(key_list[num]).enabled:
                        if len(key_list) - 1 > num:
                            num += 1
                        elif len(key_list) - 1 == num:
                            num = 0
                    
                    if len(key_list) - 1 > num:
                        show_announcement(self.server_inst, key_list[num])
                        num += 1
                    elif len(key_list) - 1 == num:
                        show_announcement(self.server_inst, key_list[num])
                        num = 0
                except IndexError:
                    continue
            
            for _ in range(config.interval):
                sleep(1.0)
                if self.stop_event.is_set() is True:
                    self.server_inst.logger.warning(f'auto_ann thread: {threading.current_thread().name} stopped '
                                                    f'because auto_ann plugin was unloaded.')
                    break


daemon_thread: AnnouncerThread


@new_thread('[auto_ann] - create')
def create_announcement(server: PluginServerInterface, name: str, src: CommandSource, value: str = ''):
    global config
    if name not in config.announcement_list:
        config.announcement_list[name] = Announcement(content=value)
        src.reply(RTextMCDRTranslation('auto_ann.create.success', name, color=RColor.green))
        server.logger.info(f'Add announcement {name} successfully.')
    else:
        src.reply(
            RTextMCDRTranslation('auto_ann.create.already_in_list', name, color=RColor.red))


@new_thread('[auto_ann] - delete')
def del_announcement(server: PluginServerInterface, name: str, src: CommandSource):
    global config
    if name in config.announcement_list:
        config.announcement_list.pop(name)
        src.reply(RTextMCDRTranslation('auto_ann.delete.success', name, color=RColor.green))
        server.logger.info(f'Delete announcement {name} successfully.')
    else:
        src.reply(RTextMCDRTranslation('auto_ann.delete.not_exist', name, color=RColor.red))


@new_thread('[auto_ann] - show')
def show_announcement(server: PluginServerInterface, name: str):
    global config
    if name in config.announcement_list:
        server.tell('@a', config.announcement_list.get(name).content)
        server.logger.info(f'Successfully showed announcement {name}.')


def set_interval(server: PluginServerInterface, interval: int, src: CommandSource):
    global config
    config.interval = interval
    server.logger.info(f'Set auto announcement interval to {interval}')
    src.reply(RTextMCDRTranslation('auto_ann.config.set_interval', interval, color=RColor.green))


def start_auto_announcement(server: PluginServerInterface, src: CommandSource):
    global config
    if config.is_auto_announcer_active:
        src.reply(RTextMCDRTranslation('auto_ann.auto_announcer.already_started', color=RColor.red))
        return
    
    config.is_auto_announcer_active = True
    server.logger.info('Auto announcement started.')
    src.reply(RTextMCDRTranslation('auto_ann.auto_announcer.start', color=RColor.green))


def stop_auto_announcement(server: PluginServerInterface, src: CommandSource):
    global config
    if not config.is_auto_announcer_active:
        src.reply(RTextMCDRTranslation('auto_ann.auto_announcer.already_stopped', color=RColor.red))
        return
    
    config.is_auto_announcer_active = False
    server.logger.info('Auto announcement stopped.')
    src.reply(RTextMCDRTranslation('auto_ann.auto_announcer.stop', color=RColor.green))


def enable_announcement(server: PluginServerInterface, name: str, src: CommandSource):
    global config
    if name in config.announcement_list:
        config.announcement_list.get(name).enabled = True
        src.reply(
            RTextMCDRTranslation('auto_ann.auto_announcer.enable', name,
                                 color=RColor.green))
        server.logger.info(f'Announcement {name} enabled successfully.')
    else:
        src.reply(RTextMCDRTranslation('auto_ann.auto_announcer.enable_or_disable_failed', name, color=RColor.red))


def disable_announcement(server: PluginServerInterface, name: str, src: CommandSource):
    global config
    if name in config.announcement_list:
        config.announcement_list.get(name).enabled = False
        src.reply(
            RTextMCDRTranslation('auto_ann.auto_announcer.disable', name,
                                 color=RColor.green))
        server.logger.info(f'Announcement {name} disabled successfully.')
    else:
        src.reply(RTextMCDRTranslation('auto_ann.auto_announcer.enable_or_disable_failed', name, color=RColor.red))


def save_config(server: PluginServerInterface, src: CommandSource):
    server.save_config_simple(config)
    src.reply(RTextMCDRTranslation('auto_ann.config.save', color=RColor.green))


def reload_config(server: PluginServerInterface, src: CommandSource):
    global config
    config = server.load_config_simple(target_class=Configuration)
    src.reply(RTextMCDRTranslation('auto_ann.config.reload', color=RColor.green))


def on_load(server: PluginServerInterface, old_module):
    global config
    
    config = server.load_config_simple(target_class=Configuration)
    
    server.register_command(
        Literal('!!auto_ann')
        .then(
            Literal('create')
            .then(
                Text('name')
                .requires(lambda src: src.has_permission(config.permission['create']))
                .on_error(CommandError,
                          lambda src, err: src.reply(
                              RTextMCDRTranslation('auto_ann.command.on_error', err, color=RColor.red)),
                          handled=True)
                .runs(lambda src, ctx: create_announcement(server, ctx['name'], src))
                .then(
                    Literal('content')
                    .then(
                        GreedyText('content')
                        .requires(lambda src: src.has_permission(config.permission['create']))
                        .on_error(CommandError,
                                  lambda src, err: src.reply(
                                      RTextMCDRTranslation('auto_ann.command.on_error', err, color=RColor.red)),
                                  handled=True)
                        .runs(lambda src, ctx: create_announcement(server, ctx['name'], src, value=ctx['content']))
                    )
                )
            )
        )
        .then(
            Literal('del')
            .then(
                Text('name')
                .requires(lambda src: src.has_permission(config.permission['del']))
                .on_error(CommandError,
                          lambda src, err: src.reply(
                              RTextMCDRTranslation('auto_ann.command.on_error', err, color=RColor.red)),
                          handled=True)
                .runs(lambda src, ctx: del_announcement(server, ctx['name'], src))
            )
        )
        
        .then(
            Literal('show')
            .then(
                Text('name')
                .requires(lambda src: src.has_permission(config.permission['show']))
                .on_error(CommandError,
                          lambda src, err: src.reply(
                              RTextMCDRTranslation('auto_ann.command.on_error', err, color=RColor.red)),
                          handled=True)
                .runs(lambda src, ctx: show_announcement(server, ctx['name']))
            )
        )
        
        .then(
            Literal('set_interval')
            .then(
                Integer('interval')
                .requires(lambda src: src.has_permission(config.permission['set_interval']))
                .on_error(CommandError,
                          lambda src, err: src.reply(
                              RTextMCDRTranslation('auto_ann.command.on_error', err, color=RColor.red)),
                          handled=True)
                .runs(lambda src, ctx: set_interval(server, ctx['interval'], src))
            )
        )
        
        .then(
            Literal('start')
            .requires(lambda src: src.has_permission(config.permission['start']))
            .on_error(CommandError,
                      lambda src, err: src.reply(
                          RTextMCDRTranslation('auto_ann.command.on_error', err, color=RColor.red)),
                      handled=True)
            .runs(lambda src: start_auto_announcement(server, src))
        )
        .then(
            Literal('stop')
            .requires(lambda src: src.has_permission(config.permission['stop']))
            .on_error(CommandError,
                      lambda src, err: src.reply(
                          RTextMCDRTranslation('auto_ann.command.on_error', err, color=RColor.red)),
                      handled=True)
            .runs(lambda src: stop_auto_announcement(server, src))
        )
        
        .then(
            Literal('enable')
            .then(
                Text('name')
                .requires(lambda src: src.has_permission(config.permission['enable']))
                .on_error(CommandError,
                          lambda src, err: src.reply(
                              RTextMCDRTranslation('auto_ann.command.on_error', err, color=RColor.red)),
                          handled=True)
                .runs(lambda src, ctx: enable_announcement(server, ctx['name'], src))
            )
        )
        .then(
            Literal('disable')
            .then(
                Text('name')
                .requires(lambda src: src.has_permission(config.permission['disable']))
                .on_error(CommandError,
                          lambda src, err: src.reply(
                              RTextMCDRTranslation('auto_ann.command.on_error', err, color=RColor.red)),
                          handled=True)
                .runs(lambda src, ctx: disable_announcement(server, ctx['name'], src))
            )
        )
        
        .then(
            Literal('save')
            .requires(lambda src: src.has_permission(config.permission['save']))
            .on_error(CommandError,
                      lambda src, err: src.reply(
                          RTextMCDRTranslation('auto_ann.command.on_error', err, color=RColor.red)),
                      handled=True)
            .runs(lambda src: save_config(server, src))
        )
        .then(
            Literal('reload')
            .requires(lambda src: src.has_permission(config.permission['reload']))
            .on_error(CommandError,
                      lambda src, err: src.reply(
                          RTextMCDRTranslation('auto_ann.command.on_error', err, color=RColor.red)),
                      handled=True)
            .runs(lambda src: reload_config(server, src))
        )
    )


def on_server_startup(server: PluginServerInterface):
    global daemon_thread
    daemon_thread = AnnouncerThread(server)
    daemon_thread.start()


def on_unload(server: PluginServerInterface):
    global daemon_thread
    daemon_thread.break_thread()
