"""
RL-based Anomaly Detector
Uses trained RL agent to determine optimal parameters
"""

import numpy as np
import os
from typing import Dict, Any
from app.utils.anomaly_detector import AnomalyDetector


class RLAnomalyDetector(AnomalyDetector):
    """
    RL 기반 이상탐지
    
    학습된 RL 에이전트가 최적의 파라미터를 선택
    """
    
    def __init__(self):
        super().__init__()
        self.rl_agent = None
        self.use_rl = self._load_rl_model()
    
    def _load_rl_model(self) -> bool:
        """RL 모델 로드"""
        model_path = 'models/rl_artwork_agent.zip'
        
        if not os.path.exists(model_path):
            print("ℹ️  RL model not found. Using heuristic parameters.")
            return False
        
        try:
            from app.utils.rl_environment import ArtworkAuthEnv
            from app.utils.rl_agent import RLfDAgent
            
            # Dummy environment for model loading
            # 실제 이미지는 analyze()에서 설정
            self.rl_agent = None  # Will be loaded per-image
            
            print("✅ RL model ready")
            return True
            
        except ImportError:
            print("⚠️  stable-baselines3 not installed. Using heuristic.")
            return False
        except Exception as e:
            print(f"⚠️  Failed to load RL model: {e}")
            return False
    
    def analyze(self, image_path: str) -> Dict[str, Any]:
        """
        RL 기반 분석
        
        1. RL 에이전트로 최적 파라미터 예측
        2. 해당 파라미터로 이상탐지 수행
        """
        if not self.use_rl or self.rl_agent is None:
            # Fallback to heuristic
            return super().analyze(image_path)
        
        try:
            from app.utils.rl_environment import ArtworkAuthEnv
            from app.utils.rl_agent import RLfDAgent
            
            # Create environment for this image
            env = ArtworkAuthEnv(image_path, ground_truth=None)
            
            # Load agent
            agent = RLfDAgent(env)
            agent.load('models/rl_artwork_agent')
            
            # Get state
            state, _ = env.reset()
            
            # Predict optimal action
            action, _ = agent.predict(state)
            
            # Parse action
            threshold = float(action[0])
            weights = action[1:5] / action[1:5].sum()
            
            # Perform analysis with RL parameters
            result = self._analyze_with_params(image_path, threshold, weights)
            
            result['rl_enabled'] = True
            result['rl_threshold'] = threshold
            result['rl_weights'] = weights.tolist()
            
            print(f"🤖 RL Analysis: threshold={threshold:.2f}, weights={weights}")
            
            return result
            
        except Exception as e:
            print(f"⚠️  RL analysis failed: {e}. Using heuristic.")
            return super().analyze(image_path)
    
    def _analyze_with_params(self, image_path: str, threshold: float, 
                            weights: np.ndarray) -> Dict[str, Any]:
        """지정된 파라미터로 분석"""
        import cv2
        
        img = cv2.imread(image_path)
        if img is None:
            return self._default_result()
        
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # 기존 분석 메서드 사용
        texture_score = self._analyze_texture(img)
        edge_score = self._analyze_edges(img)
        color_score = self._analyze_color_distribution(img_rgb)
        noise_score = self._analyze_noise_patterns(img)
        
        scores = np.array([texture_score, edge_score, color_score, noise_score])
        
        # 가중치 적용
        anomaly_score = float(np.dot(scores, weights))
        is_suspicious = anomaly_score > threshold
        
        return {
            'anomaly_score': anomaly_score,
            'is_suspicious': is_suspicious,
            'details': {
                'texture_anomaly': float(texture_score),
                'edge_anomaly': float(edge_score),
                'color_anomaly': float(color_score),
                'noise_anomaly': float(noise_score)
            },
            'flags': self._generate_flags(texture_score, edge_score, color_score, noise_score),
            'threshold': threshold,
            'weights': weights.tolist()
        }

