import sqlite3
import json
import logging
from typing import Dict, List, Optional
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CollegeDatabase:
    def __init__(self, db_path: str = "college_cutoffs.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create colleges table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS colleges (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        college_code TEXT UNIQUE NOT NULL,
                        college_name TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Create branches table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS branches (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        college_id INTEGER NOT NULL,
                        branch_code TEXT NOT NULL,
                        branch_name TEXT NOT NULL,
                        status TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (college_id) REFERENCES colleges (id),
                        UNIQUE(college_id, branch_code)
                    )
                ''')
                
                # Create cutoff_data table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS cutoff_data (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        branch_id INTEGER NOT NULL,
                        stage TEXT NOT NULL,
                        category TEXT NOT NULL,
                        rank INTEGER NOT NULL,
                        percentage REAL NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (branch_id) REFERENCES branches (id),
                        UNIQUE(branch_id, stage, category)
                    )
                ''')
                
                # Create indexes for better performance
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_college_code ON colleges(college_code)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_branch_code ON branches(branch_code)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_cutoff_branch ON cutoff_data(branch_id)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_cutoff_stage ON cutoff_data(stage)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_cutoff_category ON cutoff_data(category)')
                
                conn.commit()
                logger.info("Database initialized successfully")
                
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            raise
    
    def insert_college(self, college_code: str, college_name: str) -> Optional[int]:
        """Insert a new college and return its ID."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Check if college already exists
                cursor.execute('SELECT id FROM colleges WHERE college_code = ?', (college_code,))
                existing = cursor.fetchone()
                
                if existing:
                    # Update existing college
                    cursor.execute('''
                        UPDATE colleges 
                        SET college_name = ?, updated_at = CURRENT_TIMESTAMP 
                        WHERE college_code = ?
                    ''', (college_name, college_code))
                    college_id = existing[0]
                    logger.info(f"Updated existing college: {college_name}")
                else:
                    # Insert new college
                    cursor.execute('''
                        INSERT INTO colleges (college_code, college_name)
                        VALUES (?, ?)
                    ''', (college_code, college_name))
                    college_id = cursor.lastrowid
                    logger.info(f"Inserted new college: {college_name}")
                
                conn.commit()
                return college_id
                
        except Exception as e:
            logger.error(f"Error inserting college: {e}")
            return None
    
    def insert_branch(self, college_id: int, branch_code: str, branch_name: str, status: str) -> Optional[int]:
        """Insert a new branch and return its ID."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Check if branch already exists
                cursor.execute('''
                    SELECT id FROM branches 
                    WHERE college_id = ? AND branch_code = ?
                ''', (college_id, branch_code))
                existing = cursor.fetchone()
                
                if existing:
                    # Update existing branch
                    cursor.execute('''
                        UPDATE branches 
                        SET branch_name = ?, status = ?, updated_at = CURRENT_TIMESTAMP 
                        WHERE id = ?
                    ''', (branch_name, status, existing[0]))
                    branch_id = existing[0]
                    logger.info(f"Updated existing branch: {branch_name}")
                else:
                    # Insert new branch
                    cursor.execute('''
                        INSERT INTO branches (college_id, branch_code, branch_name, status)
                        VALUES (?, ?, ?, ?)
                    ''', (college_id, branch_code, branch_name, status))
                    branch_id = cursor.lastrowid
                    logger.info(f"Inserted new branch: {branch_name}")
                
                conn.commit()
                return branch_id
                
        except Exception as e:
            logger.error(f"Error inserting branch: {e}")
            return None
    
    def insert_cutoff_data(self, branch_id: int, stage: str, category: str, rank: int, percentage: float) -> bool:
        """Insert cutoff data for a branch."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Check if cutoff data already exists
                cursor.execute('''
                    SELECT id FROM cutoff_data 
                    WHERE branch_id = ? AND stage = ? AND category = ?
                ''', (branch_id, stage, category))
                existing = cursor.fetchone()
                
                if existing:
                    # Update existing cutoff data
                    cursor.execute('''
                        UPDATE cutoff_data 
                        SET rank = ?, percentage = ?, created_at = CURRENT_TIMESTAMP 
                        WHERE id = ?
                    ''', (rank, percentage, existing[0]))
                    logger.debug(f"Updated cutoff data: Stage {stage}, {category}")
                else:
                    # Insert new cutoff data
                    cursor.execute('''
                        INSERT INTO cutoff_data (branch_id, stage, category, rank, percentage)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (branch_id, stage, category, rank, percentage))
                    logger.debug(f"Inserted cutoff data: Stage {stage}, {category}")
                
                conn.commit()
                return True
                
        except Exception as e:
            logger.error(f"Error inserting cutoff data: {e}")
            return False
    
    def store_parsed_data(self, parsed_data: Dict) -> bool:
        """Store complete parsed data from PDF into database."""
        try:
            if not parsed_data.get("parsing_success"):
                logger.error("Cannot store data: parsing was not successful")
                return False
            
            colleges = parsed_data.get("colleges", [])
            
            if not colleges:
                logger.error("No colleges found in parsed data")
                return False
            
            logger.info(f"Storing data for {len(colleges)} colleges")
            
            total_stored = 0
            
            # Process each college
            for college in colleges:
                college_code = college.get("college_code")
                college_name = college.get("college_name")
                branches = college.get("branches", [])
                
                if not college_code or not college_name:
                    logger.warning(f"Skipping college with missing information: {college}")
                    continue
                
                logger.info(f"Processing college: {college_name} ({college_code})")
                
                # Insert college
                college_id = self.insert_college(college_code, college_name)
                if not college_id:
                    logger.error(f"Failed to insert college: {college_name}")
                    continue
                
                # Insert branches and cutoff data for this college
                for branch in branches:
                    branch_code = branch.get("branch_code")
                    branch_name = branch.get("branch_name")
                    status = branch.get("status", "Unknown")
                    cutoff_data = branch.get("cutoff_data", [])
                    
                    if not branch_code or not branch_name:
                        logger.warning(f"Skipping branch with missing information: {branch}")
                        continue
                    
                    # Insert branch
                    branch_id = self.insert_branch(college_id, branch_code, branch_name, status)
                    if not branch_id:
                        logger.error(f"Failed to insert branch: {branch_name}")
                        continue
                    
                    # Insert cutoff data for this branch
                    cutoff_count = 0
                    for cutoff in cutoff_data:
                        stage = cutoff.get("stage")
                        category = cutoff.get("category")
                        rank = cutoff.get("rank")
                        percentage = cutoff.get("percentage")
                        
                        if all([stage, category, rank is not None, percentage is not None]):
                            if self.insert_cutoff_data(branch_id, stage, category, rank, percentage):
                                cutoff_count += 1
                        else:
                            logger.warning(f"Skipping incomplete cutoff data: {cutoff}")
                    
                    logger.debug(f"Stored {cutoff_count} cutoff entries for branch {branch_name}")
                
                total_stored += 1
            
            logger.info(f"Successfully stored data for {total_stored} colleges")
            return total_stored > 0
            
        except Exception as e:
            logger.error(f"Error storing parsed data: {e}")
            return False
    
    def get_college_data(self, college_code: str = None, college_name: str = None) -> Optional[Dict]:
        """Retrieve college data with branches and cutoff information."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                if college_code:
                    cursor.execute('''
                        SELECT * FROM colleges WHERE college_code = ?
                    ''', (college_code,))
                elif college_name:
                    cursor.execute('''
                        SELECT * FROM colleges WHERE college_name LIKE ?
                    ''', (f'%{college_name}%',))
                else:
                    return None
                
                college = cursor.fetchone()
                if not college:
                    return None
                
                # Get branches
                cursor.execute('''
                    SELECT * FROM branches WHERE college_id = ?
                ''', (college['id'],))
                branches = cursor.fetchall()
                
                # Get cutoff data for each branch
                result = {
                    'college_code': college['college_code'],
                    'college_name': college['college_name'],
                    'branches': []
                }
                
                for branch in branches:
                    cursor.execute('''
                        SELECT * FROM cutoff_data WHERE branch_id = ?
                    ''', (branch['id'],))
                    cutoff_data = cursor.fetchall()
                    
                    branch_info = {
                        'branch_code': branch['branch_code'],
                        'branch_name': branch['branch_name'],
                        'status': branch['status'],
                        'cutoff_data': []
                    }
                    
                    for cutoff in cutoff_data:
                        branch_info['cutoff_data'].append({
                            'stage': cutoff['stage'],
                            'category': cutoff['category'],
                            'rank': cutoff['rank'],
                            'percentage': cutoff['percentage']
                        })
                    
                    result['branches'].append(branch_info)
                
                return result
                
        except Exception as e:
            logger.error(f"Error retrieving college data: {e}")
            return None
    
    def search_colleges(self, query: str) -> List[Dict]:
        """Search colleges by name or code."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT college_code, college_name FROM colleges 
                    WHERE college_name LIKE ? OR college_code LIKE ?
                ''', (f'%{query}%', f'%{query}%'))
                
                results = []
                for row in cursor.fetchall():
                    results.append({
                        'college_code': row['college_code'],
                        'college_name': row['college_name']
                    })
                
                return results
                
        except Exception as e:
            logger.error(f"Error searching colleges: {e}")
            return []
    
    def get_database_stats(self) -> Dict:
        """Get database statistics."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('SELECT COUNT(*) FROM colleges')
                college_count = cursor.fetchone()[0]
                
                cursor.execute('SELECT COUNT(*) FROM branches')
                branch_count = cursor.fetchone()[0]
                
                cursor.execute('SELECT COUNT(*) FROM cutoff_data')
                cutoff_count = cursor.fetchone()[0]
                
                return {
                    'colleges': college_count,
                    'branches': branch_count,
                    'cutoff_records': cutoff_count
                }
                
        except Exception as e:
            logger.error(f"Error getting database stats: {e}")
            return {}

# Usage example
if __name__ == "__main__":
    # Initialize database
    db = CollegeDatabase()
    
    # Example usage
    # stats = db.get_database_stats()
    # print(f"Database stats: {stats}")
