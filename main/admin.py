from django.contrib import admin
from .models import StockAnalysis

class StockAnalysisAdmin(admin.ModelAdmin):
    fields = ['stockTicker', 'lastUpdated', 'numTweets', 'positiveSentiment', 'negativeSentiment']
    list_display = ('stockTicker', 'lastUpdated', 'is_outdated')
    search_fields = ['stockTicker']
    ordering = ('-lastUpdated',)



# Register your models here.
admin.site.register(StockAnalysis, StockAnalysisAdmin)