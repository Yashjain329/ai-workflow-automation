from backend.models.classifier import MLTaskClassifier
from backend.models.extractor import FieldExtractor

def test_ml_task_classifier():
    clf = MLTaskClassifier()
    
    cat, conf = clf.predict("INVOICE #4412 from Acme Corp Total Amount: $2500.00")
    assert cat == "invoice"
    assert conf >= 0.70

    cat2, conf2 = clf.predict("SUPPORT TICKET: Need password reset for laptop access")
    assert cat2 == "service_request"
    assert conf2 >= 0.70

def test_field_extractor():
    text = "INVOICE #9981 from Global Supplies Total Amount Due: $3450.50"
    fields = FieldExtractor.extract_fields(text, "invoice")
    assert fields["amount"] == 3450.50
    assert fields["vendor"] == "Global Supplies"
    assert fields["invoice_number"] == "9981"
