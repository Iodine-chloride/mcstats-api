import json
from pathlib import Path
from rank import DEFAULT_RANK_FIELDS, STAT_CATEGORY_MAP

class StatsPlayer:
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
                    match unit:
                        case "heart": count = 20
                        case "half-heart": count = 10
                if any(item.endswith("_one_cm") for item in items):
                    match unit:
                        case "m": count = 100
                        case "km": count = 100000
                if any(item.endswith("_time") or item.startswith("minecraft:time_") for item in items):
                    match unit:
                        case "s": count = 20
                        case "min": count = 1200
                        case "h": count = 72000
                        case "day": count = 1728000
                        case "game-day": count = 24000
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
    
    def get_player_stats(self, identifier):
        usercache = self.load_usercache()
        rank_config = self.load_rank_config()
        
        player_uuid = None
        for uuid, name in usercache.items():
            if name.lower() == identifier.lower():
                player_uuid = uuid
                break
        
        if not player_uuid:
            try:
                if len(identifier) == 36:
                    player_uuid = identifier.replace("-", "")
                elif len(identifier) == 32:
                    player_uuid = identifier
            except:
                pass
        
        if not player_uuid:
            return None
        
        stats = self.load_player_stats(player_uuid)
        if not stats:
            return None
        
        values = self.get_stat_values(stats)
        result = dict(zip(DEFAULT_RANK_FIELDS, values))
        
        for custom_rank in rank_config.get("custom_ranks", []):
            custom_value = self.get_custom_rank_data(stats, custom_rank)
            result[custom_rank["name"]] = custom_value
        
        result["play_time_hours"] = round(result["play_time"] / 20 / 3600, 2)
        result["aviate_km"] = round(result["aviate_cm"] / 100000, 2)
        result["damage_taken_hearts"] = round(result["damage_taken"] / 20, 1)
        
        result["uuid"] = player_uuid
        result["name"] = usercache.get(player_uuid, "Unknown")
        
        return result