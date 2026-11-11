"""
Tests for ETL Pipeline Transformation Utilities

Basic tests for the transformation utilities and place normalization.
"""
import sys
import os
import unittest

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


class TestNormalizePlaces(unittest.TestCase):
    """Tests for place normalization functions."""
    
    def test_normalizar_lugar_basic(self):
        """Test basic title case normalization."""
        from normalization.normalize_places import normalizar_lugar
        
        result = normalizar_lugar("madrid")
        self.assertEqual(result, "Madrid")
    
    def test_normalizar_lugar_semicolon(self):
        """Test semicolon-separated places."""
        from normalization.normalize_places import normalizar_lugar
        
        result = normalizar_lugar("madrid;españa")
        self.assertEqual(result, "Madrid; España")
    
    def test_normalizar_lugar_whitespace(self):
        """Test whitespace handling."""
        from normalization.normalize_places import normalizar_lugar
        
        result = normalizar_lugar("  madrid  ;  españa  ")
        self.assertEqual(result, "Madrid; España")
    
    def test_normalizar_lugar_known_mapping(self):
        """Test known place mappings."""
        from normalization.normalize_places import normalizar_lugar
        
        result = normalizar_lugar("usa")
        self.assertEqual(result, "Estados Unidos")


class TestTransformationUtils(unittest.TestCase):
    """Tests for transformation utility functions."""
    
    def test_hash_sha256_deterministic(self):
        """Test that hash_sha256 is deterministic."""
        from transformation.utils import hash_sha256
        
        result1 = hash_sha256("test data")
        result2 = hash_sha256("test data")
        self.assertEqual(result1, result2)
    
    def test_hash_sha256_different_input(self):
        """Test that different inputs produce different hashes."""
        from transformation.utils import hash_sha256
        
        result1 = hash_sha256("test data 1")
        result2 = hash_sha256("test data 2")
        self.assertNotEqual(result1, result2)
    
    def test_validar_fecha_valid(self):
        """Test valid date parsing."""
        from transformation.utils import validar_fecha
        
        result = validar_fecha("2023-05-15")
        self.assertIsNotNone(result)
        self.assertEqual(result.year, 2023)
        self.assertEqual(result.month, 5)
        self.assertEqual(result.day, 15)
    
    def test_validar_fecha_invalid(self):
        """Test invalid date returns None."""
        from transformation.utils import validar_fecha
        
        result = validar_fecha("not-a-date")
        self.assertIsNone(result)
    
    def test_validar_fecha_null_date(self):
        """Test null date (0001-01-01) returns None."""
        from transformation.utils import validar_fecha
        
        result = validar_fecha("0001-01-01")
        self.assertIsNone(result)
    
    def test_is_valid_url(self):
        """Test URL validation."""
        from transformation.utils import is_valid_url
        
        self.assertTrue(is_valid_url("https://example.com"))
        self.assertTrue(is_valid_url("http://test.org/path"))
        self.assertFalse(is_valid_url("not a url"))
        self.assertFalse(is_valid_url("ftp://invalid.com"))
    
    def test_is_valid_name(self):
        """Test name validation."""
        from transformation.utils import is_valid_name
        
        self.assertTrue(is_valid_name("John Doe"))
        self.assertFalse(is_valid_name(None))
        self.assertFalse(is_valid_name("None"))
        self.assertFalse(is_valid_name("Sin determinar"))
    
    def test_parse_lugar(self):
        """Test place parts parsing."""
        from transformation.utils import parse_lugar
        
        ciudad, estado, pais = parse_lugar("Madrid;Comunidad de Madrid;España")
        self.assertEqual(ciudad, "Madrid")
        self.assertEqual(estado, "Comunidad de Madrid")
        self.assertEqual(pais, "España")


class TestRdfBuilder(unittest.TestCase):
    """Tests for RDF builder module."""
    
    def test_get_ontology_class_institution(self):
        """Test institution type mapping."""
        from transformation.rdf_builder import get_ontology_class
        
        result = get_ontology_class("Museo")
        self.assertEqual(result, "Museum")
    
    def test_get_ontology_class_exhibition(self):
        """Test exhibition type mapping."""
        from transformation.rdf_builder import get_ontology_class
        
        result = get_ontology_class("Exposición")
        self.assertEqual(result, "Exhibition")
    
    def test_get_ontology_class_unknown(self):
        """Test unknown type returns None."""
        from transformation.rdf_builder import get_ontology_class
        
        result = get_ontology_class("UnknownType")
        self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()
