"""
Reinforcement Learning Environment for Artwork Authentication
Inspired by RLfD paper for quantum control
"""

import numpy as np
import gymnasium as gym
from gymnasium import spaces
from typing import Dict, Any, Optional, Tuple
import cv2


class ArtworkAuthEnv(gym.Env):
    """
    강화학습 환경: 미술품 진위 판별
    
    State: 이미지 특징 (텍스처, 엣지, 색상, 노이즈 점수)
    Action: 이상탐지 파라미터 (임계값, 가중치 등)
    Reward: 사용자 피드백 기반
    """
    
    metadata = {'render_modes': []}
    
    def __init__(self, image_path: str, ground_truth: Optional[bool] = None):
        super().__init__()
        
        self.image_path = image_path
        self.ground_truth = ground_truth  # True: 진품, False: 위작, None: 모름
        
        # Load image
        self.image = cv2.imread(image_path)
        if self.image is None:
            raise ValueError(f"Cannot load image: {image_path}")
        
        # State space: [texture_score, edge_score, color_score, noise_score]
        self.observation_space = spaces.Box(
            low=0.0, 
            high=1.0, 
            shape=(4,), 
            dtype=np.float32
        )
        
        # Action space: [threshold, texture_weight, edge_weight, color_weight, noise_weight]
        # 모든 값은 0~1 범위로 정규화
        self.action_space = spaces.Box(
            low=0.0,
            high=1.0,
            shape=(5,),
            dtype=np.float32
        )
        
        # Current state
        self.current_state = None
        self.current_step = 0
        self.max_steps = 1  # 단일 스텝 환경 (분석 1회)
        
    def reset(self, seed: Optional[int] = None, options: Optional[dict] = None) -> Tuple[np.ndarray, Dict]:
        """환경 초기화"""
        super().reset(seed=seed)
        
        # 초기 state 계산 (기본 파라미터 사용)
        self.current_state = self._compute_state(
            threshold=0.7,
            weights=[0.25, 0.25, 0.25, 0.25]
        )
        self.current_step = 0
        
        return self.current_state, {}
    
    def step(self, action: np.ndarray) -> Tuple[np.ndarray, float, bool, bool, Dict]:
        """
        환경 스텝
        
        Args:
            action: [threshold, texture_weight, edge_weight, color_weight, noise_weight]
        
        Returns:
            observation, reward, terminated, truncated, info
        """
        self.current_step += 1
        
        # Action 파싱
        threshold = float(action[0])  # 0~1
        weights = action[1:5] / action[1:5].sum()  # 정규화
        
        # 새로운 state 계산
        next_state = self._compute_state(threshold, weights)
        
        # 판단 수행
        anomaly_score = self._compute_anomaly_score(next_state, weights)
        prediction = anomaly_score > threshold  # True: 의심스러움 (위작), False: 정상 (진품)
        
        # Reward 계산
        reward = self._compute_reward(prediction)
        
        # Episode 종료
        terminated = True  # 단일 스텝 환경
        truncated = False
        
        info = {
            'prediction': not prediction,  # 진품 여부
            'anomaly_score': anomaly_score,
            'threshold': threshold,
            'weights': weights.tolist()
        }
        
        self.current_state = next_state
        
        return next_state, reward, terminated, truncated, info
    
    def _compute_state(self, threshold: float, weights: np.ndarray) -> np.ndarray:
        """현재 파라미터로 state 계산"""
        # 이미지 분석
        gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        img_rgb = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
        
        # 1. Texture score
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        variance = laplacian.var()
        texture_score = 1.0 - min(variance / 1000.0, 1.0)
        
        # 2. Edge score
        edges = cv2.Canny(gray, 100, 200)
        edge_density = np.sum(edges > 0) / edges.size
        if 0.1 <= edge_density <= 0.3:
            edge_score = 0.0
        elif edge_density < 0.1:
            edge_score = (0.1 - edge_density) / 0.1
        else:
            edge_score = (edge_density - 0.3) / 0.7
        
        # 3. Color score
        hist_r = cv2.calcHist([img_rgb], [0], None, [256], [0, 256])
        hist_g = cv2.calcHist([img_rgb], [1], None, [256], [0, 256])
        hist_b = cv2.calcHist([img_rgb], [2], None, [256], [0, 256])
        
        hist_r = hist_r / hist_r.sum()
        hist_g = hist_g / hist_g.sum()
        hist_b = hist_b / hist_b.sum()
        
        def entropy(hist):
            hist = hist[hist > 0]
            return -np.sum(hist * np.log2(hist))
        
        avg_entropy = (entropy(hist_r) + entropy(hist_g) + entropy(hist_b)) / 3
        
        if 4 <= avg_entropy <= 7:
            color_score = 0.0
        elif avg_entropy < 4:
            color_score = (4 - avg_entropy) / 4
        else:
            color_score = (avg_entropy - 7) / 8
        
        # 4. Noise score
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        noise = cv2.absdiff(gray, blurred)
        noise_mean = np.mean(noise)
        noise_std = np.std(noise)
        noise_score = min((noise_mean + noise_std) / 100.0, 1.0)
        
        state = np.array([texture_score, edge_score, color_score, noise_score], dtype=np.float32)
        
        return state
    
    def _compute_anomaly_score(self, state: np.ndarray, weights: np.ndarray) -> float:
        """가중치를 적용하여 anomaly score 계산"""
        return float(np.dot(state, weights))
    
    def _compute_reward(self, prediction: bool) -> float:
        """
        Reward 계산
        
        ground_truth가 있으면: 정확도 기반 보상
        ground_truth가 없으면: 확신도 기반 보상 (중간 보상)
        """
        if self.ground_truth is not None:
            # Ground truth 있음 (사용자 피드백)
            # prediction: False = 진품, True = 위작
            is_authentic_prediction = not prediction
            
            if is_authentic_prediction == self.ground_truth:
                # 정답!
                reward = 1.0
            else:
                # 오답
                reward = -1.0
        else:
            # Ground truth 없음 - 중간 보상 (exploration)
            # 너무 극단적이지 않은 판단에 작은 보상
            state_mean = np.mean(self.current_state)
            if 0.3 <= state_mean <= 0.7:
                reward = 0.1  # 작은 양수 보상
            else:
                reward = 0.0
        
        return reward
    
    def set_ground_truth(self, ground_truth: bool):
        """사용자 피드백 설정"""
        self.ground_truth = ground_truth


class BatchArtworkEnv(gym.Env):
    """
    여러 이미지를 배치로 처리하는 환경
    """
    
    def __init__(self, image_paths: list, ground_truths: Optional[list] = None):
        super().__init__()
        
        self.image_paths = image_paths
        self.ground_truths = ground_truths if ground_truths else [None] * len(image_paths)
        self.current_image_idx = 0
        
        # Single image environment
        self.current_env = None
        
        # State space: [texture, edge, color, noise, progress]
        self.observation_space = spaces.Box(
            low=0.0,
            high=1.0,
            shape=(5,),
            dtype=np.float32
        )
        
        # Action space: [threshold, texture_w, edge_w, color_w, noise_w]
        self.action_space = spaces.Box(
            low=0.0,
            high=1.0,
            shape=(5,),
            dtype=np.float32
        )
    
    def reset(self, seed: Optional[int] = None, options: Optional[dict] = None):
        """Reset to first image"""
        super().reset(seed=seed)
        
        self.current_image_idx = 0
        self.current_env = ArtworkAuthEnv(
            self.image_paths[0],
            self.ground_truths[0]
        )
        
        state, info = self.current_env.reset()
        
        # Add progress indicator
        progress = self.current_image_idx / len(self.image_paths)
        state_with_progress = np.append(state, progress)
        
        return state_with_progress, info
    
    def step(self, action: np.ndarray):
        """Step in current image environment"""
        state, reward, terminated, truncated, info = self.current_env.step(action)
        
        # Move to next image
        self.current_image_idx += 1
        
        if self.current_image_idx < len(self.image_paths):
            # More images to process
            self.current_env = ArtworkAuthEnv(
                self.image_paths[self.current_image_idx],
                self.ground_truths[self.current_image_idx]
            )
            next_state, _ = self.current_env.reset()
            terminated = False
        else:
            # All images processed
            next_state = state
            terminated = True
        
        # Add progress indicator
        progress = self.current_image_idx / len(self.image_paths)
        state_with_progress = np.append(next_state, progress)
        
        return state_with_progress, reward, terminated, truncated, info

