import os
from statspublic import StatsPublic, DEFAULT_RANK_FIELDS

class StatsRank:
    def __init__(self, stats_public: StatsPublic):
        self.stats_public = stats_public

    def get_all_ranks(self):
        usercache = self.stats_public.load_usercache()
        player_stats = []
        rank_config = self.stats_public.load_rank_config()
        
        for filename in os.listdir(self.stats_public.STATS_DIR):
            if filename.endswith(".json"):
                uuid = filename.replace(".json", "")
                stats = self.stats_public.load_player_stats(uuid)
                values = self.stats_public.get_stat_values(stats)

                for custom_rank in rank_config.get("custom_ranks", []):
                    custom_value = self.stats_public.get_custom_rank_data(stats, custom_rank)
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