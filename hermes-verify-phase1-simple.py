import os
import sys

# Set environment variables before importing any of our modules
os.environ['API_KEY_ADMIN'] = 'test-admin-key'
os.environ['API_KEY_OPERATOR'] = 'test-operator-key'
os.environ['API_KEY_VIEWER'] = 'test-viewer-key'
os.environ['DATABASE_URL'] = 'sqlite:///:memory:'

# Now insert the project root and import
sys.path.insert(0, '/d/Desertation/ai-workflow-automation')

def test_config():
    from backend.config import settings
    # Test defaults from the original config
    assert settings.CONFIDENCE_HIGH == 0.90, f"Expected CONFIDENCE_HIGH=0.90, got {settings.CONFIDENCE_HIGH}"
    assert settings.CONFIDENCE_MEDIUM == 0.70, f"Expected CONFIDENCE_MEDIUM=0.70, got {settings.CONFIDENCE_MEDIUM}"
    assert settings.AUTO_APPROVE_MAX_AMOUNT == 5000.0, f"Expected AUTO_APPROVE_MAX_AMOUNT=5000.0, got {settings.AUTO_APPROVE_MAX_AMOUNT}"
    assert settings.MAX_RETRIES == 3, f"Expected MAX_RETRIES=3, got {settings.MAX_RETRIES}"
    # Test new settings from classifier
    assert settings.CLASSIFIER_UNKNOWN_CONFIDENCE == 0.40, f"Expected CLASSIFIER_UNKNOWN_CONFIDENCE=0.40, got {settings.CLASSIFIER_UNKNOWN_CONFIDENCE}"
    assert settings.CLASSIFIER_INVOICE_KEYWORD_BONUS == 3, f"Expected CLASSIFIER_INVOICE_KEYWORD_BONUS=3, got {settings.CLASSIFIER_INVOICE_KEYWORD_BONUS}"
    # Test new settings from extractor
    assert settings.EXTRACTOR_AMOUNT_CONFIDENCE_HIGH == 0.95, f"Expected EXTRACTOR_AMOUNT_CONFIDENCE_HIGH=0.95, got {settings.EXTRACTOR_AMOUNT_CONFIDENCE_HIGH}"
    assert settings.EXTRACTOR_AMOUNT_CONFIDENCE_ZERO == 0.0, f"Expected EXTRACTOR_AMOUNT_CONFIDENCE_ZERO=0.0, got {settings.EXTRACTOR_AMOUNT_CONFIDENCE_ZERO}"
    assert settings.EXTRACTOR_VENDOR_CONFIDENCE_HIGH == 0.94, f"Expected EXTRACTOR_VENDOR_CONFIDENCE_HIGH=0.94, got {settings.EXTRACTOR_VENDOR_CONFIDENCE_HIGH}"
    assert settings.EXTRACTOR_VENDOR_CONFIDENCE_AMBIGUOUS == 0.78, f"Expected EXTRACTOR_VENDOR_CONFIDENCE_AMBIGUOUS=0.78, got {settings.EXTRACTOR_VENDOR_CONFIDENCE_AMBIGUOUS}"
    assert settings.EXTRACTOR_VENDOR_CONFIDENCE_ZERO == 0.0, f"Expected EXTRACTOR_VENDOR_CONFIDENCE_ZERO=0.0, got {settings.EXTRACTOR_VENDOR_CONFIDENCE_ZERO}"
    assert settings.EXTRACTOR_INVOICE_NUMBER_CONFIDENCE_HIGH == 0.95, f"Expected EXTRACTOR_INVOICE_NUMBER_CONFIDENCE_HIGH=0.95, got {settings.EXTRACTOR_INVOICE_NUMBER_CONFIDENCE_HIGH}"
    assert settings.EXTRACTOR_INVOICE_NUMBER_CONFIDENCE_ZERO == 0.0, f"Expected EXTRACTOR_INVOICE_NUMBER_CONFIDENCE_ZERO=0.0, got {settings.EXTRACTOR_INVOICE_NUMBER_CONFIDENCE_ZERO}"
    assert settings.EXTRACTOR_URGENCY_CONFIDENCE_HIGH == 0.95, f"Expected EXTRACTOR_URGENCY_CONFIDENCE_HIGH=0.95, got {settings.EXTRACTOR_URGENCY_CONFIDENCE_HIGH}"
    assert settings.EXTRACTOR_URGENCY_CONFIDENCE_LOW == 0.90, f"Expected EXTRACTOR_URGENCY_CONFIDENCE_LOW=0.90, got {settings.EXTRACTOR_URGENCY_CONFIDENCE_LOW}"
    assert settings.EXTRACTOR_URGENCY_CONFIDENCE_NORMAL == 0.85, f"Expected EXTRACTOR_URGENCY_CONFIDENCE_NORMAL=0.85, got {settings.EXTRACTOR_URGENCY_CONFIDENCE_NORMAL}"
    assert settings.EXTRACTOR_DEPARTMENT_CONFIDENCE_KNOWN == 0.92, f"Expected EXTRACTOR_DEPARTMENT_CONFIDENCE_KNOWN=0.92, got {settings.EXTRACTOR_DEPARTMENT_CONFIDENCE_KNOWN}"
    assert settings.EXTRACTOR_DEPARTMENT_CONFIDENCE_GENERAL == 0.50, f"Expected EXTRACTOR_DEPARTMENT_CONFIDENCE_GENERAL=0.50, got {settings.EXTRACTOR_DEPARTMENT_CONFIDENCE_GENERAL}"
    # Test new settings from rules
    assert settings.RULES_VENDOR_CONFIDENCE_THRESHOLD == 0.80, f"Expected RULES_VENDOR_CONFIDENCE_THRESHOLD=0.80, got {settings.RULES_VENDOR_CONFIDENCE_THRESHOLD}"
    assert settings.RULES_AMOUNT_CONFIDENCE_THRESHOLD == 0.80, f"Expected RULES_AMOUNT_CONFIDENCE_THRESHOLD=0.80, got {settings.RULES_AMOUNT_CONFIDENCE_THRESHOLD}"
    assert settings.RULES_VENDOR_CONFIDENCE_AMBIGUITY_THRESHOLD == 0.90, f"Expected RULES_VENDOR_CONFIDENCE_AMBIGUITY_THRESHOLD=0.90, got {settings.RULES_VENDOR_CONFIDENCE_AMBIGUITY_THRESHOLD}"
    assert settings.RULES_DEPARTMENT_CONFIDENCE_THRESHOLD == 0.80, f"Expected RULES_DEPARTMENT_CONFIDENCE_THRESHOLD=0.80, got {settings.RULES_DEPARTMENT_CONFIDENCE_THRESHOLD}"
    print("✓ Configuration test passed")

def test_auth():
    from backend.auth import API_KEYS, ROLE_PERMISSIONS
    # Check that the API keys are set from the environment
    assert API_KEYS['test-admin-key'] == 'admin', f"Expected API_KEY for admin key to be 'admin', got {API_KEYS['test-admin-key']}"
    assert API_KEYS['test-operator-key'] == 'operator', f"Expected API_KEY for operator key to be 'operator', got {API_KEYS['test-operator-key']}"
    assert API_KEYS['test-viewer-key'] == 'viewer', f"Expected API_KEY for viewer key to be 'viewer', got {API_KEYS['test-viewer-key']}"
    # Check that the role permissions are set
    assert 'read' in ROLE_PERMISSIONS['admin'], f"Expected 'read' in admin permissions, got {ROLE_PERMISSIONS['admin']}"
    assert 'write' in ROLE_PERMISSIONS['admin'], f"Expected 'write' in admin permissions, got {ROLE_PERMISSIONS['admin']}"
    assert 'delete' in ROLE_PERMISSIONS['admin'], f"Expected 'delete' in admin permissions, got {ROLE_PERMISSIONS['admin']}"
    assert 'approve' in ROLE_PERMISSIONS['admin'], f"Expected 'approve' in admin permissions, got {ROLE_PERMISSIONS['admin']}"
    assert 'configure' in ROLE_PERMISSIONS['admin'], f"Expected 'configure' in admin permissions, got {ROLE_PERMISSIONS['admin']}"
    assert 'read' in ROLE_PERMISSIONS['operator'], f"Expected 'read' in operator permissions, got {ROLE_PERMISSIONS['operator']}"
    assert 'write' in ROLE_PERMISSIONS['operator'], f"Expected 'write' in operator permissions, got {ROLE_PERMISSIONS['operator']}"
    assert 'approve' in ROLE_PERMISSIONS['operator'], f"Expected 'approve' in operator permissions, got {ROLE_PERMISSIONS['operator']}"
    assert 'read' in ROLE_PERMISSIONS['viewer'], f"Expected 'read' in viewer permissions, got {ROLE_PERMISSIONS['viewer']}"
    print("✓ Auth test passed")

if __name__ == '__main__':
    test_config()
    test_auth()
    print("\n✅ Phase 1 verification tests passed!")