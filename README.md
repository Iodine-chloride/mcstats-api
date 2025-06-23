# mcstats-API
获取玩家统计数据生成排行榜,并且生成一个API以供调用

## 使用

### 下载

从[Release页面](https://github.com/Iodine-chloride/mcstats-api/releases)下载stats.pyz文件

将.pyz文件放入服务器根目录,例如

    ├── logs

    ├── mods

    ├── versions

    ├── worlds              //世界文件夹

    │   ├──stats            //统计信息文件夹

    │   ├──data             //计分板信息存储位置

    │   └── ...

    ├── stats.pyz           //程序本体

    ├── usercache.json      //服务器玩家名——UUID对应表缓存

    ├── rank_config.json    //程序配置文件

    └── ...

### 安装依赖

    pip install flask nbtlib

### 运行

在服务器根目录执行

    python stats.pyz

程序默认运行端口：5000

指定端口运行 参数-port

    python stats.pyz -port 1145

## API

### 玩家统计数据榜单

程序默认内置了以下榜单

    play_time, mined, damage_taken, killed, aviate_cm, deaths, fish_caught, built, traded

    游玩时长（单位：小时）,挖掘榜,受伤榜（单位：heart）,击杀榜,鞘翅飞行距离（单位：km）,死亡榜,钓鱼榜,建筑榜,交易榜

也可以[自定义榜单](##自定义榜单)

输出所有榜单前十（包括内置榜单与自定义榜单）

    GET /api/rank/all HTTP/1.1

输出特定榜单前十（包括内置榜单与自定义榜单） 

例：挖掘榜

    GET /api/rank/mined HTTP/1.1

### 获取单独玩家统计数据

输出指定玩家/UUID的榜单项目 

例1：输出Steve的所有榜单项目（包括内置榜单与自定义榜单）

    GET /api/player/Steve HTTP/1.1

例2：输出UUID为8667ba71-b85a-4004-af54-457a9734eed7的玩家的所有榜单项目（包括内置榜单与自定义榜单）

    GET /api/player/8667ba71-b85a-4004-af54-457a9734eed7 HTTP/1.1

### 获取指定玩家所有计分板数据

例：输出Steve的所有计分板数据

    GET /api/scoreboard/player/Steve HTTP/1.1

### 获取某项积分数据的前十名

例：输出名为"spring_move"的计分板项前十名

    GET /api/scoreboard/leaderboard/spring_move HTTP/1.1

## 自定义榜单

在程序目录下新建rank_config.json文件用于编写自定义榜单,格式如下

    {

        "custom_ranks": [

          {

            "name": "rank1",               //榜单名称,即调用时输入的名称

            "label": "自定义榜单1",         //榜单标签,相当于注释

            "field": "custom",             //榜单类型,可选类型有custom, mined, broken, dropped, killed, killed_by, picked_up,

                                           //used, crafted

            "items": [

                ...

            ]                              //统计的项目

          },

          {

            "name": "rank2",

            "label": "自定义榜单2",

            "field": "custom",

            "items": [

                ...

                ]

          }

        ]

    }


field为custom时,items的空间命名对照ID可见[MinecraftWiki](https://zh.minecraft.wiki/w/%E7%BB%9F%E8%AE%A1%E4%BF%A1%E6%81%AF)

field为非custom时,items的空间命名对照ID可见[MinecraftWiki](https://zh.minecraft.wiki/w/%E5%91%BD%E5%90%8D%E7%A9%BA%E9%97%B4ID)

可选标签

"mode",仅当field为非custom时生效,默认值为"white_list",可选"all"和"black_list",效果为字面意思

"unit",仅当field为custom且包含特定项目时生效,默认值为"default",输出原始数据

当包含伤害项目时可选单位为"heart"和"half-heart"（若为default,则单位为1/10half-heart或1/20heart）

当包含距离项目时可选单位为"m"和"km"（若为default,则单位为cm）

当包含时间项目时可选单位为"s","min","h","day"和"game-day"（若为default，则单位为gt或game-tick）
