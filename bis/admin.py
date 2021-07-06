from django.contrib import admin
from django.utils.safestring import mark_safe
import threading
from django.conf import settings
from django.http import HttpResponse
from django.core.mail import (send_mail, BadHeaderError, EmailMessage)
from .models import *
from .forms import *

# Register your models here.


def make_refund_accepted(modeladmin, request, queryset):
    queryset.update(refund_requested=False, refund_granted=True)


make_refund_accepted.short_description = 'Mettre à jour les commandes de remboursement accordées'


class OrderAdmin(admin.ModelAdmin):
    list_display = ['user',
                    'ordered',
                    'payer',
                    'utiliser',
                    'refund_requested',
                    'refund_granted',
                    'billing_address',
                    'payment',
                    'coupon'
                    ]
    list_display_links = [
        'user',
        'billing_address',
        'payment',
        'coupon'
    ]
    list_filter = ['user',
                   'ordered',
                   'payer',
                   'utiliser',
                   'refund_requested',
                   'refund_granted']
    search_fields = [
        'user__username',
        'ref_code'
    ]
    actions = [make_refund_accepted]


class AddressAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'prenom',
        'nom',
        'id_type',
        'id_number',
        'default'
    ]
    list_filter = ['default', 'id_type']
    search_fields = ['user','prenom','nom', 'id_type', 'id_number']


def copy_items(modeladmin, request, queryset):
    for object in queryset:
        object.id = None
        object.save()


copy_items.short_description = 'Copier Bus'


class BusAdmin(admin.ModelAdmin):
    list_display = [
        'author',
        'source',
        'destination',
        'date_depart',
        'is_active',
    ]
    list_filter = ['author', 'is_active','date_depart']
    search_fields = ['author', 'is_active','destination','source']
    # prepopulated_fields = {"slug": ("name",)}
    actions = [copy_items]
      
    def render_change_form(self, request, context, *args, **kwargs):
        context['adminform'].form.fields['author'].queryset = User.objects.filter(is_company=True)
        return super(BusAdmin, self).render_change_form(request, context, *args, **kwargs)
admin.site.register(Bus, BusAdmin)


class CategoryAdmin(admin.ModelAdmin):
    list_display = [
        'title',
        'is_active'
    ]
    list_filter = ['title', 'is_active']
    search_fields = ['title', 'is_active']
    prepopulated_fields = {"slug": ("title",)}


admin.site.register(Category, CategoryAdmin)

admin.site.register(OrderItem)
# admin.site.register(ItemSeller)
admin.site.register(Order, OrderAdmin)
admin.site.register(Payment)
admin.site.register(Coupon)
admin.site.register(Refund)
admin.site.register(BillingAddress, AddressAdmin)

class ContactusAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject','date',)
    search_fields = ('name', 'email',)
    date_hierarchy = 'date'

admin.site.register(Contactus, ContactusAdmin)
admin.site.register(Profile)

# class UserAdmin(admin.ModelAdmin):
#     list_display = [
#         'is_passenger',
#         'is_company'
#     ]
#     list_filter = ['is_passenger', 'is_company']
#     # search_fields = ['user']
admin.site.register(User)
admin.site.register(Testimonial)
admin.site.register(Wallet)
admin.site.register(WalletTransac)

class ReservationAdmin(admin.ModelAdmin):
    list_display = [
        'utiliser',
        'client',
        'nom',
        'prenom',
        'id_type',
        'id_number',
        'code',
        'source',
        'destination',
        'name',
        'prix',
        'date_depart',
    ]
    list_filter = ['author','client', 'utiliser','date']
    search_fields = ['client','destination','source']
admin.site.register(Reservation, ReservationAdmin)


class EmailThread(threading.Thread):
    def __init__(self, sujet, html_content, recipient_list):
        self.sujet = sujet
        self.recipient_list = recipient_list
        self.html_content = html_content
        threading.Thread.__init__(self)

    def run(self):
        msg = EmailMessage(self.sujet, self.html_content, settings.EMAIL_HOST_USER, self.recipient_list)
        msg.content_subtype = "html"
        try:
            msg.send()
        except BadHeaderError:
            return HttpResponse('En-tête non valide trouvé.')

class BroadCast_Email_Admin(admin.ModelAdmin):
    form = BroadCast_EmailAdminForm
    # model = BroadCast_Email

    def submit_email(self, request, obj): #`obj` is queryset, so there we only use first selection, exacly obj[0]
        list_email_user = [ p.email for p in User.objects.filter(is_passenger=True) ] #: if p.email != settings.EMAIL_HOST_USER   #this for exception
        obj_selected = obj[0]
        EmailThread(obj_selected.sujet, mark_safe(obj_selected.message), list_email_user).start()
    submit_email.short_description = "Envoyer les mails (n'oublie pas!! 1 sélection uniquement)"
    submit_email.allow_tags = True

    actions = [ 'submit_email' ]

    list_display = ("sujet", "creer")
    search_fields = ['sujet',]

admin.site.register(BroadCast_Email, BroadCast_Email_Admin)