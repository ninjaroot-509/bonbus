from django.urls import include, path
from django.conf.urls import url
from django.views.generic import TemplateView
from .views import *

urlpatterns = [
    path('', bis.home, name='home'),
    path('Erreur-de-compte/', bis.bevalide, name='bevalide'),
    path('Profile-edite/', bis.ProfileUpdateView.as_view(), name='profile-update'),
    path('Profile/', bis.profile, name='profile'),
    path('utilisateurs/<slug>/', bis.profile_view, name='profile_view'),
    path('A-propos/', TemplateView.as_view(template_name='bis/about.html'), name='about'),
    path('Contactez-nous/', bis.contact, name='contact'),
    path('FAQ/', bis.faq, name='faq'),
    path('Comment-sa-fonctionne/', bis.howork, name="howork"),
    path('Mes/Testimonials/', bis.testimonial, name="testi"),
    
    path('', include(([
        path('Dashboard/', companies.viewcomp, name='viewcomp'),
        path('my-bus/', companies.mybus, name="mybus"),
        path('edit_places/', companies.edit_n_places, name="n_places"),
        path('reservation_listes/', companies.reservation_listes, name="all_re"),
        path('bus-disponible-en-ce-moment/', companies.reservation_at_this_time, name="at_time"),
        path('Ajouter/Bus/', companies.AddBusView.as_view(), name='addbus'),
        url(r'^Bus/(?P<pk>[0-9]+)/update/$', companies.BusUpdateView.as_view(), name='bus_update'),
        url(r'^Bus/(?P<pk>[0-9]+)/delete/$', companies.BusDeleteView.as_view(), name='bus_delete'),
        ###taxi###
        path('Ajouter/Taxi/', companies.AddTaxiView.as_view(), name='addtaxi'),
        url(r'^Taxi/(?P<pk>[0-9]+)/update/$', companies.TaxiUpdateView.as_view(), name='taxi_update'),
        url(r'^Taxi/(?P<pk>[0-9]+)/delete/$', companies.TaxiDeleteView.as_view(), name='taxi_delete'),
        ###end###
        path('rechercher-Reservation/', companies.search_reser, name='search_reser'),
        path('check/reservation/<code>/', companies.check, name="check"),
        path('uncheck/reservation/<code>/', companies.uncheck, name="uncheck"),
    ], 'bis'), namespace='companies')),

    path('', include(([
        path('Acceuil/', passengers.viewp, name='viewp'),
        path('Listes/Bus/', passengers.findbus, name="findbus"),
        path('Rechercher/Bus/', passengers.search_bus, name="search_bus"),
        path('Rechercher/Bus/q/', passengers.offre, name="offre"),
        path('Annulations/Bus/', passengers.cancellings, name="cancellings"),
        path('Mes/Reservations/Bus/', passengers.seebookings, name="reser"),
        path('Bus/<slug>/', passengers.BusDetailView.as_view(), name='bus_detail'),
        path('Formulaire-de-paiment/', passengers.CheckoutView.as_view(), name='checkout'),
        path('categorie/<slug>/', passengers.CategoryView.as_view(), name='category'),
        path('ajouter-ticket/<slug>/', passengers.add_ticket, name='add-ticket'),
        path('Mes-tickets/', passengers.OrderSummaryView.as_view(), name='order-summary'),
        path('effacer-ticket/<slug>/', passengers.remove_single_item_ticket, name='remove-single-item-ticket'),
        path('ajouter_coupon/', passengers.AddCouponView.as_view(), name='add-coupon'),
        path('effacer-ticket/<slug>/', passengers.remove_ticket, name='remove-ticket'),
        path('paiment-M/moncash/', passengers.payment_moncash, name='payment_moncash'),
        path('paiment/Portefeuille/', passengers.payment_bous, name='payment_bous'),
        path('paiment-P/paypal/', passengers.payment_paypal, name='payment_paypal'),
        path('transaction/success/', passengers.moncash_p_done, name='moncash_p_done'),
        path('transaction/error/', passengers.moncash_p_error, name='moncash_p_error'),
        path('payment-P/Done/', passengers.payment_p_done, name='payment_p_done'),
        path('payment-P/Annuler/', passengers.payment_p_canceled, name='payment_p_canceled'),
        path('Remboursement/', passengers.RequestRefundView.as_view(), name='request-refund'),
        path('create-wallet/', passengers.create_wallet, name="create-wallet"),
        path('Depot/Moncash/', passengers.wallet_cash_send, name="depot"),
        path('Transactions/Depot/Moncash/', passengers.depot_moncash, name="depot_moncash"),
    ], 'bis'), namespace='passengers')),
]
