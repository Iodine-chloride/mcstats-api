import os
import json
from pathlib import Path

DEFAULT_RANK_FIELDS = [
    "play_time",
    "mined",
    "damage_taken",
    "killed",
    "aviate_cm",
    "deaths",
    "fish_caught",
    "built",
    "traded"
]

STAT_CATEGORY_MAP = {
    "mined": "minecraft:mined",
    "broken": "minecraft:broken",
    "dropped": "minecraft:dropped",
    "killed": "minecraft:killed",
    "killed_by": "minecraft:killed_by",
    "picked_up": "minecraft:picked_up",
    "used": "minecraft:used",
    "crafted": "minecraft:crafted"
}

class StatsRank:
    def __init__(self, stats_dir="./world/stats", 
                 usercache_path="./usercache.json", 
                 rank_config_path="./rank_config.json"):
        self.STATS_DIR = Path(stats_dir)
        self.USERCACHE = Path(usercache_path)
        self.RANK_CONFIG_PATH = Path(rank_config_path)
        
        self.STATS_DIR.mkdir(parents=True, exist_ok=True)
        self.USERCACHE.parent.mkdir(parents=True, exist_ok=True)
        self.RANK_CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    def load_usercache(self):
        if not self.USERCACHE.exists():
            return {}
        with self.USERCACHE.open("r", encoding="utf-8") as f:
            cache = json.load(f)
        return {item["uuid"]: item["name"] for item in cache}
    
    def load_rank_config(self):
        if not self.RANK_CONFIG_PATH.exists():
            return {"custom_ranks": []}
        with self.RANK_CONFIG_PATH.open("r", encoding="utf-8") as f:
            return json.load(f)
    
    def load_player_stats(self, uuid):
        filepath = self.STATS_DIR / f"{uuid}.json"
        if not filepath.exists():
            return {}
        try:
            with filepath.open("r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading {filepath}: {e}")
            return {}
    
    def get_stat_values(self, stats):
        custom = stats.get("stats", {}).get("minecraft:custom", {})
        
        return (
            custom.get("minecraft:play_time", 0),
            sum(stats.get("stats", {}).get("minecraft:mined", {}).values()),
            custom.get("minecraft:damage_taken", 0),
            sum(stats.get("stats", {}).get("minecraft:killed", {}).values()),
            custom.get("minecraft:aviate_one_cm", 0),
            custom.get("minecraft:deaths", 0),
            custom.get("minecraft:fish_caught", 0),
            sum(stats.get("stats", {}).get("minecraft:used", {}).values()),
            custom.get("minecraft:traded_with_villager", 0)
        )
    
    def get_custom_rank_data(self, stats, rank_config):
        field = rank_config.get("field")
        mode = rank_config.get("mode", "white_list")
        items = rank_config.get("items", [])
        count = 1
        
        if field == "custom":
            unit = rank_config.get("unit", "default")
            values = 0
            if unit != "default":
                if any(item.startswith("minecraft:damage_") for item in items):
                    if unit == "heart":
                        count = 20
                    elif unit == "half-heart":
                        count = 10
                if any(item.endswith("_one_cm") for item in items):
                    if unit == "m":
                        count = 100
                    elif unit == "km":
                        count = 100000
                if any(item.endswith("_time") or item.startswith("minecraft:time_") for item in items):
                    if unit == "s":
                        count = 20
                    elif unit == "min":
                        count = 1200
                    elif unit == "h":
                        count = 72000
                    elif unit == "day":
                        count = 1728000
                    elif unit == "game-day":
                        count = 24000
            custom_stats = stats.get("stats", {}).get("minecraft:custom", {})
            for item in custom_stats:
                values += custom_stats.get(item, 0)

            return round(values / count, 2)
        
        category = STAT_CATEGORY_MAP.get(field)
        if not category:
            return 0
        
        stat_dict = stats.get("stats", {}).get(category, {})
        
        if mode == "all":
            target_items = stat_dict.keys()
        elif mode == "white_list":
            target_items = items
        elif mode == "black_list":
            target_items = [k for k in stat_dict.keys() if k not in items]
        else:
            target_items = items
        
        total = 0
        for item in target_items:
            total += stat_dict.get(item, 0)
        
        return total
    
    def get_all_ranks(self):
        usercache = self.load_usercache()
        player_stats = []
        rank_config = self.load_rank_config()
        
        for filename in os.listdir(self.STATS_DIR):
            if filename.endswith(".json"):
                uuid = filename.replace(".json", "")
                stats = self.load_player_stats(uuid)
                values = self.get_stat_values(stats)

                for custom_rank in rank_config.get("custom_ranks", []):
                    custom_value = self.get_custom_rank_data(stats, custom_rank)
                    values += (custom_value,)
                player_stats.append((uuid, *values))
        
        ranks = {}
        for idx, field in enumerate(DEFAULT_RANK_FIELDS, 1):
            ranks[field] = sorted(player_stats, key=lambda x: x[idx], reverse=True)[:10]
        
        for custom_rank in rank_config.get("custom_ranks", []):
            custom_field = custom_rank["name"]
            ranks[custom_field] = sorted(player_stats, key=lambda x: x[-1], reverse=True)[:10]
        
        def filter_fields(rank, field):
            res = []
            if field in DEFAULT_RANK_FIELDS:
                field_idx = DEFAULT_RANK_FIELDS.index(field) + 1
            else:
                field_idx = -1

            for row in rank:
                uuid = row[0]
                name = usercache.get(uuid, uuid)
                value = row[field_idx]
                entry = {"uuid": uuid, "name": name, field: value}
                if field == "play_time":
                    entry["play_time_hours"] = round(value / 20 / 3600, 2)
                elif field == "aviate_cm":
                    entry["aviate_km"] = round(value / 100000, 2) 
                elif field == "damage_taken":
                    entry["damage_taken_hearts"] = round(value / 20, 1)
                res.append(entry)
            return res
        
        return {field: filter_fields(ranks[field], field) for field in ranks}