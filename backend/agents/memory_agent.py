import sqlite3
import json
from typing import Dict, Any, List, Optional
import faiss
import numpy as np
from .base_agent import BaseAgent

class MemoryAgent(BaseAgent):
    def __init__(self, event_bus, settings):
        super().__init__("MemoryAgent", event_bus)
        self.vector_dim = settings.VECTOR_DIM
        self.vector_db = faiss.IndexFlatL2(self.vector_dim)
        self.sql_db = self._initialize_database(settings.SQLITE_DB_PATH)
        
        # Subscribe to memory update events
        self.subscribe("update_memory")

    def _initialize_database(self, db_path: str) -> sqlite3.Connection:
        """Initialize SQLite database with complete schema"""
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create features table with all required fields
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS features (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                status TEXT DEFAULT 'draft',
                priority TEXT,
                requirements TEXT,
                feedback TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create dependencies table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS dependencies (
                id INTEGER PRIMARY KEY,
                feature_id INTEGER,
                description TEXT,
                type TEXT,
                status TEXT DEFAULT 'pending',
                FOREIGN KEY(feature_id) REFERENCES features(id)
            )
        """)
        
        # Create research_data table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS research_data (
                id INTEGER PRIMARY KEY,
                query TEXT,
                findings TEXT,
                sources TEXT,
                relevance_score REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create validation_results table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS validation_results (
                id INTEGER PRIMARY KEY,
                feature_id INTEGER,
                rule_name TEXT,
                score REAL,
                feedback TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(feature_id) REFERENCES features(id)
            )
        """)
        
        conn.commit()
        return conn

    def store_feature(self, feature: Dict[str, Any]) -> int:
        """Store or update a feature with all its attributes"""
        cursor = self.sql_db.cursor()
        
        # Convert lists to JSON strings
        requirements = json.dumps(feature.get('requirements', []))
        
        if 'id' in feature:
            # Update existing feature
            cursor.execute("""
                UPDATE features 
                SET name=?, description=?, status=?, priority=?, 
                    requirements=?, feedback=?, updated_at=CURRENT_TIMESTAMP
                WHERE id=?
            """, (
                feature['name'], feature['description'], feature['status'],
                feature['priority'], requirements, feature.get('feedback'),
                feature['id']
            ))
            feature_id = feature['id']
        else:
            # Insert new feature
            cursor.execute("""
                INSERT INTO features (name, description, status, priority, requirements, feedback)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                feature['name'], feature['description'], feature['status'],
                feature['priority'], requirements, feature.get('feedback')
            ))
            feature_id = cursor.lastrowid
        
        # Handle dependencies
        if 'dependencies' in feature:
            for dep in feature['dependencies']:
                cursor.execute("""
                    INSERT INTO dependencies (feature_id, description, type)
                    VALUES (?, ?, ?)
                """, (feature_id, dep, 'technical'))
        
        self.sql_db.commit()
        return feature_id

    def store_validation_result(self, feature_id: int, validation: Dict[str, Any]):
        """Store validation results"""
        cursor = self.sql_db.cursor()
        cursor.execute("""
            INSERT INTO validation_results (feature_id, rule_name, score, feedback)
            VALUES (?, ?, ?, ?)
        """, (
            feature_id,
            validation['rule'],
            validation['score'],
            validation['feedback']
        ))
        self.sql_db.commit()

    def get_feature_with_dependencies(self, feature_id: int) -> Dict[str, Any]:
        """Retrieve a feature with its dependencies"""
        cursor = self.sql_db.cursor()
        
        # Get feature
        cursor.execute("SELECT * FROM features WHERE id = ?", (feature_id,))
        feature_row = cursor.fetchone()
        
        if not feature_row:
            return None
        
        # Get dependencies
        cursor.execute("SELECT description FROM dependencies WHERE feature_id = ?", (feature_id,))
        dependencies = [row[0] for row in cursor.fetchall()]
        
        # Convert row to dict
        feature = {
            'id': feature_row[0],
            'name': feature_row[1],
            'description': feature_row[2],
            'status': feature_row[3],
            'priority': feature_row[4],
            'requirements': json.loads(feature_row[5]) if feature_row[5] else [],
            'feedback': feature_row[6],
            'dependencies': dependencies
        }
        
        return feature

    def handle_event(self, event):
        if event.type == 'update_memory':
            self.store(event.data)

    def store(self, data: dict):
        # Store embeddings in FAISS
        if 'text' in data:
            embedding = self._generate_embedding(data['text'])
            self.vector_db.add(np.array([embedding]).astype('float32'))

        # Store metadata in SQLite
        cursor = self.sql_db.cursor()
        cursor.execute(
            "INSERT INTO features (name, description, status) VALUES (?, ?, ?)",
            (data.get('name', ''), data.get('text', ''), data.get('status', 'active'))
        )
        self.sql_db.commit()

        # Notify other agents of the update
        self.publish('memory_updated', data)

    def _generate_embedding(self, text: str) -> np.ndarray:
        # TODO: Replace with actual embedding model
        # This is a temporary implementation for testing
        padding = [0] * self.vector_dim
        for i, char in enumerate(text[:self.vector_dim]):
            padding[i] = float(ord(char)) / 255.0
        return np.array(padding, dtype='float32')

    def search_similar(self, query: str, k: int = 5):
        query_embedding = self._generate_embedding(query)
        distances, indices = self.vector_db.search(
            np.array([query_embedding]).astype('float32'), k
        )
        return distances, indices

    def __del__(self):
        self.sql_db.close() 