from django.contrib import admin
from .models import StockAnalysis

class StockAnalysisAdmin(admin.ModelAdmin):
    fields = ['stockTicker', 'lastUpdated', 'sentimentScore', 'numTweets', 'numPositiveTweets', 'numNeutralTweets', 'numNegativeTweets']
    list_display = ('stockTicker', 'lastUpdated', 'is_outdated')
    search_fields = ['stockTicker']
    ordering = ('-lastUpdated',)



# Register your models here.
admin.site.register(StockAnalysis, StockAnalysisAdmin)