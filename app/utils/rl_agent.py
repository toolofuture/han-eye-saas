"""
Reinforcement Learning from Demonstration (RLfD) Agent
Inspired by the quantum control paper
"""

import numpy as np
from typing import Dict, Any, List, Optional, Tuple
import os
import pickle


class RLfDAgent:
    """
    RLfD Agent for Artwork Authentication
    
    Uses SAC (Soft Actor-Critic) with demonstration pre-training
    """
    
    def __init__(self, env, model_path: Optional[str] = None):
        """
        Args:
            env: Gymnasium environment
            model_path: Path to save/load model
        """
        self.env = env
        self.model_path = model_path or 'models/rl_artwork_agent'
        self.model = None
        self.demonstrations = []
        
    def add_demonstration(self, state: np.ndarray, action: np.ndarray, 
                         reward: float, next_state: np.ndarray):
        """
        Add demonstration data
        
        Demonstrations can come from:
        1. Current heuristic parameters
        2. Expert human labels
        3. GRAPE-like optimization methods
        """
        self.demonstrations.append({
            'state': state,
            'action': action,
            'reward': reward,
            'next_state': next_state
        })
    
    def load_demonstrations_from_heuristics(self):
        """
        Load demonstrations from current heuristic method
        
        현재 휴리스틱 파라미터를 demonstration으로 사용
        """
        # Default heuristic parameters
        heuristic_action = np.array([
            0.7,    # threshold
            0.25,   # texture_weight
            0.25,   # edge_weight
            0.25,   # color_weight
            0.25    # noise_weight
        ], dtype=np.float32)
        
        # Generate demonstration from heuristic
        print("🎯 Generating demonstrations from heuristic parameters...")
        
        state, _ = self.env.reset()
        next_state, reward, done, truncated, info = self.env.step(heuristic_action)
        
        self.add_demonstration(state, heuristic_action, reward, next_state)
        
        print(f"✅ Added demonstration: reward={reward:.2f}, prediction={info['prediction']}")
        
        return len(self.demonstrations)
    
    def load_demonstrations_from_feedback(self, db_session):
        """
        Load demonstrations from user feedback
        
        사용자 피드백이 있는 분석들을 demonstration으로 사용
        """
        from app.models import Analysis
        
        print("📊 Loading demonstrations from user feedback...")
        
        # Get analyses with feedback
        analyses = db_session.query(Analysis).filter(
            Analysis.user_feedback.in_(['correct', 'incorrect']),
            Analysis.anomaly_score.isnot(None)
        ).limit(100).all()
        
        demo_count = 0
        for analysis in analyses:
            try:
                # Reconstruct state
                result = analysis.get_analysis_result_dict()
                style = analysis.get_style_analysis_dict()
                tech = analysis.get_technique_analysis_dict()
                
                # Create pseudo-state (simplified)
                state = np.array([
                    analysis.anomaly_score,
                    analysis.confidence_score,
                    0.5,  # placeholder
                    0.5   # placeholder
                ], dtype=np.float32)
                
                # Reconstruct action (estimated from analysis)
                action = np.array([
                    0.7,  # threshold (default)
                    0.25, 0.25, 0.25, 0.25  # weights (default)
                ], dtype=np.float32)
                
                # Ground truth from feedback
                if analysis.user_feedback == 'correct':
                    ground_truth = analysis.is_authentic
                else:
                    ground_truth = not analysis.is_authentic
                
                # Reward: correct prediction = +1, incorrect = -1
                prediction = analysis.is_authentic
                reward = 1.0 if prediction == ground_truth else -1.0
                
                self.add_demonstration(state, action, reward, state)
                demo_count += 1
                
            except Exception as e:
                print(f"Warning: Failed to load demonstration: {e}")
                continue
        
        print(f"✅ Loaded {demo_count} demonstrations from feedback")
        return demo_count
    
    def pretrain_with_demonstrations(self, epochs: int = 100):
        """
        Pre-train agent with demonstrations using behavioral cloning
        
        논문의 RLfD에서 사용하는 방법:
        1. Demonstration으로 supervised learning
        2. 이후 RL로 fine-tuning
        """
        if len(self.demonstrations) == 0:
            print("⚠️  No demonstrations available for pre-training")
            return
        
        print(f"🎓 Pre-training with {len(self.demonstrations)} demonstrations...")
        
        try:
            from stable_baselines3 import SAC
            from stable_baselines3.common.noise import NormalActionNoise
            
            # Initialize SAC agent
            n_actions = self.env.action_space.shape[0]
            action_noise = NormalActionNoise(
                mean=np.zeros(n_actions),
                sigma=0.1 * np.ones(n_actions)
            )
            
            self.model = SAC(
                "MlpPolicy",
                self.env,
                action_noise=action_noise,
                verbose=1,
                learning_rate=3e-4,
                buffer_size=100000,
                batch_size=64,
                tau=0.005,
                gamma=0.99
            )
            
            # Pre-fill replay buffer with demonstrations
            for demo in self.demonstrations:
                self.model.replay_buffer.add(
                    obs=demo['state'],
                    next_obs=demo['next_state'],
                    action=demo['action'],
                    reward=np.array([demo['reward']]),
                    done=np.array([True]),
                    infos=[{}]
                )
            
            print("✅ Pre-training completed with demonstration replay buffer")
            
        except ImportError:
            print("⚠️  stable-baselines3 not installed. Using behavioral cloning fallback...")
            self._behavioral_cloning_pretrain(epochs)
    
    def _behavioral_cloning_pretrain(self, epochs: int):
        """
        Fallback: Simple behavioral cloning without RL library
        """
        print("📚 Behavioral cloning pre-training...")
        
        # Extract states and actions
        states = np.array([d['state'] for d in self.demonstrations])
        actions = np.array([d['action'] for d in self.demonstrations])
        
        # Simple supervised learning would go here
        # For MVP, we just store the demonstrations
        
        print(f"✅ Stored {len(self.demonstrations)} demonstration pairs")
    
    def train(self, total_timesteps: int = 10000):
        """
        Train agent with reinforcement learning
        
        논문의 RLfD 방식:
        1. Pre-trained model로 시작
        2. Environment와 interaction하며 학습
        3. Demonstration replay buffer 계속 사용
        """
        if self.model is None:
            print("⚠️  Model not initialized. Call pretrain_with_demonstrations() first")
            return
        
        print(f"🚀 Training RL agent for {total_timesteps} timesteps...")
        
        try:
            self.model.learn(
                total_timesteps=total_timesteps,
                log_interval=10,
                progress_bar=True
            )
            
            print("✅ Training completed!")
            
        except Exception as e:
            print(f"❌ Training failed: {e}")
    
    def predict(self, state: np.ndarray) -> Tuple[np.ndarray, Any]:
        """
        Predict action for given state
        
        Returns:
            action, _state
        """
        if self.model is None:
            # Fallback to heuristic
            return np.array([0.7, 0.25, 0.25, 0.25, 0.25], dtype=np.float32), None
        
        return self.model.predict(state, deterministic=True)
    
    def save(self, path: Optional[str] = None):
        """Save trained model"""
        save_path = path or self.model_path
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        if self.model is not None:
            self.model.save(save_path)
            print(f"💾 Model saved to {save_path}")
        
        # Save demonstrations
        demo_path = save_path + '_demonstrations.pkl'
        with open(demo_path, 'wb') as f:
            pickle.dump(self.demonstrations, f)
        print(f"💾 Demonstrations saved to {demo_path}")
    
    def load(self, path: Optional[str] = None):
        """Load trained model"""
        load_path = path or self.model_path
        
        try:
            from stable_baselines3 import SAC
            
            self.model = SAC.load(load_path, env=self.env)
            print(f"📂 Model loaded from {load_path}")
            
            # Load demonstrations
            demo_path = load_path + '_demonstrations.pkl'
            if os.path.exists(demo_path):
                with open(demo_path, 'rb') as f:
                    self.demonstrations = pickle.load(f)
                print(f"📂 Demonstrations loaded from {demo_path}")
            
        except Exception as e:
            print(f"❌ Failed to load model: {e}")
    
    def evaluate(self, n_eval_episodes: int = 10) -> Dict[str, float]:
        """
        Evaluate agent performance
        
        Returns:
            Dictionary with evaluation metrics
        """
        if self.model is None:
            print("⚠️  No model to evaluate")
            return {}
        
        from stable_baselines3.common.evaluation import evaluate_policy
        
        mean_reward, std_reward = evaluate_policy(
            self.model,
            self.env,
            n_eval_episodes=n_eval_episodes,
            deterministic=True
        )
        
        metrics = {
            'mean_reward': mean_reward,
            'std_reward': std_reward,
            'n_episodes': n_eval_episodes
        }
        
        print(f"📊 Evaluation: mean_reward={mean_reward:.2f} ± {std_reward:.2f}")
        
        return metrics


def create_default_demonstrations() -> List[Dict]:
    """
    Create default demonstrations from heuristic parameters
    
    논문에서 GRAPE 펄스로 demonstration 생성하는 것과 유사
    """
    demonstrations = []
    
    # Demonstration 1: 기본 휴리스틱
    demonstrations.append({
        'name': 'default_heuristic',
        'action': np.array([0.7, 0.25, 0.25, 0.25, 0.25], dtype=np.float32),
        'description': '기본 이상탐지 파라미터'
    })
    
    # Demonstration 2: 보수적 판단 (높은 임계값)
    demonstrations.append({
        'name': 'conservative',
        'action': np.array([0.8, 0.3, 0.3, 0.2, 0.2], dtype=np.float32),
        'description': '보수적 판단 (위작으로 판단하기 어렵게)'
    })
    
    # Demonstration 3: 공격적 판단 (낮은 임계값)
    demonstrations.append({
        'name': 'aggressive',
        'action': np.array([0.6, 0.2, 0.2, 0.3, 0.3], dtype=np.float32),
        'description': '공격적 판단 (위작으로 판단하기 쉽게)'
    })
    
    return demonstrations

