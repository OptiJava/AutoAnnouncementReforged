# AutoAnnouncementReforged

> Send announcements to members of your server more conveniently and easily in game.

## Usage

### Command

`!!auto_ann`:

- Print help message.

`!!auto_ann create <name>`:

- Create an default announcement.
- Default (template) announcement can be change in config file
- `<name>` is an identifier of your announcement(must without blank).

`!!auto_ann create <name> content <content>`:

- Create a new announcement(use template announcement configuration). The announcements will be saved in the config file.
- `<name>` is an identifier of your announcement.
- `<content>` is the content of the announcement.

`!!auto_ann del <name>`

- Delete an announcement

`!!auto_ann show <name>`

- Manually show an announcement to everyone

`!!auto_ann start`

- Start auto_announcer

`!!auto_ann stop`

- Stop auto_announcer

`!!auto_ann set_interval <interval>`

- Set auto announce interval (unit is second)
- For example, if there are announcements A, B and C, the interval is 120s, the effect is: play A, wait 120s, play B,
  wait 120s, play C, wait 120s, then play A again, wait 120s......
- This will be saved into config file, too.

`!!auto_ann enable <name>`

- Enable an announcement, auto_announcer will just show announcements which is enabled.

`!!auto_ann disable <name>`

- Disable an announcement, auto_announcer will not show announcement to players which is disabled.

`!!auto_ann save`

- Manually save all configurations to config file.
- The plugin will auto save config when server stopped

`!!auto_ann reload`

- Use this command when you changed the config file.

`!!auto_ann list`

- List all announcements.

`!!auto_ann modify <name> <content>`
- Modify announcement content

### Configuration

```
 {
    # default announcement config (announcement template)
    "default_announcement_configuration": {
        "content": "",
        "enabled": true
    },
    
    # is auto announcer active
    "is_auto_announcer_active": false,
    
    # announcement prefix, example: '[Announcement]'
    "prefix": "",
    
    # announcement dict, usually you needn't edit this
    "announcement_list": {},
    
    # auto announcer interval, unit seconds
    "interval": 120,
    
    # command permission
    "permission": {
        "create": 3,
        "del": 3,
        "show": 3,
        "stop": 3,
        "start": 3,
        "enable": 3,
        "disable": 3,
        "set_interval": 3,
        "save": 3,
        "reload": 3,
        "list": 1,
        "rename": 3,
        "set_prefix": 3,
        "modify": 3
    }
}
```