from flask import Flask, jsonify
from rank import StatsRank, DEFAULT_RANK_FIELDS
from stats import StatsPlayer

def create_app(stats_dir="./world/stats", 
               usercache_path="./usercache.json", 
               rank_config_path="./rank_config.json"):
    app = Flask(__name__)
    core = StatsRank(
        stats_dir=stats_dir,
        usercache_path=usercache_path,
        rank_config_path=rank_config_path
    )
    
    player_stats = StatsPlayer(
        stats_dir=stats_dir,
        usercache_path=usercache_path,
        rank_config_path=rank_config_path
    )

    @app.route('/api/rank/all', methods=['GET'])
    def api_rank_all():
        return jsonify(core.get_all_ranks())
    
    @app.route('/api/rank/<field>', methods=['GET'])
    def api_rank_field(field):
        rank_config = core.load_rank_config()
        all_fields = DEFAULT_RANK_FIELDS.copy()
        custom_fields = [rank["name"] for rank in rank_config.get("custom_ranks", [])]
        all_fields.extend(custom_fields)
        
        if field not in all_fields:
            return jsonify({
                "error": f"field must be one of {DEFAULT_RANK_FIELDS} or custom ranks: {custom_fields}"
            }), 404
        
        all_ranks = core.get_all_ranks()
        return jsonify({field: all_ranks[field]})
    
    @app.route('/api/player/<player_identifier>', methods=['GET'])
    def api_player_stats(player_identifier):
        stats = player_stats.get_player_stats(player_identifier)
        if not stats:
            return jsonify({"error": "Player not found"}), 404
        return jsonify(stats)
    
    return app