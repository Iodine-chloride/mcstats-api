import argparse
from api import create_app

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='MCSTATS-API')
    parser.add_argument('--port', type=int, default=5000, 
                        help='自定义端口 (默认: 5000)')
    parser.add_argument('--stats-dir', type=str, default="./world/stats",
                        help='统计数据目录 (默认: ./world/stats)')
    parser.add_argument('--usercache', type=str, default="./usercache.json",
                        help='用户缓存文件路径 (默认: ./usercache.json)')
    parser.add_argument('--rank-config', type=str, default="./rank_config.json",
                        help='排行配置文件路径 (默认: ./rank_config.json)')
    
    args = parser.parse_args()
    
    app = create_app(
        stats_dir=args.stats_dir,
        usercache_path=args.usercache,
        rank_config_path=args.rank_config
    )
    
    app.run(host="0.0.0.0", port=args.port)