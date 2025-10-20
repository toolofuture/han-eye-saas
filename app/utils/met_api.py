import requests
import time
from typing import Dict, Any, List, Optional

class MetAPI:
    """
    Interface to The Metropolitan Museum of Art Collection API
    Documentation: https://metmuseum.github.io/
    """
    
    BASE_URL = 'https://collectionapi.metmuseum.org/public/collection/v1'
    
    def __init__(self):
        self.session = requests.Session()
    
    def search_objects(self, query: str, has_images: bool = True) -> List[int]:
        """
        Search for objects in the Met collection
        
        Args:
            query: Search query string
            has_images: Only return objects with images
        
        Returns:
            List of object IDs
        """
        try:
            url = f"{self.BASE_URL}/search"
            params = {
                'q': query,
                'hasImages': 'true' if has_images else 'false'
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            return data.get('objectIDs', [])[:100]  # Limit to 100 results
            
        except Exception as e:
            print(f"Met API search error: {e}")
            return []
    
    def get_object(self, object_id: int) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific object
        
        Args:
            object_id: Met object ID
        
        Returns:
            Dictionary with object data or None
        """
        try:
            url = f"{self.BASE_URL}/objects/{object_id}"
            
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            print(f"Met API get object error: {e}")
            return None
    
    def get_departments(self) -> List[Dict[str, Any]]:
        """Get list of all departments"""
        try:
            url = f"{self.BASE_URL}/departments"
            
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            return data.get('departments', [])
            
        except Exception as e:
            print(f"Met API get departments error: {e}")
            return []
    
    def get_objects_by_department(self, department_id: int, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get objects from a specific department
        
        Args:
            department_id: Department ID
            limit: Maximum number of objects to return
        
        Returns:
            List of object data dictionaries
        """
        try:
            url = f"{self.BASE_URL}/objects"
            params = {'departmentIds': department_id}
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            object_ids = data.get('objectIDs', [])[:limit]
            
            objects = []
            for obj_id in object_ids:
                obj_data = self.get_object(obj_id)
                if obj_data and obj_data.get('primaryImage'):
                    objects.append(obj_data)
                    time.sleep(0.1)  # Rate limiting
                
                if len(objects) >= limit:
                    break
            
            return objects
            
        except Exception as e:
            print(f"Met API get objects by department error: {e}")
            return []
    
    def extract_artwork_info(self, met_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract relevant information from Met API response
        
        Args:
            met_data: Raw data from Met API
        
        Returns:
            Cleaned artwork information
        """
        return {
            'title': met_data.get('title', 'Unknown'),
            'artist': met_data.get('artistDisplayName', 'Unknown'),
            'period': met_data.get('period', ''),
            'medium': met_data.get('medium', ''),
            'dimensions': met_data.get('dimensions', ''),
            'image_url': met_data.get('primaryImage', ''),
            'met_object_id': met_data.get('objectID'),
            'department': met_data.get('department', ''),
            'culture': met_data.get('culture', ''),
            'object_date': met_data.get('objectDate', ''),
            'credit_line': met_data.get('creditLine', ''),
            'classification': met_data.get('classification', '')
        }
    
    def download_sample_dataset(self, num_samples: int = 100) -> List[Dict[str, Any]]:
        """
        Download a sample dataset of artworks for training
        
        Args:
            num_samples: Number of samples to download
        
        Returns:
            List of artwork data
        """
        artworks = []
        
        # Get departments
        departments = self.get_departments()
        
        if not departments:
            return artworks
        
        # Focus on painting and sculpture departments
        target_depts = ['European Paintings', 'American Paintings and Sculpture', 
                       'Asian Art', 'Modern and Contemporary Art']
        
        for dept in departments:
            if dept['displayName'] in target_depts:
                dept_objects = self.get_objects_by_department(
                    dept['departmentId'], 
                    limit=num_samples // len(target_depts)
                )
                artworks.extend(dept_objects)
                
                if len(artworks) >= num_samples:
                    break
        
        return artworks[:num_samples]

