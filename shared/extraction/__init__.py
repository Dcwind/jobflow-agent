"""Job extraction utilities with fallback chain."""

from shared.extraction.bs4_extractor import ExtractionResult, extract_with_bs4
from shared.extraction.pii_filter import filter_pii, filter_pii_from_result
from shared.extraction.pipeline import ExtractionMetrics, extract_job

__all__ = [
    "extract_job",
    "extract_with_bs4",
    "ExtractionResult",
    "ExtractionMetrics",
    "filter_pii",
    "filter_pii_from_result",
]
