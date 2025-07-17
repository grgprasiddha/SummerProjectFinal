from django.contrib import admin
from .models import Job, Proposal, Contract, Review, Dispute

# Register the models with explicit admin site
admin_site = admin.site

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('compact_title', 'client', 'category', 'budget', 'status', 'deadline', 'created_at')
    search_fields = ('title', 'client__username', 'category', 'description')
    list_filter = ('category', 'status', 'created_at')
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 50
    actions = ['simple_delete', 'mark_as_completed', 'mark_as_cancelled']
    list_select_related = ('client',)
    
    # Enable delete functionality
    def has_delete_permission(self, request, obj=None):
        return True
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'category', 'budget', 'deadline', 'requirements', 'image')
        }),
        ('Status & Client', {
            'fields': ('status', 'client')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def compact_title(self, obj):
        """Display a compact version of the job title"""
        if len(obj.title) > 40:
            return f"{obj.title[:40]}..."
        return obj.title
    compact_title.short_description = 'Title'
    compact_title.admin_order_field = 'title'
    
    def simple_delete(self, request, queryset):
        count = queryset.count()
        queryset.delete()
        self.message_user(request, f'{count} job(s) deleted successfully.')
    simple_delete.short_description = "Delete selected jobs"
    
    def mark_as_completed(self, request, queryset):
        updated = queryset.update(status='completed')
        self.message_user(request, f'{updated} job(s) marked as completed.')
    mark_as_completed.short_description = "Mark selected jobs as completed"
    
    def mark_as_cancelled(self, request, queryset):
        updated = queryset.update(status='cancelled')
        self.message_user(request, f'{updated} job(s) marked as cancelled.')
    mark_as_cancelled.short_description = "Mark selected jobs as cancelled"
    
    def get_actions(self, request):
        actions = super().get_actions(request)
        print(f"DEBUG: Available actions: {list(actions.keys())}")
        return actions
    
    def changelist_view(self, request, extra_context=None):
        print("DEBUG: changelist_view called")
        response = super().changelist_view(request, extra_context)
        print(f"DEBUG: Response status: {response.status_code}")
        return response

@admin.register(Proposal)
class ProposalAdmin(admin.ModelAdmin):
    list_display = ('job', 'freelancer', 'bid_amount', 'estimated_days', 'status', 'created_at')
    search_fields = ('job__title', 'freelancer__username', 'cover_letter')
    list_filter = ('status', 'created_at', 'estimated_days')
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 20

@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = ('job', 'freelancer', 'client', 'status', 'start_date', 'end_date', 'completion_status')
    search_fields = ('job__title', 'freelancer__username', 'job__client__username')
    list_filter = ('status', 'start_date', 'end_date', 'completed_by_freelancer', 'confirmed_by_client')
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 20
    
    def client(self, obj):
        return obj.job.client.username
    client.short_description = 'Client'
    
    def completion_status(self, obj):
        if obj.completed_by_freelancer and obj.confirmed_by_client:
            return "✅ Completed"
        elif obj.completed_by_freelancer:
            return "⏳ Awaiting Confirmation"
        else:
            return "📋 In Progress"
    completion_status.short_description = 'Completion Status'
    
    fieldsets = (
        ('Contract Details', {
            'fields': ('job', 'freelancer', 'proposal', 'terms', 'start_date', 'end_date', 'status')
        }),
        ('Completion Status', {
            'fields': ('completed_by_freelancer', 'completed_at', 'confirmed_by_client', 'confirmed_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('contract', 'reviewer', 'rating', 'created_at')
    search_fields = ('contract__job__title', 'reviewer__username', 'comment')
    list_filter = ('rating', 'created_at')
    readonly_fields = ('created_at',)

@admin.register(Dispute)
class DisputeAdmin(admin.ModelAdmin):
    list_display = ('title', 'contract', 'raised_by', 'status', 'created_at')
    search_fields = ('title', 'contract__job__title', 'raised_by__username', 'description')
    list_filter = ('status', 'created_at')
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 20
    
    fieldsets = (
        ('Dispute Information', {
            'fields': ('title', 'contract', 'payment', 'raised_by', 'description', 'evidence', 'status')
        }),
        ('Resolution', {
            'fields': ('resolution', 'admin_decision', 'decided_by')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
