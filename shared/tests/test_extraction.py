"""Tests for extraction utilities."""

from shared.extraction.bs4_extractor import ExtractionResult, extract_with_bs4
from shared.extraction.pii_filter import filter_pii, filter_pii_from_result


class TestBS4Extractor:
    """Tests for BeautifulSoup extractor."""

    def test_extract_from_json_ld(self) -> None:
        """Extract fields from JSON-LD structured data."""
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Software Engineer at ACME Corp</title>
            <script type="application/ld+json">
            {
                "@type": "JobPosting",
                "title": "Senior Software Engineer",
                "hiringOrganization": {
                    "@type": "Organization",
                    "name": "ACME Corporation"
                },
                "jobLocation": {
                    "@type": "Place",
                    "address": {
                        "addressLocality": "San Francisco",
                        "addressRegion": "CA"
                    }
                },
                "baseSalary": {
                    "currency": "USD",
                    "value": {
                        "minValue": 150000,
                        "maxValue": 200000,
                        "unitText": "YEAR"
                    }
                },
                "description": "We are looking for a talented engineer to join our team."
            }
            </script>
        </head>
        <body></body>
        </html>
        """
        result = extract_with_bs4(html)

        assert result.title == "Senior Software Engineer"
        assert result.company == "ACME Corporation"
        assert result.location == "San Francisco, CA"
        assert "150,000" in result.salary
        assert "200,000" in result.salary
        assert "talented engineer" in result.description

    def test_extract_from_meta_tags(self) -> None:
        """Extract fields from meta tags when JSON-LD is absent."""
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Product Manager - TechCorp</title>
            <meta property="og:title" content="Product Manager" />
            <meta property="og:site_name" content="TechCorp" />
        </head>
        <body></body>
        </html>
        """
        result = extract_with_bs4(html)

        assert result.title == "Product Manager"
        assert result.company == "TechCorp"

    def test_extract_with_unknown_fallbacks(self) -> None:
        """Fall back to Unknown when fields not found."""
        html = "<html><head></head><body>Empty page</body></html>"
        result = extract_with_bs4(html)

        assert result.title == "Unknown Title"
        assert result.company == "Unknown"
        assert result.location is None
        assert result.salary is None

    def test_is_complete(self) -> None:
        """Test completeness check."""
        complete = ExtractionResult(
            title="Engineer",
            company="ACME",
            location="NYC",
            salary=None,
            description=None,
        )
        assert complete.is_complete()

        incomplete = ExtractionResult(
            title="Unknown Title",
            company="ACME",
            location=None,
            salary=None,
            description=None,
        )
        assert not incomplete.is_complete()

    def test_to_dict(self) -> None:
        """Test dictionary conversion."""
        result = ExtractionResult(
            title="Engineer",
            company="ACME",
            location="Remote",
            salary="$100k",
            description="Great job",
            source="bs4",
        )
        d = result.to_dict()

        assert d["title"] == "Engineer"
        assert d["company"] == "ACME"
        assert d["extraction_method"] == "bs4"


class TestPIIFilter:
    """Tests for PII filtering."""

    def test_filter_email(self) -> None:
        """Filter email addresses."""
        text = "Contact us at john.doe@example.com for more info."
        filtered = filter_pii(text)
        assert "[EMAIL]" in filtered
        assert "john.doe@example.com" not in filtered

    def test_filter_phone_us(self) -> None:
        """Filter US phone numbers."""
        text = "Call us at (555) 123-4567 or 555-123-4567."
        filtered = filter_pii(text)
        assert "[PHONE]" in filtered
        assert "555" not in filtered

    def test_filter_linkedin(self) -> None:
        """Filter LinkedIn URLs."""
        text = "See my profile at linkedin.com/in/johndoe"
        filtered = filter_pii(text)
        assert "[LINKEDIN]" in filtered
        assert "johndoe" not in filtered

    def test_filter_none(self) -> None:
        """Handle None input."""
        assert filter_pii(None) is None

    def test_filter_no_pii(self) -> None:
        """Text without PII passes through."""
        text = "We are looking for a software engineer with 5 years experience."
        filtered = filter_pii(text)
        assert filtered == text

    def test_filter_from_result(self) -> None:
        """Apply filter to ExtractionResult."""
        result = ExtractionResult(
            title="Engineer",
            company="ACME",
            location="NYC",
            salary=None,
            description="Contact john@example.com for details.",
        )
        filtered = filter_pii_from_result(result)

        # Title and company unchanged
        assert filtered.title == "Engineer"
        assert filtered.company == "ACME"
        # Description filtered
        assert "[EMAIL]" in filtered.description
        assert "john@example.com" not in filtered.description
