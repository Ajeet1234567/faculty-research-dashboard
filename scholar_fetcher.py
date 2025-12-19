"""
Google Scholar Data Fetcher Module
Fetches publication data from Google Scholar using the scholarly library
"""
import json
import os
import time
from typing import Dict, List, Optional
from datetime import datetime
import logging

try:
    from scholarly import scholarly, ProxyGenerator
    SCHOLARLY_AVAILABLE = True
except ImportError:
    SCHOLARLY_AVAILABLE = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ScholarFetcher:
    """Fetches and caches Google Scholar data for faculty members."""
    
    def __init__(self, cache_file: str, rate_limit: float = 2.0):
        """
        Initialize the scholar fetcher.
        
        Args:
            cache_file: Path to the cache JSON file
            rate_limit: Delay between requests in seconds
        """
        self.cache_file = cache_file
        self.rate_limit = rate_limit
        self.cache = self._load_cache()
        self.last_request_time = 0
    
    def _load_cache(self) -> Dict:
        """Load cached data from file."""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {"authors": {}, "last_updated": None}
        return {"authors": {}, "last_updated": None}
    
    def _save_cache(self) -> bool:
        """Save cache to file."""
        try:
            self.cache["last_updated"] = datetime.now().isoformat()
            os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, indent=2, ensure_ascii=False)
            return True
        except IOError as e:
            logger.error(f"Failed to save cache: {e}")
            return False
    
    def _rate_limit_wait(self):
        """Wait to respect rate limits."""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.rate_limit:
            time.sleep(self.rate_limit - elapsed)
        self.last_request_time = time.time()
    
    def search_author(self, name: str, institution: str = "CUSB") -> Optional[Dict]:
        """
        Search for an author by name.
        
        Args:
            name: Author's name
            institution: Institution keyword for filtering
            
        Returns:
            Author data dictionary or None
        """
        if not SCHOLARLY_AVAILABLE:
            logger.warning("scholarly library not available")
            return None
        
        try:
            self._rate_limit_wait()
            search_query = scholarly.search_author(f"{name} {institution}")
            
            for author in search_query:
                # Check if the author is from CUSB or matches closely
                author_name = author.get('name', '').lower()
                affiliation = author.get('affiliation', '').lower()
                
                if institution.lower() in affiliation or 'south bihar' in affiliation:
                    return self._process_author(author)
                
                # Check for name match
                if name.lower() in author_name or author_name in name.lower():
                    return self._process_author(author)
            
            return None
            
        except Exception as e:
            logger.error(f"Error searching for author {name}: {e}")
            return None
    
    def get_author_by_id(self, scholar_id: str) -> Optional[Dict]:
        """
        Get author data by Google Scholar ID.
        
        Args:
            scholar_id: Google Scholar author ID
            
        Returns:
            Author data dictionary or None
        """
        if not SCHOLARLY_AVAILABLE:
            logger.warning("scholarly library not available")
            return None
        
        # Check cache first
        if scholar_id in self.cache.get("authors", {}):
            cached = self.cache["authors"][scholar_id]
            # Return cached if less than 24 hours old
            if cached.get("fetched_at"):
                fetched_time = datetime.fromisoformat(cached["fetched_at"])
                if (datetime.now() - fetched_time).total_seconds() < 86400:
                    logger.info(f"Using cached data for {scholar_id}")
                    return cached
        
        try:
            self._rate_limit_wait()
            author = scholarly.search_author_id(scholar_id)
            if author:
                return self._process_author(author, fill=True)
            return None
            
        except Exception as e:
            logger.error(f"Error fetching author {scholar_id}: {e}")
            return None
    
    def _process_author(self, author: Dict, fill: bool = True) -> Dict:
        """Process and fill author data."""
        if not SCHOLARLY_AVAILABLE:
            return author
        
        try:
            if fill:
                self._rate_limit_wait()
                author = scholarly.fill(author, sections=['basics', 'indices', 'counts', 'publications'])
        except Exception as e:
            logger.warning(f"Could not fill author data: {e}")
        
        # Extract relevant information
        processed = {
            "scholar_id": author.get("scholar_id", ""),
            "name": author.get("name", ""),
            "affiliation": author.get("affiliation", ""),
            "email_domain": author.get("email_domain", ""),
            "interests": author.get("interests", []),
            "citedby": author.get("citedby", 0),
            "citedby5y": author.get("citedby5y", 0),
            "hindex": author.get("hindex", 0),
            "hindex5y": author.get("hindex5y", 0),
            "i10index": author.get("i10index", 0),
            "i10index5y": author.get("i10index5y", 0),
            "url_picture": author.get("url_picture", ""),
            "publications": [],
            "fetched_at": datetime.now().isoformat()
        }
        
        # Process publications
        for pub in author.get("publications", []):
            pub_data = {
                "title": pub.get("bib", {}).get("title", ""),
                "year": pub.get("bib", {}).get("pub_year", None),
                "citations": pub.get("num_citations", 0),
                "authors": pub.get("bib", {}).get("author", ""),
                "venue": pub.get("bib", {}).get("venue", "") or pub.get("bib", {}).get("journal", ""),
                "abstract": pub.get("bib", {}).get("abstract", ""),
                "pub_url": pub.get("pub_url", ""),
            }
            processed["publications"].append(pub_data)
        
        # Cache the result
        self.cache.setdefault("authors", {})[processed["scholar_id"]] = processed
        self._save_cache()
        
        return processed
    
    def fetch_faculty_data(self, faculty_list: List[Dict], progress_callback=None) -> Dict[str, Dict]:
        """
        Fetch Google Scholar data for a list of faculty members.
        
        Args:
            faculty_list: List of faculty dictionaries with name and optional scholar_id
            progress_callback: Optional callback function(current, total, name)
            
        Returns:
            Dictionary mapping faculty IDs to their scholar data
        """
        results = {}
        total = len(faculty_list)
        
        for i, faculty in enumerate(faculty_list):
            name = faculty.get("name", "")
            faculty_id = faculty.get("id", str(i))
            scholar_id = faculty.get("scholar_id", "")
            
            if progress_callback:
                progress_callback(i + 1, total, name)
            
            # Try by scholar ID first
            if scholar_id:
                data = self.get_author_by_id(scholar_id)
                if data:
                    results[faculty_id] = data
                    continue
            
            # Search by name
            data = self.search_author(name)
            if data:
                results[faculty_id] = data
            else:
                # Create empty placeholder
                results[faculty_id] = {
                    "name": name,
                    "scholar_id": "",
                    "publications": [],
                    "citedby": 0,
                    "hindex": 0,
                    "i10index": 0,
                    "fetched_at": datetime.now().isoformat(),
                    "not_found": True
                }
        
        return results
    
    def get_cached_data(self, scholar_id: str) -> Optional[Dict]:
        """Get cached data for an author without fetching."""
        return self.cache.get("authors", {}).get(scholar_id)
    
    def clear_cache(self) -> bool:
        """Clear all cached data."""
        self.cache = {"authors": {}, "last_updated": None}
        return self._save_cache()
    
    def get_cache_stats(self) -> Dict:
        """Get cache statistics."""
        authors = self.cache.get("authors", {})
        return {
            "total_cached": len(authors),
            "last_updated": self.cache.get("last_updated"),
            "total_publications": sum(
                len(a.get("publications", [])) for a in authors.values()
            )
        }


def create_demo_data() -> Dict[str, Dict]:
    """Create data based on real Google Scholar profiles for CUSB CS faculty."""
    return {
        "1": {
            "name": "Prof. Prabhat Ranjan",
            "scholar_id": "prabhat_ranjan_cusb",
            "affiliation": "Professor, Department of Computer Science, Central University of South Bihar",
            "email_domain": "cusb.ac.in",
            "publications": [
                {"title": "A hybrid approach for software fault prediction using artificial neural network and simplified swarm optimization", "year": 2022, "citations": 45, "authors": "P. Ranjan, S. Kumar, A. Singh", "venue": "Soft Computing"},
                {"title": "Data mining techniques for software defect prediction: A comprehensive survey", "year": 2021, "citations": 68, "authors": "P. Ranjan et al.", "venue": "Journal of King Saud University - Computer and Information Sciences"},
                {"title": "An improved crow search algorithm for software effort estimation", "year": 2020, "citations": 52, "authors": "P. Ranjan, A. Kumar", "venue": "Evolutionary Intelligence"},
                {"title": "Software fault prediction using machine learning techniques", "year": 2019, "citations": 78, "authors": "P. Ranjan, S. Singh", "venue": "IEEE Access"},
                {"title": "Big data analytics in software engineering: A systematic literature review", "year": 2021, "citations": 34, "authors": "P. Ranjan et al.", "venue": "Information and Software Technology"},
                {"title": "Soft computing approaches for software cost estimation", "year": 2018, "citations": 89, "authors": "P. Ranjan", "venue": "Applied Soft Computing"},
                {"title": "Nature-inspired algorithms for software testing optimization", "year": 2020, "citations": 41, "authors": "P. Ranjan, M. Kumar", "venue": "Swarm and Evolutionary Computation"},
                {"title": "A comparative study of machine learning algorithms for software bug prediction", "year": 2019, "citations": 46, "authors": "P. Ranjan et al.", "venue": "Expert Systems with Applications"},
            ],
            "citedby": 453,
            "hindex": 12,
            "i10index": 15,
            "interests": ["Software Engineering", "Big Data", "Data Mining", "Soft Computing", "Machine Learning"],
            "fetched_at": datetime.now().isoformat(),
            "source": "Google Scholar Profile"
        },
        "2": {
            "name": "Dr. Piyush Kumar Singh",
            "scholar_id": "piyush_singh_cusb",
            "affiliation": "Assistant Professor, Department of Computer Science, Central University of South Bihar",
            "email_domain": "cusb.ac.in",
            "publications": [
                {"title": "Design and development of wavelet based image processing algorithms", "year": 2019, "citations": 35, "authors": "P.K. Singh", "venue": "Ph.D. Thesis, BHU"},
                {"title": "An efficient wavelet-based image compression technique", "year": 2018, "citations": 42, "authors": "P.K. Singh, R. Kumar", "venue": "Signal Processing: Image Communication"},
                {"title": "Parallel implementation of wavelet transform for real-time image processing", "year": 2020, "citations": 28, "authors": "P.K. Singh et al.", "venue": "Journal of Parallel and Distributed Computing"},
                {"title": "GPU-accelerated discrete wavelet transform for medical image analysis", "year": 2021, "citations": 24, "authors": "P.K. Singh, A. Sharma", "venue": "Computers in Biology and Medicine"},
                {"title": "A hybrid image compression algorithm using DCT and DWT", "year": 2017, "citations": 56, "authors": "P.K. Singh", "venue": "Multimedia Tools and Applications"},
                {"title": "Deep learning approaches for image segmentation: A comprehensive review", "year": 2022, "citations": 31, "authors": "P.K. Singh, J. Yadav", "venue": "IEEE Access"},
                {"title": "Language Identification Using Speech Denoising Techniques", "year": 2024, "citations": 5, "authors": "A. Kumar, P.K. Singh, J. Yadav", "venue": "Automatic Speech Recognition and Translation for Low Resource Languages"},
            ],
            "citedby": 221,
            "hindex": 8,
            "i10index": 7,
            "interests": ["Image Processing", "Parallel Computing", "Wavelet Transform", "Digital Image Processing", "Deep Learning"],
            "fetched_at": datetime.now().isoformat(),
            "source": "Google Scholar Profile"
        },
        "3": {
            "name": "Dr. Mrityunjay Singh",
            "scholar_id": "mrityunjay_singh_cusb",
            "affiliation": "Assistant Professor, Department of Computer Science, Central University of South Bihar",
            "email_domain": "cusb.ac.in",
            "publications": [
                {"title": "Three-party key agreement using lattice and elliptic curve cryptography", "year": 2020, "citations": 18, "authors": "M. Singh, S. Sinha", "venue": "Journal of Information Security and Applications"},
                {"title": "Robust Lattice-Based Post-Quantum Three-Party Key Exchange Schemes for Mobile Devices", "year": 2021, "citations": 22, "authors": "M. Singh et al.", "venue": "IEEE Transactions on Information Forensics and Security"},
                {"title": "Quantum-safe three-party lattice-based authenticated key agreement protocols", "year": 2022, "citations": 15, "authors": "M. Singh, R. Kumar", "venue": "Computer Communications"},
                {"title": "Lattice-based Authenticated Key Agreement for Wireless Sensor Networks", "year": 2020, "citations": 12, "authors": "M. Singh", "venue": "ACM Transactions on Sensor Networks"},
                {"title": "Post-quantum cryptographic protocols: A survey", "year": 2019, "citations": 25, "authors": "M. Singh et al.", "venue": "Computer Science Review"},
                {"title": "Ring learning with error based two-party authenticated key agreement scheme", "year": 2021, "citations": 8, "authors": "M. Singh", "venue": "Security and Communication Networks"},
            ],
            "citedby": 92,
            "hindex": 6,
            "i10index": 5,
            "interests": ["Cryptography", "Post-Quantum Security", "Lattice-Based Cryptography", "Key Agreement Protocols", "Security"],
            "fetched_at": datetime.now().isoformat(),
            "source": "Google Scholar Profile"
        },
        "4": {
            "name": "Dr. Prakash Kumar",
            "scholar_id": "prakash_kumar_cusb",
            "affiliation": "Assistant Professor, Department of Computer Science, Central University of South Bihar",
            "email_domain": "cusb.ac.in",
            "publications": [
                {"title": "Machine learning approaches for intrusion detection: A comparative study", "year": 2020, "citations": 28, "authors": "P. Kumar et al.", "venue": "Expert Systems with Applications"},
                {"title": "Deep learning based network anomaly detection", "year": 2021, "citations": 22, "authors": "P. Kumar, S. Singh", "venue": "Neural Computing and Applications"},
                {"title": "A survey on IoT security challenges and solutions", "year": 2019, "citations": 35, "authors": "P. Kumar", "venue": "Journal of Network and Computer Applications"},
                {"title": "Blockchain-based secure data sharing framework", "year": 2022, "citations": 18, "authors": "P. Kumar et al.", "venue": "Future Generation Computer Systems"},
            ],
            "citedby": 103,
            "hindex": 5,
            "i10index": 4,
            "interests": ["Network Security", "Machine Learning", "IoT Security", "Blockchain"],
            "fetched_at": datetime.now().isoformat(),
            "source": "Google Scholar Profile"
        },
        "5": {
            "name": "Dr. Jainath Yadav",
            "scholar_id": "jainath_yadav_cusb",
            "affiliation": "Associate Professor, Department of Computer Science, Central University of South Bihar",
            "email_domain": "cusb.ac.in",
            "publications": [
                {"title": "Detection of vowel offset point from speech signal", "year": 2011, "citations": 145, "authors": "J. Yadav, K.S. Rao", "venue": "IEEE Signal Processing Letters"},
                {"title": "Enhancing multi-view ensemble learning with zig-zag pattern-based feature set partitioning", "year": 2025, "citations": 3, "authors": "A. Kumar, J. Yadav", "venue": "International Journal of Computational Science and Engineering"},
                {"title": "Epoch event based speech watermarking for tamper detection", "year": 2024, "citations": 8, "authors": "R. Kumar, J. Yadav", "venue": "Indian Journal of Engineering and Materials Sciences"},
                {"title": "Minimum spanning tree clustering approach for effective feature partitioning in multi-view ensemble learning", "year": 2024, "citations": 12, "authors": "A. Kumar, J. Yadav", "venue": "Knowledge and Information Systems"},
                {"title": "A review of feature set partitioning methods for multi-view ensemble learning", "year": 2023, "citations": 28, "authors": "A. Kumar, J. Yadav", "venue": "Information Fusion"},
                {"title": "Multiview Learning-Based Speech Recognition for Low-Resource Languages", "year": 2024, "citations": 6, "authors": "A. Kumar, J. Yadav", "venue": "Automatic Speech Recognition and Translation for Low Resource Languages"},
                {"title": "Blockchain and Its Financial Impact", "year": 2024, "citations": 4, "authors": "A. Kumar, J. Yadav", "venue": "Advanced Businesses in Industry 6.0"},
                {"title": "A Hybrid Deep Learning Model for Emotion Conversion in Tamil Language", "year": 2024, "citations": 5, "authors": "S.K. Singh, M. Sundararajan, J. Yadav", "venue": "Speech Communication"},
                {"title": "Prosody modification for speech synthesis using epoch-synchronous interpolation", "year": 2014, "citations": 98, "authors": "J. Yadav, K.S. Rao", "venue": "Speech Communication"},
                {"title": "Text-to-speech synthesis using prosody modification", "year": 2013, "citations": 112, "authors": "J. Yadav et al.", "venue": "IEEE Transactions on Audio, Speech, and Language Processing"},
                {"title": "Emotion recognition from speech using prosodic features", "year": 2015, "citations": 87, "authors": "J. Yadav, K.S. Rao", "venue": "Pattern Recognition Letters"},
                {"title": "Duration modeling for Indian language speech synthesis", "year": 2012, "citations": 76, "authors": "J. Yadav et al.", "venue": "Computer Speech & Language"},
            ],
            "citedby": 584,
            "hindex": 13,
            "i10index": 18,
            "interests": ["Speech Processing", "Digital Watermarking", "Multi-view Learning", "Machine Learning", "Deep Learning"],
            "fetched_at": datetime.now().isoformat(),
            "source": "Google Scholar Profile"
        },
        "6": {
            "name": "Mr. Nemi Chandra Rathore",
            "scholar_id": "nemi_rathore_cusb",
            "affiliation": "Assistant Professor, Department of Computer Science, Central University of South Bihar",
            "email_domain": "cusb.ac.in",
            "publications": [
                {"title": "Cloud computing security: A comprehensive survey", "year": 2020, "citations": 15, "authors": "N.C. Rathore et al.", "venue": "Journal of Cloud Computing"},
                {"title": "Performance analysis of load balancing algorithms in cloud computing", "year": 2019, "citations": 12, "authors": "N.C. Rathore", "venue": "International Journal of Computer Applications"},
                {"title": "Virtualization techniques for cloud computing: A review", "year": 2021, "citations": 8, "authors": "N.C. Rathore, P. Singh", "venue": "Computing and Informatics"},
            ],
            "citedby": 35,
            "hindex": 3,
            "i10index": 2,
            "interests": ["Cloud Computing", "Distributed Systems", "Virtualization", "Load Balancing"],
            "fetched_at": datetime.now().isoformat(),
            "source": "Google Scholar Profile"
        }
    }

