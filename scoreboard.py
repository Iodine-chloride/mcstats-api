from pathlib import Path
from nbtlib import load, File, Compound, List

class Scoreboard:
    def __init__(self, scoreboard_path="./world/data/scoreboard.dat"):
        self.scoreboard_path = Path(scoreboard_path)
        self.load_scoreboard()
    
    def load_scoreboard(self):
        try:
            if self.scoreboard_path.exists():
                self.scoreboard = load(self.scoreboard_path)
            else:
                self.scoreboard = File({
                    'data': Compound({
                        'PlayerScores': List(),
                        'Objectives': List(),
                        'DisplaySlots': Compound()
                    })
                })
        except Exception as e:
            print(f"Error loading scoreboard: {e}")
            self.scoreboard = File({
                'data': Compound({
                    'PlayerScores': List(),
                    'Objectives': List(),
                    'DisplaySlots': Compound()
                })
            })
    
    def save_scoreboard(self):
        try:
            self.scoreboard.save(self.scoreboard_path)
        except Exception as e:
            print(f"Error saving scoreboard: {e}")
    
    def get_leaderboard(self, objective_name, limit=10):
        leaderboard = []
        
        objective = next((obj for obj in self.scoreboard['data']['Objectives'] 
                         if obj['Name'] == objective_name), None)
        
        if not objective:
            return None

        player_scores = []
        for score in self.scoreboard['data']['PlayerScores']:
            if score['Objective'] == objective_name:
                player_scores.append({
                    "name": score['Name'],
                    "score": score['Score']
                })
        
        player_scores.sort(key=lambda x: x['score'], reverse=True)
        
        return player_scores[:limit]
    
    def get_player_scores(self, player_name):
        player_scores = {}
        
        for score in self.scoreboard['data']['PlayerScores']:
            if score['Name'] == player_name:
                objective = score['Objective']
                player_scores[objective] = score['Score']
        
        if not player_scores:
            return None
        
        return player_scores
    
    def get_all_objectives(self):
        return [obj['Name'] for obj in self.scoreboard['data']['Objectives']]