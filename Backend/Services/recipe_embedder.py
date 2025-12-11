import os
# CRITICAL: Disable onnxruntime BEFORE importing sentence_transformers AND chromadb
# onnxruntime 1.23.2 is built for macOS 13.4+ and incompatible with macOS 13.2.1
os.environ['DISABLE_ONNXRUNTIME_OPTIMIZATION'] = '1'
os.environ['TOKENIZERS_PARALLELISM'] = 'false'
# Tell ChromaDB to NOT use onnxruntime
os.environ['CHROMA_ONNX_PROVIDER'] = 'none'

from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings
from typing import List, Dict, Optional

class RecipeVectorStore:
    """Manages recipe embeddings in ChromaDB using free embedding model"""
    
    def __init__(self):
        # Initialize free embedding model (all-MiniLM-L6-v2 - fast and good quality)
        print("Loading embedding model...")
        # Force PyTorch backend only (no ONNX optimization)
        self.embedding_model = SentenceTransformer(
            'all-MiniLM-L6-v2',
            device='cpu',
            backend='torch'  # Explicitly use PyTorch backend
        )
        
        # Initialize ChromaDB with persistent storage
        chroma_dir = os.path.join(os.path.dirname(__file__), '../../chroma_db')
        os.makedirs(chroma_dir, exist_ok=True)
        
        # CRITICAL: Configure ChromaDB to NOT use onnxruntime
        self.chroma_client = chromadb.PersistentClient(
            path=chroma_dir,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Create or get collection
        # CRITICAL: Set embedding_function=None to prevent ChromaDB from using
        # its default ONNXMiniLM_L6_V2 which requires the broken onnxruntime
        # We provide embeddings manually using our SentenceTransformer
        self.collection = self.chroma_client.get_or_create_collection(
            name="recipes",
            metadata={"description": "Recipe embeddings for meal planning"},
            embedding_function=None  # Don't use ChromaDB's default ONNX embedder
        )
        
        print(f"✅ ChromaDB initialized. Current recipe count: {self.collection.count()}")
    
    def is_empty(self) -> bool:
        """Check if vector database is empty"""
        return self.collection.count() == 0
    
    def add_recipes(self, recipes: List[Dict]):
        """Add recipes to vector database"""
        if not recipes:
            print("No recipes to add")
            return
        
        print(f"Embedding {len(recipes)} recipes...")
        
        embeddings = []
        documents = []
        metadatas = []
        ids = []
        
        for recipe in recipes:
            # Create rich text representation for embedding
            text = self._create_embedding_text(recipe)
            
            # Generate embedding
            embedding = self.embedding_model.encode(text).tolist()
            
            embeddings.append(embedding)
            documents.append(text)
            ids.append(recipe["id"])
            
            metadatas.append({
                "recipe_id": recipe["id"],
                "name": recipe["name"],
                "cuisine": recipe["cuisine"],
                "source": recipe["source"],
                "calories": float(recipe["nutrition"]["calories"]),
                "protein": float(recipe["nutrition"]["protein"]),
                "carbs": float(recipe["nutrition"]["carbs"]),
                "fat": float(recipe["nutrition"]["fat"]),
                "tags": ",".join(recipe.get("tags", []))
            })
        
        # Add to ChromaDB
        self.collection.add(
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        
        print(f"✅ Added {len(recipes)} recipes to vector database")
    
    def _create_embedding_text(self, recipe: Dict) -> str:
        """Create rich text representation for better embeddings"""
        ingredients_text = ', '.join(recipe.get('ingredients', [])[:10])  # Limit to first 10
        tags_text = ', '.join(recipe.get('tags', []))
        
        return f"""
        Recipe: {recipe['name']}
        Cuisine: {recipe['cuisine']}
        Description: {recipe.get('description', '')}
        Ingredients: {ingredients_text}
        Nutrition: {recipe['nutrition']['calories']} calories, 
                  {recipe['nutrition']['protein']}g protein,
                  {recipe['nutrition']['carbs']}g carbs,
                  {recipe['nutrition']['fat']}g fat
        Tags: {tags_text}
        """
    
    def search_by_goals_and_taste(
        self, 
        goal: str,
        preferences: Optional[List[str]] = None,
        allergies: Optional[List[str]] = None,
        n_results: int = 15
    ) -> List[Dict]:
        """
        Search recipes by BOTH goals (nutrition) and taste (preferences)
        """
        if self.collection.count() == 0:
            print("⚠️  Vector database is empty. Run seed script first.")
            return []
        
        # Build query text
        query_text = self._build_query_text(goal, preferences or [])
        
        # CRITICAL: Generate query embedding using our SentenceTransformer
        # Can't use query_texts= because embedding_function=None
        query_embedding = self.embedding_model.encode(query_text).tolist()
        
        # Build filters for nutrition goals
        filters = self._build_nutrition_filters(goal, preferences)
        
        try:
            # Search using query_embeddings instead of query_texts
            results = self.collection.query(
                query_embeddings=[query_embedding],  # Use our embeddings, not ChromaDB's ONNX
                n_results=min(n_results * 2, self.collection.count()),
                where=filters if filters else None
            )
            
            # Filter out allergies
            filtered_results = self._filter_allergies(results, allergies or [])
            
            return filtered_results[:n_results]
        except Exception as e:
            print(f"Error searching: {e}")
            # Fallback: search without filters
            try:
                results = self.collection.query(
                    query_embeddings=[query_embedding],  # Use our embeddings here too
                    n_results=min(n_results * 2, self.collection.count())
                )
                filtered_results = self._filter_allergies(results, allergies or [])
                return filtered_results[:n_results]
            except Exception as e2:
                print(f"Error in fallback search: {e2}")
                return []
    
    def _build_query_text(self, goal: str, preferences: List[str]) -> str:
        """Build query text combining goals and preferences"""
        goal_descriptions = {
            "lose_fat": "low calorie, high protein, low carb, healthy fats, weight loss",
            "gain_muscle": "high protein, moderate carbs, nutrient dense, muscle building",
            "maintain": "balanced nutrition, moderate calories, healthy eating"
        }
        
        query = goal_descriptions.get(goal, "balanced nutrition")
        if preferences:
            query += f" {' '.join(preferences)} cuisine"
        
        return query
    
    def _build_nutrition_filters(self, goal: str, preferences: Optional[List[str]] = None) -> Optional[Dict]:
        """
        Build simple nutrition filters based on goal
        ChromaDB 0.3.23 has limited query support - using single conditions only
        """
        # Use simple filters that ChromaDB 0.3.23 can handle
        if goal == "lose_fat":
            filter_dict = {"calories": {"$lt": 600}}
        elif goal == "gain_muscle":
            filter_dict = {"protein": {"$gt": 25}}
        else:  # maintain
            filter_dict = {"calories": {"$gte": 200}}
        
        # Add cuisine preference if provided (but separately, not nested)
        if preferences and len(preferences) > 0:
            # For ChromaDB 0.3.23, we can't combine $and with $in easily
            # So we'll rely on semantic search for cuisine matching
            pass
        
        return filter_dict
    
    def _filter_allergies(self, results: Dict, allergies: List[str]) -> List[Dict]:
        """Filter out recipes with allergens"""
        if not allergies or not results["metadatas"]:
            return results["metadatas"][0] if results["metadatas"] else []
        
        filtered = []
        for metadata, document in zip(results["metadatas"][0], results["documents"][0]):
            # Check if any allergen is in the recipe
            has_allergen = any(
                allergen.lower() in document.lower() 
                for allergen in allergies
            )
            if not has_allergen:
                filtered.append(metadata)
        
        return filtered
    
    def get_recipe_count(self) -> int:
        """Get total number of recipes in vector database"""
        return self.collection.count()
    
    def clear_all(self):
        """Clear all recipes from vector database (use with caution!)"""
        self.chroma_client.delete_collection("recipes")
        self.collection = self.chroma_client.get_or_create_collection(
            name="recipes",
            metadata={"description": "Recipe embeddings for meal planning"}
        )
        print("✅ Vector database cleared")
