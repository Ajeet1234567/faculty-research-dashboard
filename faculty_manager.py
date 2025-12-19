"""
Faculty Manager Module
Handles CRUD operations for faculty members
"""
import json
import os
from typing import Dict, List, Optional
from datetime import datetime


class FacultyManager:
    """Manages faculty data persistence and operations."""
    
    def __init__(self, data_file: str):
        """Initialize the faculty manager with data file path."""
        self.data_file = data_file
        self.faculty_data = self._load_data()
    
    def _load_data(self) -> Dict:
        """Load faculty data from JSON file."""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return self._get_default_data()
        return self._get_default_data()
    
    def _get_default_data(self) -> Dict:
        """Return default faculty data for CUSB CS department."""
        return {
            "department": "Department of Computer Science",
            "institution": "Central University of South Bihar, Gaya",
            "last_updated": datetime.now().isoformat(),
            "faculty": [
                {
                    "id": "1",
                    "name": "Prof. Prabhat Ranjan",
                    "designation": "Professor & Head of Department",
                    "email": "",
                    "scholar_id": "",
                    "research_areas": ["Computer Science"],
                    "joined_year": None,
                    "profile_fetched": False
                },
                {
                    "id": "2",
                    "name": "Dr. Piyush Kumar Singh",
                    "designation": "Assistant Professor",
                    "email": "",
                    "scholar_id": "",
                    "research_areas": ["Image Processing", "Parallel Computing", "Wavelet Transform"],
                    "joined_year": 2016,
                    "profile_fetched": False
                },
                {
                    "id": "3",
                    "name": "Dr. Mrityunjay Singh",
                    "designation": "Assistant Professor",
                    "email": "",
                    "scholar_id": "",
                    "research_areas": ["Theoretical Computer Science", "Discrete Mathematics", "Algorithms", "Cryptography", "Security"],
                    "joined_year": 2023,
                    "profile_fetched": False
                },
                {
                    "id": "4",
                    "name": "Dr. Prakash Kumar",
                    "designation": "Assistant Professor",
                    "email": "",
                    "scholar_id": "",
                    "research_areas": ["Computer Science"],
                    "joined_year": None,
                    "profile_fetched": False
                },
                {
                    "id": "5",
                    "name": "Dr. Jainath Yadav",
                    "designation": "Assistant Professor",
                    "email": "",
                    "scholar_id": "",
                    "research_areas": ["Computer Science"],
                    "joined_year": None,
                    "profile_fetched": False
                },
                {
                    "id": "6",
                    "name": "Mr. Nemi Chandra Rathore",
                    "designation": "Assistant Professor",
                    "email": "",
                    "scholar_id": "",
                    "research_areas": ["Computer Science"],
                    "joined_year": None,
                    "profile_fetched": False
                }
            ]
        }
    
    def _save_data(self) -> bool:
        """Save faculty data to JSON file."""
        try:
            self.faculty_data["last_updated"] = datetime.now().isoformat()
            os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.faculty_data, f, indent=2, ensure_ascii=False)
            return True
        except IOError:
            return False
    
    def get_all_faculty(self) -> List[Dict]:
        """Get list of all faculty members."""
        return self.faculty_data.get("faculty", [])
    
    def get_faculty_by_id(self, faculty_id: str) -> Optional[Dict]:
        """Get a faculty member by ID."""
        for faculty in self.faculty_data.get("faculty", []):
            if faculty["id"] == faculty_id:
                return faculty
        return None
    
    def get_faculty_by_name(self, name: str) -> Optional[Dict]:
        """Get a faculty member by name (case-insensitive partial match)."""
        name_lower = name.lower()
        for faculty in self.faculty_data.get("faculty", []):
            if name_lower in faculty["name"].lower():
                return faculty
        return None
    
    def add_faculty(self, faculty_info: Dict) -> bool:
        """Add a new faculty member."""
        # Generate new ID
        existing_ids = [int(f["id"]) for f in self.faculty_data.get("faculty", []) if f["id"].isdigit()]
        new_id = str(max(existing_ids, default=0) + 1)
        
        faculty_info["id"] = new_id
        faculty_info.setdefault("profile_fetched", False)
        
        self.faculty_data.setdefault("faculty", []).append(faculty_info)
        return self._save_data()
    
    def update_faculty(self, faculty_id: str, updates: Dict) -> bool:
        """Update a faculty member's information."""
        for i, faculty in enumerate(self.faculty_data.get("faculty", [])):
            if faculty["id"] == faculty_id:
                self.faculty_data["faculty"][i].update(updates)
                return self._save_data()
        return False
    
    def delete_faculty(self, faculty_id: str) -> bool:
        """Delete a faculty member."""
        faculty_list = self.faculty_data.get("faculty", [])
        for i, faculty in enumerate(faculty_list):
            if faculty["id"] == faculty_id:
                faculty_list.pop(i)
                return self._save_data()
        return False
    
    def update_scholar_id(self, faculty_id: str, scholar_id: str) -> bool:
        """Update a faculty member's Google Scholar ID."""
        return self.update_faculty(faculty_id, {"scholar_id": scholar_id})
    
    def mark_profile_fetched(self, faculty_id: str, fetched: bool = True) -> bool:
        """Mark a faculty member's profile as fetched."""
        return self.update_faculty(faculty_id, {"profile_fetched": fetched})
    
    def get_department_info(self) -> Dict:
        """Get department information."""
        return {
            "department": self.faculty_data.get("department", ""),
            "institution": self.faculty_data.get("institution", ""),
            "last_updated": self.faculty_data.get("last_updated", ""),
            "faculty_count": len(self.faculty_data.get("faculty", []))
        }
    
    def export_faculty_list(self) -> List[Dict]:
        """Export faculty list for external use."""
        return [
            {
                "name": f["name"],
                "designation": f["designation"],
                "research_areas": ", ".join(f.get("research_areas", [])),
                "scholar_id": f.get("scholar_id", "")
            }
            for f in self.get_all_faculty()
        ]
    
    def reset_to_default(self) -> bool:
        """Reset faculty data to default values."""
        self.faculty_data = self._get_default_data()
        return self._save_data()
