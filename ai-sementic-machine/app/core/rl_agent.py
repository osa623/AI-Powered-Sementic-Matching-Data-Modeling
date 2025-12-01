import numpy as np
import pickle
import os
from app.config import settings

class RLRankingAgent:
    """
    Simple Q-Learning agent to optimize search ranking weights
    State: (category_match, semantic_score_range)
    Action: Adjust ranking weight
    Reward: +1 for successful claim, -1 for rejection
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RLRankingAgent, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        print("Loading RL Agent...")
        self.q_table_path = os.path.join(settings.BASE_DIR, "data/models/rl_q_table.pkl")
        
        if os.path.exists(self.q_table_path):
            with open(self.q_table_path, 'rb') as f:
                self.q_table = pickle.load(f)
            print("✅ RL Q-Table Loaded.")
        else:
            # Initialize Q-table: state -> action -> Q-value
            self.q_table = {}
            print("✅ New Q-Table initialized.")
        
        self.alpha = 0.1  # Learning rate
        self.gamma = 0.9  # Discount factor
        self.epsilon = 0.1  # Exploration rate

    def get_state(self, match_info: dict):
        """Convert match info to discrete state"""
        category_match = 1 if match_info.get('category_matched') else 0
        score_range = int(match_info.get('semantic_score', 0) // 20)  # 0-4
        return (category_match, score_range)

    def choose_action(self, state):
        """Epsilon-greedy action selection"""
        if np.random.random() < self.epsilon or state not in self.q_table:
            return np.random.choice([0, 1, 2])  # 0: decrease, 1: keep, 2: increase weight
        return np.argmax(self.q_table[state])

    def update(self, state, action, reward, next_state):
        """Q-learning update"""
        if state not in self.q_table:
            self.q_table[state] = np.zeros(3)
        
        if next_state not in self.q_table:
            self.q_table[next_state] = np.zeros(3)
        
        # Q-learning formula
        current_q = self.q_table[state][action]
        max_next_q = np.max(self.q_table[next_state])
        new_q = current_q + self.alpha * (reward + self.gamma * max_next_q - current_q)
        self.q_table[state][action] = new_q

    def save(self):
        """Persist Q-table"""
        os.makedirs(os.path.dirname(self.q_table_path), exist_ok=True)
        with open(self.q_table_path, 'wb') as f:
            pickle.dump(self.q_table, f)
        print("✅ Q-Table saved.")
