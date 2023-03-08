import threading
from time import sleep

from mcdreforged.api.all import *

from auto_ann_r.config import Configuration, Announcement

config: Configuration


class AnnouncerThread(threading.Thread):
    server_inst: PluginServerInterface
    
    def __init__(self, server: PluginServerInterface):
        super().__init__(name='auto_ann_r - daemon', daemon=True)
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
            
            tmp_interval = config.interval
            
            for _ in range(tmp_interval):
                sleep(1.0)
                if tmp_interval != config.interval:
                    break
                
                if self.stop_event.is_set() is True:
                    self.server_inst.logger.info(
                        'auto_ann_r daemon thread stopped because auto_ann_r plugin was unloaded.')
                    break


daemon_thread: AnnouncerThread


@new_thread('auto_ann_r - create')
def create_announcement(server: PluginServerInterface, name: str, src: CommandSource, value: str = ''):
    global config
    if name not in config.announcement_list:
        config.announcement_list[name] = Announcement(content=value)
        src.reply(RTextMCDRTranslation('auto_ann_r.create.success', name))
        server.logger.info(f'Add announcement {name} successfully.')
    else:
        src.reply(
            RTextMCDRTranslation('auto_ann_r.create.already_in_list', name))


@new_thread('auto_ann_r - delete')
def del_announcement(server: PluginServerInterface, name: str, src: CommandSource):
    global config
    if name in config.announcement_list:
        config.announcement_list.pop(name)
        src.reply(RTextMCDRTranslation('auto_ann_r.delete.success', name))
        server.logger.info(f'Delete announcement {name} successfully.')
    else:
        src.reply(RTextMCDRTranslation('auto_ann_r.delete.not_exist', name))


@new_thread('auto_ann_r - show')
def show_announcement(server: PluginServerInterface, name: str):
    global config
    if name in config.announcement_list:
        prefix_t = config.prefix
        
        prefix_t = prefix_t.replace('%name', name)
        
        server.tell('@a', RTextList(
            RText(prefix_t)
            .h(f'{name}'),
            RText(' '),
            RText(config.announcement_list.get(name).content)
        ))
        server.logger.info(f'Successfully showed announcement {name}.')


def set_interval(server: PluginServerInterface, interval: int, src: CommandSource):
    global config
    config.interval = interval
    server.logger.info(f'Set auto announcement interval to {interval}')
    src.reply(RTextMCDRTranslation('auto_ann_r.config.set_interval', interval))


def start_auto_announcement(server: PluginServerInterface, src: CommandSource):
    global config
    if config.is_auto_announcer_active:
        src.reply(RTextMCDRTranslation('auto_ann_r.auto_announcer.already_started'))
        return
    
    config.is_auto_announcer_active = True
    server.logger.info('Auto announcement started.')
    src.reply(RTextMCDRTranslation('auto_ann_r.auto_announcer.start'))


def stop_auto_announcement(server: PluginServerInterface, src: CommandSource):
    global config
    if not config.is_auto_announcer_active:
        src.reply(RTextMCDRTranslation('auto_ann_r.auto_announcer.already_stopped'))
        return
    
    config.is_auto_announcer_active = False
    server.logger.info('Auto announcement stopped.')
    src.reply(RTextMCDRTranslation('auto_ann_r.auto_announcer.stop'))


def enable_announcement(server: PluginServerInterface, name: str, src: CommandSource):
    global config
    if name in config.announcement_list:
        config.announcement_list.get(name).enabled = True
        src.reply(
            RTextMCDRTranslation('auto_ann_r.auto_announcer.enable', name))
        server.logger.info(f'Announcement {name} enabled successfully.')
    else:
        src.reply(RTextMCDRTranslation('auto_ann_r.auto_announcer.enable_or_disable_failed', name))


def disable_announcement(server: PluginServerInterface, name: str, src: CommandSource):
    global config
    if name in config.announcement_list:
        config.announcement_list.get(name).enabled = False
        src.reply(
            RTextMCDRTranslation('auto_ann_r.auto_announcer.disable', name))
        server.logger.info(f'Announcement {name} disabled successfully.')
    else:
        src.reply(RTextMCDRTranslation('auto_ann_r.auto_announcer.enable_or_disable_failed', name))


@new_thread('auto_ann_r - save')
def save_config(server: PluginServerInterface, src: CommandSource):
    server.save_config_simple(config)
    src.reply(RTextMCDRTranslation('auto_ann_r.config.save'))


@new_thread('auto_ann_r - reload')
def reload_config(server: PluginServerInterface, src: CommandSource):
    global config
    config = server.load_config_simple(target_class=Configuration)
    src.reply(RTextMCDRTranslation('auto_ann_r.config.reload'))


@new_thread('auto_ann_r - list')
def list_announcements(server: PluginServerInterface, src: CommandSource):
    global config
    key_list = list(config.announcement_list.keys())
    
    src.reply(RTextMCDRTranslation('auto_ann_r.list.header'))
    if len(key_list) == 0:
        src.reply(RTextList(
            RText('  '),
            RTextMCDRTranslation('auto_ann_r.list.empty')
        ))
        return
    
    for name in key_list:
        if not config.announcement_list.get(name).enabled:
            src.reply(RTextList(
                RText('  '),
                RText('[▷]', color=RColor.green)
                .c(RAction.suggest_command, f'!!auto_ann_r show {name}')
                .h(server.tr('auto_ann_r.list.click_to_show')),
                RText('[x]', color=RColor.red)
                .c(RAction.suggest_command, f'!!auto_ann_r del {name}')
                .h(server.tr('auto_ann_r.list.click_to_del')),
                RText('[e]', color=RColor.green)
                .h(server.tr('auto_ann_r.list.click_to_enable'))
                .c(RAction.suggest_command, f'!!auto_ann_r enable {name}'),
                RText(' '),
                RTextMCDRTranslation('auto_ann_r.list.announcement', name, config.announcement_list.get(name).content)
            ))
        else:
            src.reply(RTextList(
                RText('  '),
                RText('[▷]', color=RColor.green)
                .c(RAction.suggest_command, f'!!auto_ann_r show {name}')
                .h(server.tr('auto_ann_r.list.click_to_show')),
                RText('[x]', color=RColor.red)
                .c(RAction.suggest_command, f'!!auto_ann_r del {name}')
                .h(server.tr('auto_ann_r.list.click_to_del')),
                RText('[d]', color=RColor.red)
                .h(server.tr('auto_ann_r.list.click_to_disable'))
                .c(RAction.suggest_command, f'!!auto_ann_r disable {name}'),
                RText(' '),
                RTextMCDRTranslation('auto_ann_r.list.announcement', name, config.announcement_list.get(name).content)
            ))


@new_thread('auto_ann_r - help')
def print_help_message(server: PluginServerInterface, src: CommandSource):
    global config
    src.reply(RTextMCDRTranslation('auto_ann_r.help_msg.msg', server.get_self_metadata().version))
    src.reply('')
    src.reply(RTextMCDRTranslation('auto_ann_r.help_msg.announcer', config.is_auto_announcer_active))
    src.reply('')
    list_announcements(server, src)


@new_thread('auto_ann_r - rename')
def rename_announcement(server: PluginServerInterface, p_name: str, u_name: str, src: CommandSource):
    global config
    
    if p_name not in config.announcement_list:
        src.reply(RTextMCDRTranslation('auto_ann_r.rename.not_exist'))
        return
    
    content = config.announcement_list.get(p_name)
    
    config.announcement_list.pop(p_name)
    config.announcement_list[u_name] = content
    src.reply(RTextMCDRTranslation('auto_ann_r.rename.success', p_name, u_name))
    server.logger.info(f'Successfully renamed announcement {p_name} to {u_name}')


def set_prefix(server: PluginServerInterface, prefix: str, src: CommandSource):
    global config
    config.prefix = prefix
    src.reply(RTextMCDRTranslation("auto_ann_r.config.set_prefix", prefix))
    server.logger.info(f'Set prefix to {prefix}')


def on_load(server: PluginServerInterface, old_module):
    global config
    
    config = server.load_config_simple(target_class=Configuration)
    
    oe = 'auto_ann_r.command.on_error'
    server.register_command(
        Literal('!!auto_ann')
        .runs(lambda src: print_help_message(server, src))
        .then(
            Literal('create')
            .then(
                Text('name')
                .requires(lambda src: src.has_permission(config.permission['create']))
                .on_error(CommandError,
                          lambda src, err: src.reply(
                              RTextMCDRTranslation(oe, err)),
                          handled=True)
                .runs(lambda src, ctx: create_announcement(server, ctx['name'], src))
                .then(
                    Literal('content')
                    .then(
                        GreedyText('content')
                        .requires(lambda src: src.has_permission(config.permission['create']))
                        .on_error(CommandError,
                                  lambda src, err: src.reply(
                                      RTextMCDRTranslation(oe, err)),
                                  handled=True)
                        .runs(lambda src, ctx: create_announcement(server, ctx['name'], src,
                                                                   value=ctx['content']))
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
                              RTextMCDRTranslation(oe, err)),
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
                              RTextMCDRTranslation(oe, err)),
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
                              RTextMCDRTranslation(oe, err)),
                          handled=True)
                .runs(lambda src, ctx: set_interval(server, ctx['interval'], src))
            )
        )
        
        .then(
            Literal('start')
            .requires(lambda src: src.has_permission(config.permission['start']))
            .on_error(CommandError,
                      lambda src, err: src.reply(
                          RTextMCDRTranslation(oe, err)),
                      handled=True)
            .runs(lambda src: start_auto_announcement(server, src))
        )
        .then(
            Literal('stop')
            .requires(lambda src: src.has_permission(config.permission['stop']))
            .on_error(CommandError,
                      lambda src, err: src.reply(
                          RTextMCDRTranslation(oe, err)),
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
                              RTextMCDRTranslation(oe, err)),
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
                              RTextMCDRTranslation(oe, err)),
                          handled=True)
                .runs(lambda src, ctx: disable_announcement(server, ctx['name'], src))
            )
        )
        
        .then(
            Literal('save')
            .requires(lambda src: src.has_permission(config.permission['save']))
            .on_error(CommandError,
                      lambda src, err: src.reply(
                          RTextMCDRTranslation(oe, err)),
                      handled=True)
            .runs(lambda src: save_config(server, src))
        )
        .then(
            Literal('reload')
            .requires(lambda src: src.has_permission(config.permission['reload']))
            .on_error(CommandError,
                      lambda src, err: src.reply(
                          RTextMCDRTranslation(oe, err)),
                      handled=True)
            .runs(lambda src: reload_config(server, src))
        )
        .then(
            Literal('list')
            .requires(lambda src: src.has_permission(config.permission['list']))
            .on_error(CommandError,
                      lambda src, err: src.reply(
                          RTextMCDRTranslation(oe, err)),
                      handled=True)
            .runs(lambda src: list_announcements(server, src))
        )
        .then(
            Literal('rename')
            .then(
                Text('p_name')
                .then(
                    Text('u_name')
                    .requires(lambda src: src.has_permission(config.permission['rename']))
                    .on_error(CommandError,
                              lambda src, err: src.reply(
                                  RTextMCDRTranslation(oe, err)),
                              handled=True)
                    .runs(lambda src, ctx: rename_announcement(server, ctx['p_name'], ctx['u_name'], src))
                )
            )
        )
        .then(
            Literal('set_prefix')
            .then(
                GreedyText('prefix')
                .requires(lambda src: src.has_permission(config.permission['set_prefix']))
                .on_error(CommandError, lambda src, err: src.reply(
                    RTextMCDRTranslation(oe, err)),
                          handled=True)
                .runs(lambda src, ctx: set_prefix(server, ctx['prefix'], src))
            )
        )
    )


def on_server_startup(server: PluginServerInterface):
    global daemon_thread
    daemon_thread = AnnouncerThread(server)
    daemon_thread.start()


def on_server_stop(server: PluginServerInterface, return_code: int):
    save_config(server, server.get_plugin_command_source())


def on_unload(server: PluginServerInterface):
    try:
        global daemon_thread
        daemon_thread.break_thread()
    except NameError:
        pass
