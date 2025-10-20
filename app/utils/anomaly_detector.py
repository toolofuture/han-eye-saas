import numpy as np
from typing import Dict, Any, Tuple
import cv2
from PIL import Image

class AnomalyDetector:
    """
    Image-based anomaly detection for artwork authentication
    Uses computer vision techniques to detect suspicious patterns
    """
    
    def __init__(self):
        self.threshold = self._get_adaptive_threshold()
    
    def _get_adaptive_threshold(self) -> float:
        """
        피드백 데이터를 기반으로 최적 임계값 계산 (자가개선!)
        
        사용자 피드백이 쌓이면 임계값이 자동으로 조정됩니다.
        """
        try:
            from app.models import Analysis
            
            # 피드백이 있는 분석들
            analyses = Analysis.query.filter(
                Analysis.user_feedback.isnot(None),
                Analysis.anomaly_score.isnot(None)
            ).all()
            
            if len(analyses) < 10:  # 데이터 부족
                return 0.7  # 기본값
            
            # Ground truth 계산
            authentic_scores = []
            fake_scores = []
            
            for analysis in analyses:
                # 실제 정답 결정
                if analysis.user_feedback == 'correct':
                    ground_truth = analysis.is_authentic
                elif analysis.user_feedback == 'incorrect':
                    ground_truth = not analysis.is_authentic
                else:
                    continue
                
                # 진품/위작별 anomaly score 수집
                if ground_truth:
                    authentic_scores.append(analysis.anomaly_score)
                else:
                    fake_scores.append(analysis.anomaly_score)
            
            if not authentic_scores or not fake_scores:
                return 0.7
            
            import numpy as np
            
            # 최적 임계값: 진품과 위작의 평균 중간값
            optimal_threshold = (np.mean(authentic_scores) + np.mean(fake_scores)) / 2
            
            # 0.3 ~ 0.9 사이로 제한
            optimal_threshold = max(0.3, min(0.9, optimal_threshold))
            
            print(f"🔧 자가개선: 임계값 조정 0.7 → {optimal_threshold:.2f}")
            print(f"   (진품 평균: {np.mean(authentic_scores):.2f}, 위작 평균: {np.mean(fake_scores):.2f})")
            
            return optimal_threshold
            
        except Exception as e:
            print(f"Adaptive threshold error: {e}")
            return 0.7  # 기본값
    
    def analyze(self, image_path: str) -> Dict[str, Any]:
        """
        Perform anomaly detection on artwork image
        
        Args:
            image_path: Path to the artwork image
        
        Returns:
            Dictionary with anomaly detection results
        """
        try:
            # Load image
            img = cv2.imread(image_path)
            if img is None:
                return self._default_result()
            
            # Convert to RGB
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            
            # Perform various analyses
            texture_score = self._analyze_texture(img)
            edge_score = self._analyze_edges(img)
            color_score = self._analyze_color_distribution(img_rgb)
            noise_score = self._analyze_noise_patterns(img)
            
            # Calculate overall anomaly score
            anomaly_score = (texture_score + edge_score + color_score + noise_score) / 4
            
            # Determine if suspicious
            is_suspicious = anomaly_score > self.threshold
            
            return {
                'anomaly_score': float(anomaly_score),
                'is_suspicious': is_suspicious,
                'details': {
                    'texture_anomaly': float(texture_score),
                    'edge_anomaly': float(edge_score),
                    'color_anomaly': float(color_score),
                    'noise_anomaly': float(noise_score)
                },
                'flags': self._generate_flags(texture_score, edge_score, color_score, noise_score)
            }
            
        except Exception as e:
            print(f"Anomaly detection error: {e}")
            return self._default_result()
    
    def _analyze_texture(self, img: np.ndarray) -> float:
        """Analyze texture patterns for anomalies"""
        try:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Calculate texture using Laplacian variance
            laplacian = cv2.Laplacian(gray, cv2.CV_64F)
            variance = laplacian.var()
            
            # Normalize to 0-1 range
            # Low variance might indicate digital manipulation
            normalized = 1.0 - min(variance / 1000.0, 1.0)
            
            return normalized
        except:
            return 0.0
    
    def _analyze_edges(self, img: np.ndarray) -> float:
        """Analyze edge patterns for digital manipulation"""
        try:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Detect edges using Canny
            edges = cv2.Canny(gray, 100, 200)
            
            # Calculate edge density
            edge_density = np.sum(edges > 0) / edges.size
            
            # Too sharp or too blurred edges might be suspicious
            # Optimal range is around 0.1-0.3
            if 0.1 <= edge_density <= 0.3:
                return 0.0
            elif edge_density < 0.1:
                return (0.1 - edge_density) / 0.1
            else:
                return (edge_density - 0.3) / 0.7
                
        except:
            return 0.0
    
    def _analyze_color_distribution(self, img_rgb: np.ndarray) -> float:
        """Analyze color distribution for unnatural patterns"""
        try:
            # Calculate color histograms
            hist_r = cv2.calcHist([img_rgb], [0], None, [256], [0, 256])
            hist_g = cv2.calcHist([img_rgb], [1], None, [256], [0, 256])
            hist_b = cv2.calcHist([img_rgb], [2], None, [256], [0, 256])
            
            # Normalize
            hist_r = hist_r / hist_r.sum()
            hist_g = hist_g / hist_g.sum()
            hist_b = hist_b / hist_b.sum()
            
            # Calculate entropy
            def entropy(hist):
                hist = hist[hist > 0]
                return -np.sum(hist * np.log2(hist))
            
            avg_entropy = (entropy(hist_r) + entropy(hist_g) + entropy(hist_b)) / 3
            
            # Very low or very high entropy might be suspicious
            # Optimal range is around 4-7
            if 4 <= avg_entropy <= 7:
                return 0.0
            elif avg_entropy < 4:
                return (4 - avg_entropy) / 4
            else:
                return (avg_entropy - 7) / 8
                
        except:
            return 0.0
    
    def _analyze_noise_patterns(self, img: np.ndarray) -> float:
        """Analyze noise patterns for artificial generation"""
        try:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Apply Gaussian blur and subtract to get noise
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            noise = cv2.absdiff(gray, blurred)
            
            # Calculate noise statistics
            noise_mean = np.mean(noise)
            noise_std = np.std(noise)
            
            # Unnatural noise patterns might indicate digital manipulation
            # Normalize to 0-1 range
            noise_score = min((noise_mean + noise_std) / 100.0, 1.0)
            
            return noise_score
            
        except:
            return 0.0
    
    def _generate_flags(self, texture: float, edge: float, color: float, noise: float) -> list:
        """Generate warning flags based on anomaly scores"""
        flags = []
        
        if texture > 0.7:
            flags.append('비정상적인 텍스처 패턴 감지')
        if edge > 0.7:
            flags.append('의심스러운 엣지 패턴')
        if color > 0.7:
            flags.append('부자연스러운 색상 분포')
        if noise > 0.7:
            flags.append('인위적인 노이즈 패턴')
        
        return flags
    
    def _default_result(self) -> Dict[str, Any]:
        """Return default result when analysis fails"""
        return {
            'anomaly_score': 0.0,
            'is_suspicious': False,
            'details': {
                'texture_anomaly': 0.0,
                'edge_anomaly': 0.0,
                'color_anomaly': 0.0,
                'noise_anomaly': 0.0
            },
            'flags': []
        }

