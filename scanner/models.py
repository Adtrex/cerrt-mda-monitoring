from django.db import models
from django.utils import timezone
import datetime

# Create your models here.
class ScanTarget(models.Model):
    url = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)
    last_scanned_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.url

class ScanSession(models.Model):
    target = models.ForeignKey(ScanTarget, on_delete=models.CASCADE, related_name="scans")
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    score = models.FloatField(default=0.0)  # 0–100 rating
    summary = models.TextField(blank=True)  # optional overall notes

    def __str__(self):
        return f"Scan {self.id} for {self.target.url}"


class ScanReport(models.Model):
    url = models.URLField()
    scan_date = models.DateTimeField(auto_now_add=True)
    results = models.JSONField()
    
    class Meta:
        indexes = [
            models.Index(fields=['url']),
            models.Index(fields=['scan_date']),
        ]
    
    def __str__(self):
        return f"Report for {self.url} on {self.scan_date.strftime('%Y-%m-%d')}"
    
    @classmethod
    def get_latest_report(cls, url):
        """Get the latest report for a URL or None if no report exists"""
        return cls.objects.filter(url=url).order_by('-scan_date').first()
    
    @classmethod
    def should_create_new_report(cls, url):
        """Check if a new report should be created based on the 2-day rule"""
        latest_report = cls.get_latest_report(url)
        if not latest_report:
            return True
        
        two_days_ago = timezone.now() - datetime.timedelta(days=2)
        return latest_report.scan_date < two_days_ago
