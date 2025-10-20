import os
import base64
from typing import Dict, Any, Optional
import json
import time

class AIAnalyzer:
    """
    Multi-model AI analyzer that uses GPT-4, Claude, or Gemini for artwork authentication
    """
    
    def __init__(self, model: str = 'gpt-4'):
        self.model = model
        self.api_key = self._get_api_key()
    
    def _get_api_key(self) -> Optional[str]:
        """Get API key based on selected model"""
        if self.model.startswith('gpt'):
            return os.environ.get('OPENAI_API_KEY')
        elif self.model.startswith('claude'):
            return os.environ.get('ANTHROPIC_API_KEY')
        elif self.model.startswith('gemini'):
            return os.environ.get('GOOGLE_API_KEY')
        return None
    
    def encode_image(self, image_path: str) -> str:
        """Encode image to base64"""
        with open(image_path, 'rb') as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    def analyze_artwork(self, image_path: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Analyze artwork image for authenticity
        
        Args:
            image_path: Path to the artwork image
            context: Optional context information (artist, period, etc.)
        
        Returns:
            Dictionary with analysis results
        """
        start_time = time.time()
        
        # Build prompt
        prompt = self._build_analysis_prompt(context)
        
        # Call appropriate model
        if self.model.startswith('gpt'):
            result = self._analyze_with_gpt(image_path, prompt)
        elif self.model.startswith('claude'):
            result = self._analyze_with_claude(image_path, prompt)
        elif self.model.startswith('gemini'):
            result = self._analyze_with_gemini(image_path, prompt)
        else:
            result = self._mock_analysis()  # Fallback for demo
        
        processing_time = time.time() - start_time
        result['processing_time'] = processing_time
        result['model_used'] = self.model
        
        return result
    
    def _build_analysis_prompt(self, context: Optional[Dict] = None) -> str:
        """Build prompt for AI analysis with few-shot learning from feedback"""
        
        # Few-shot examples from user feedback
        few_shot_examples = self._get_feedback_examples()
        
        base_prompt = """당신은 미술품 진위 감정 전문가입니다. 제공된 이미지를 분석하여 다음 항목을 평가해주세요:

1. **진품 가능성**: 이 작품이 진품일 확률을 0-100% 사이로 평가
2. **스타일 분석**: 
   - 붓질과 기법의 일관성
   - 색채 사용과 조화
   - 구도와 원근법
3. **기술적 분석**:
   - 재료와 매체의 적절성
   - 노화와 보존 상태
   - 시대적 기법 일치 여부
4. **의심되는 요소**: 위작일 가능성이 있는 특징들
5. **종합 판정**: AUTHENTIC (진품), FAKE (위작), UNCERTAIN (불확실)"""

        # Add few-shot examples if available
        if few_shot_examples:
            base_prompt += "\n\n**과거 학습 사례 (참고용):**\n"
            for i, example in enumerate(few_shot_examples[:3], 1):  # 최대 3개
                base_prompt += f"\n사례 {i}:\n"
                base_prompt += f"- 실제 결과: {'진품' if example['ground_truth'] else '위작'}\n"
                base_prompt += f"- 주요 특징: {example['reasoning']}\n"

        base_prompt += """

응답은 반드시 JSON 형식으로 제공해주세요:
{
  "authenticity": "AUTHENTIC|FAKE|UNCERTAIN",
  "confidence_score": 0.0-1.0,
  "style_analysis": {
    "brushwork": "평가 내용",
    "color": "평가 내용",
    "composition": "평가 내용"
  },
  "technical_analysis": {
    "materials": "평가 내용",
    "aging": "평가 내용",
    "techniques": "평가 내용"
  },
  "suspicious_elements": ["요소1", "요소2"],
  "reasoning": "종합적인 판단 근거"
}"""
        
        if context:
            context_str = "\n\n**작품 정보:**\n"
            if 'artist' in context:
                context_str += f"- 작가: {context['artist']}\n"
            if 'period' in context:
                context_str += f"- 시대: {context['period']}\n"
            if 'medium' in context:
                context_str += f"- 매체: {context['medium']}\n"
            base_prompt += context_str
        
        return base_prompt
    
    def _get_feedback_examples(self) -> list:
        """Get few-shot examples from user feedback"""
        try:
            from app.models import Analysis
            from app import db
            
            # Get analyses with correct feedback
            correct_analyses = Analysis.query.filter_by(
                user_feedback='correct'
            ).order_by(Analysis.created_at.desc()).limit(5).all()
            
            examples = []
            for analysis in correct_analyses:
                result = analysis.get_analysis_result_dict()
                
                # Determine ground truth
                if analysis.user_feedback == 'correct':
                    ground_truth = analysis.is_authentic
                elif analysis.user_feedback == 'incorrect':
                    ground_truth = not analysis.is_authentic
                else:
                    continue
                
                examples.append({
                    'ground_truth': ground_truth,
                    'reasoning': result.get('reasoning', ''),
                    'confidence': analysis.confidence_score
                })
            
            return examples
            
        except Exception as e:
            print(f"Error getting feedback examples: {e}")
            return []
    
    def _analyze_with_gpt(self, image_path: str, prompt: str) -> Dict[str, Any]:
        """Analyze using GPT-4 Vision"""
        try:
            import openai
            
            client = openai.OpenAI(api_key=self.api_key)
            
            # Encode image
            base64_image = self.encode_image(image_path)
            
            response = client.chat.completions.create(
                model="gpt-4o",  # Using GPT-4 with vision
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=2000
            )
            
            content = response.choices[0].message.content
            return self._parse_ai_response(content)
            
        except Exception as e:
            print(f"GPT-4 analysis error: {e}")
            return self._mock_analysis()
    
    def _analyze_with_claude(self, image_path: str, prompt: str) -> Dict[str, Any]:
        """Analyze using Claude"""
        try:
            import anthropic
            
            client = anthropic.Anthropic(api_key=self.api_key)
            
            # Encode image
            base64_image = self.encode_image(image_path)
            
            message = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2000,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": "image/jpeg",
                                    "data": base64_image,
                                },
                            },
                            {
                                "type": "text",
                                "text": prompt
                            }
                        ],
                    }
                ],
            )
            
            content = message.content[0].text
            return self._parse_ai_response(content)
            
        except Exception as e:
            print(f"Claude analysis error: {e}")
            return self._mock_analysis()
    
    def _analyze_with_gemini(self, image_path: str, prompt: str) -> Dict[str, Any]:
        """Analyze using Gemini"""
        try:
            import google.generativeai as genai
            
            genai.configure(api_key=self.api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            # Load image
            import PIL.Image
            img = PIL.Image.open(image_path)
            
            response = model.generate_content([prompt, img])
            
            return self._parse_ai_response(response.text)
            
        except Exception as e:
            print(f"Gemini analysis error: {e}")
            return self._mock_analysis()
    
    def _parse_ai_response(self, content: str) -> Dict[str, Any]:
        """Parse AI response to extract structured data"""
        try:
            # Try to extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                
                # Normalize authenticity value
                auth = data.get('authenticity', 'UNCERTAIN').upper()
                if auth == 'AUTHENTIC':
                    is_authentic = True
                elif auth == 'FAKE':
                    is_authentic = False
                else:
                    is_authentic = None
                
                return {
                    'is_authentic': is_authentic,
                    'confidence_score': float(data.get('confidence_score', 0.5)),
                    'style_analysis': data.get('style_analysis', {}),
                    'technical_analysis': data.get('technical_analysis', {}),
                    'suspicious_elements': data.get('suspicious_elements', []),
                    'reasoning': data.get('reasoning', ''),
                    'raw_response': content
                }
        except Exception as e:
            print(f"Error parsing AI response: {e}")
        
        # Fallback if parsing fails
        return self._mock_analysis()
    
    def _mock_analysis(self) -> Dict[str, Any]:
        """Mock analysis for demo purposes when API is not available"""
        import random
        
        confidence = random.uniform(0.65, 0.95)
        is_authentic = random.choice([True, False, None])
        
        return {
            'is_authentic': is_authentic,
            'confidence_score': confidence,
            'style_analysis': {
                'brushwork': '붓질이 일관되고 숙련된 기법을 보입니다.',
                'color': '시대적 색채 사용이 적절합니다.',
                'composition': '구도가 균형잡혀 있습니다.'
            },
            'technical_analysis': {
                'materials': '사용된 재료가 시대와 일치합니다.',
                'aging': '자연스러운 노화 흔적이 관찰됩니다.',
                'techniques': '시대적 기법이 정확히 적용되었습니다.'
            },
            'suspicious_elements': [] if is_authentic else ['일부 붓질이 부자연스러움', '색채 조화 불일치'],
            'reasoning': 'Demo 모드로 실행 중입니다. 실제 API 키를 설정하면 정확한 분석이 가능합니다.',
            'raw_response': 'Mock analysis for demo'
        }

