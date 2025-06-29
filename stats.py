from statspublic import StatsPublic, DEFAULT_RANK_FIELDS

class StatsPlayer:
    def __init__(self, stats_public: StatsPublic):
        self.stats_public = stats_public

    def get_player_stats(self, identifier):
        usercache = self.stats_public.load_usercache()
        rank_config = self.stats_public.load_rank_config()
        
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
        
        stats = self.stats_public.load_player_stats(player_uuid)
        if not stats:
            return None
        
        values = self.stats_public.get_stat_values(stats)
        result = dict(zip(DEFAULT_RANK_FIELDS, values))
        
        for custom_rank in rank_config.get("custom_ranks", []):
            custom_value = self.stats_public.get_custom_rank_data(stats, custom_rank)
            result[custom_rank["name"]] = custom_value
        
        result["play_time_hours"] = round(result["play_time"] / 20 / 3600, 2)
        result["aviate_km"] = round(result["aviate_cm"] / 100000, 2)
        result["damage_taken_hearts"] = round(result["damage_taken"] / 20, 1)
        
        result["uuid"] = player_uuid
        result["name"] = usercache.get(player_uuid, "Unknown")
        
        return result