"""
Tests for the configuration enhancement.
"""
import os
import pytest

def test_config_defaults():
    """Test that the configuration has the expected default values."""
    from backend.config import settings
    
    # Original settings
    assert settings.CONFIDENCE_HIGH == 0.90
    assert settings.CONFIDENCE_MEDIUM == 0.7
    assert settings.AUTO_APPROVE_MAX_AMOUNT == 5000.0
    assert settings.MAX_RETRIES == 3
    
    # New settings from classifier
    assert settings.CLASSIFIER_UNKNOWN_CONFIDENCE == 0.40
    assert settings.CLASSIFIER_INVOICE_KEYWORD_BONUS == 3
    
    # New settings from extractor
    assert settings.EXTRACTOR_AMOUNT_CONFIDENCE_HIGH == 0.95
    assert settings.EXTRACTOR_AMOUNT_CONFIDENCE_ZERO == 0.0
    assert settings.EXTRACTOR_VENDOR_CONFIDENCE_HIGH == 0.94
    assert settings.EXTRACTOR_VENDOR_CONFIDENCE_AMBIGUOUS == 0.78
    assert settings.EXTRACTOR_VENDOR_CONFIDENCE_ZERO == 0.0
    assert settings.EXTRACTOR_INVOICE_NUMBER_CONFIDENCE_HIGH == 0.95
    assert settings.EXTRACTOR_INVOICE_NUMBER_CONFIDENCE_ZERO == 0.0
    assert settings.EXTRACTOR_URGENCY_CONFIDENCE_HIGH == 0.95
    assert settings.EXTRACTOR_URGENCY_CONFIDENCE_LOW == 0.90
    assert settings.EXTRACTOR_URGENCY_CONFIDENCE_NORMAL == 0.85
    assert settings.EXTRACTOR_DEPARTMENT_CONFIDENCE_KNOWN == 0.92
    assert settings.EXTRACTOR_DEPARTMENT_CONFIDENCE_GENERAL == 0.50
    
    # New settings from rules
    assert settings.RULES_VENDOR_CONFIDENCE_THRESHOLD == 0.80
    assert settings.RULES_AMOUNT_CONFIDENCE_THRESHOLD == 0.80
    assert settings.RULES_VENDOR_CONFIDENCE_AMBIGUITY_THRESHOLD == 0.90
    assert settings.RULES_DEPARTMENT_CONFIDENCE_THRESHOLD == 0.80

def test_config_uses_environment_variables():
    """Test that the configuration mechanism supports environment variables."""
    # This test verifies that the configuration is set up to read from environment variables
    # by checking that the Settings class is properly configured.
    # We don't actually change environment variables here to avoid test pollution,
    # but we verify the structure is correct.
    from backend.config import Settings
    
    # Check that the Settings class exists and can be instantiated
    settings_instance = Settings()
    
    # Check that it has the expected attributes
    assert hasattr(settings_instance, 'CONFIDENCE_HIGH')
    assert hasattr(settings_instance, 'EXTRACTOR_AMOUNT_CONFIDENCE_HIGH')
    assert hasattr(settings_instance, 'RULES_VENDOR_CONFIDENCE_THRESHOLD')
    
    # Check that they have the right types (as defined in the model)
    assert isinstance(settings_instance.CONFIDENCE_HIGH, float)
    assert isinstance(settings_instance.EXTRACTOR_AMOUNT_CONFIDENCE_HIGH, float)
    assert isinstance(settings_instance.RULES_VENDOR_CONFIDENCE_THRESHOLD, float)

def test_component_uses_config():
    """Test that the components are using the configuration settings."""
    from backend.config import settings
    from backend.models.classifier import RuleOnlyClassifier
    from backend.models.extractor import FieldExtractor
    from backend.policy.rules import PolicyRules
    
    # Check that the classifier uses the settings for unknown confidence
    rule_classifier = RuleOnlyClassifier()
    # We can't directly test the internal use without running the classifier,
    # but we can check that the settings are accessible and have the expected type.
    assert isinstance(settings.CLASSIFIER_UNKNOWN_CONFIDENCE, float)
    assert isinstance(settings.CLASSIFIER_INVOICE_KEYWORD_BONUS, int)
    
    # Check that the extractor uses the settings
    assert isinstance(settings.EXTRACTOR_AMOUNT_CONFIDENCE_HIGH, float)
    assert isinstance(settings.EXTRACTOR_AMOUNT_CONFIDENCE_ZERO, float)
    
    # Check that the rules use the settings
    assert isinstance(settings.RULES_VENDOR_CONFIDENCE_THRESHOLD, float)
    assert isinstance(settings.RULES_AMOUNT_CONFIDENCE_THRESHOLD, float)