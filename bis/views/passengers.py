from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.db.models import Avg, Count
from django.forms import inlineformset_factory
from django.shortcuts import get_object_or_404, redirect, render, HttpResponse
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView, View)
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from ..decorators import passenger_required
from ..forms import *
from ..models import *
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from decimal import Decimal
from django.core.mail import send_mail, BadHeaderError, mail_admins
from django.urls import reverse_lazy, reverse
from django.db.models.signals import post_save
from django.template import Context
from django.template.loader import render_to_string, get_template
from django.utils.html import strip_tags
from django.contrib.auth import authenticate
from django.core.mail import EmailMultiAlternatives
from django.db.models import Q
import random
import string
from time import gmtime, strftime
import datetime
from datetime import date
from django.http import HttpResponseRedirect

@passenger_required
def depot_moncash(request):
    wallets = WalletTransac.objects.filter(user=request.user).order_by('-date')
    return render(request, 'companies/depot_list.html', locals())

@passenger_required
def create_wallet(request):
    re_user = request.user
    ver = Wallet.objects.filter(user=re_user)
    if ver.exists():
        messages.warning(request, "Vous Avez deja une portefeuille enregistrer sur BusHaiti.")
        return redirect('profile')
    else:
        Wallet.objects.get_or_create(user=request.user)
        messages.success(request, "Vous venez d'enregistrer une portefeuille sur BusHaiti.")
    return redirect('profile')

@passenger_required 
def wallet_cash_send(request):
    if request.method == 'POST':
        montant = int(request.POST['montant'])
        order_id = create_ref_code()
        moncash = moncashify.API(settings.MONCASH_CLIENT_ID, settings.MONCASH_SECRET_KEY, debug=False)
        payment = moncash.payment(order_id, montant)
        Order.objects.filter(user=request.user).delete()
        return HttpResponseRedirect(payment.redirect_url)
    return render(request, 'companies/depot.html')    
    
from itertools import chain

@passenger_required 
def viewp(request):
    today = date.today()
    # now1 = datetime.datetime.now().time()
    # now = datetime.datetime.now().strftime("%Y, %m, %d, %H, %M")
    now = timezone.now()
    # nowfilter = now + datetime.timedelta(hours = 1)
    # timefilter = nowfilter.time().strftime('%H:%M')
    testi = Testimonial.objects.all()
    item1 = Bus.objects.filter(is_active=True, date_depart__gte=now).order_by('-date_depart')
    item2 = Bus.objects.filter(is_active=True, is_taxi=True)
    items = list(chain(item2, item1))
    return render(request, 'bis/index.html', locals())

class PassengerSignUpView(CreateView):
    model = User
    form_class = PassengerSignUpForm
    template_name = 'registration/signup_form.html'

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'passenger'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('profile-update')
    
import unicodedata

def strip_accents(text):
    try:
        text = unicode(text, 'utf-8')
    except NameError: # unicode is a default on python 3 
        pass

    text = unicodedata.normalize('NFD', text)\
           .encode('ascii', 'ignore')\
           .decode("utf-8")
    return str(text)


def offre(request):
    today = date.today()
    now1 = datetime.datetime.now().time()
    now = datetime.datetime.now()
    nowfilter = now + datetime.timedelta(hours = 1)
    if request.method == 'GET':
        dest_r = request.GET.get('destination', '')
        bus_list = Bus.objects.filter(Q(Q(destination__icontains=strip_accents(dest_r))))
        if bus_list:
            return render(request, 'bis/list.html', locals())
        else:
            messages.warning(request, "Pas encore de bus prévu pour ses paramètres!!.")
            return redirect('passengers:search_bus')
    else:
        return redirect('passengers:search_bus')

def findbus(request):
    today = date.today()
    now1 = datetime.datetime.now().time()
    # now = datetime.datetime.now().strftime("%Y, %m, %d, %H, %M")
    now = timezone.now()
    # nowfilter = now + datetime.timedelta(hours = 1)
    # timefilter = nowfilter.time().strftime('%H:%M')
    if request.method == 'GET':
        source_r = request.GET.get('source', '')
        dest_r = request.GET.get('destination', '')
        date_r = request.GET.get('date_depart', '')
        if source_r and dest_r and date_r:
            bus_list = Bus.objects.filter(Q(source__icontains=strip_accents(source_r)), Q(destination__icontains=strip_accents(dest_r)), date_depart__startswith=date_r)
        elif source_r and dest_r:
            bus_list = Bus.objects.filter(Q(source__icontains=strip_accents(source_r)), Q(destination__icontains=strip_accents(dest_r)))
        elif source_r and date_r:
            bus_list = Bus.objects.filter(Q(source__icontains=strip_accents(source_r)), date_depart__startswith=date_r)
        elif dest_r and date_r:
            bus_list = Bus.objects.filter(Q(destination__icontains=strip_accents(dest_r)), date_depart__startswith=date_r)
        elif source_r:
            bus_list = Bus.objects.filter(Q(source__icontains=strip_accents(source_r)))
        elif dest_r:
            bus_list = Bus.objects.filter(Q(destination__icontains=strip_accents(dest_r)))
        elif date_r:
            bus_list = Bus.objects.filter(date_depart__startswith=date_r)
        else:
            bus_list = Bus.objects.filter()
        if bus_list:
            return render(request, 'bis/list.html', locals())
        else:
            messages.warning(request, "Pas encore de bus prévu pour ses paramètres!!.")
            return redirect('passengers:search_bus')
    else:
        return redirect('passengers:search_bus')

def search_bus(request):
    return render(request, 'bis/findbus.html')

@passenger_required 
def cancellings(request):
    return render(request, 'bis/findbus.html')


@passenger_required 
def seebookings(request):
    id_r = request.user
    book_list = Reservation.objects.filter(client=id_r).order_by('-date_depart')
    if book_list:
        return render(request, 'bis/booklist.html', locals())
    else:
        messages.error(request, "Désolé aucun bus réservé!!")
        return render(request, 'bis/findbus.html')
  
# @method_decorator([login_required, passenger_required], name='dispatch')   
class BusDetailView(DetailView):
    model = Bus
    template_name = "bis/bus-detail.html"
    
    def get_context_data(self, **kwargs):
        context = super(BusDetailView, self).get_context_data(**kwargs)
        context['items'] = Bus.objects.filter(is_active=True)

        return context

@passenger_required 
def add_ticket(request, slug):
    ticket = Order.objects.filter(user=request.user, ordered=False).count()
    if int(ticket) < 1:
        item = get_object_or_404(Bus, slug=slug)
        order_item, created = OrderItem.objects.get_or_create(
            item=item,
            user=request.user,
            ordered=False
        )
        order_item.item.nombre_place -= 1
        order_item.item.save()
        order_qs = Order.objects.filter(user=request.user, ordered=False)
        if order_qs.exists():
            order = order_qs[0]
            quan1 = int(order_item.item.nombre_place)
            quan2 = int(order_item.quantity)
            if order.items.filter(item__slug=item.slug).exists():
                messages.warning(request, "Ticket existe deja!?.")
                return redirect("passengers:order-summary")
            else:
                order.items.add(order_item)
                messages.success(request, "le ticket a été ajouté avec succes.")
                return redirect("passengers:order-summary")
        else:
            ordered_date = timezone.now()
            order = Order.objects.create(
                user=request.user, ordered_date=ordered_date)
            order.items.add(order_item)
            messages.success(request, "le ticket a été ajouté avec succes.")
            return redirect("passengers:order-summary")
    else:
        messages.warning(request, "Vous avez deja un ticket enregistrer!.")
        messages.error(request, "Vous avez deja un ticket enregistrer!.")
        return redirect("passengers:order-summary")


@passenger_required 
def remove_ticket(request, slug):
    item = get_object_or_404(Bus, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        quan1 = int(order_item.item.nombre_place)
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            order_item.item.nombre_place += 1
            order_item.item.save()
            order.items.remove(order_item)
            order1 = Order.objects.get(user=request.user,ordered=False)
            order1.delete()
            messages.success(request, "Item was removed from your ticket.")
            return redirect("passengers:order-summary")
        else:
            # add a message saying the user dosent have an order
            messages.error(request, "Item was not in your ticket.")
            return redirect("passengers:product", slug=slug)
    else:
        # add a message saying the user dosent have an order
        messages.error(request, "u don't have an active order.")
        return redirect("passengers:product", slug=slug)
    return redirect("passengers:product", slug=slug)


@passenger_required 
def remove_single_item_ticket(request, slug):
    item = get_object_or_404(Bus, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            order_item.item.nombre_place += 1
            order_item.item.save()
            order.items.remove(order_item)
            order1 = Order.objects.get(user=request.user,ordered=False)
            order1.delete()
            messages.success(request, "This item qty was updated.")
            return redirect("passengers:order-summary")
        else:
            # add a message saying the user dosent have an order
            messages.error(request, "Item was not in your ticket.")
            return redirect("passengers:product", slug=slug)
    else:
        # add a message saying the user dosent have an order
        messages.error(request, "u don't have an active order.")
        return redirect("passengers:product", slug=slug)
    return redirect("passengers:product", slug=slug)

@passenger_required 
def get_coupon(request, code):
    try:
        coupon = Coupon.objects.get(code=code)
        return coupon
    except ObjectDoesNotExist:
        messages.warning(request, "This coupon does not exist")
        return redirect("passengers:checkout")

@method_decorator([login_required, passenger_required], name='dispatch')   
class OrderSummaryView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'object': order,
                'couponform': CouponForm(),
                'DISPLAY_COUPON_FORM': True
            }
            return render(self.request, 'bis/mytickets.html', context)
        except ObjectDoesNotExist:
            messages.error(self.request, "Vous n'avez pas de commande active")
            return redirect("/") 

@method_decorator([login_required, passenger_required], name='dispatch')   
class CheckoutView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            # distance = OrderItem.objects.get(user=self.request.user,ordered=True)[0]
            form = CheckoutForm()
            context = {
                'form': form,
                'couponform': CouponForm(),
                'order': order,
                'DISPLAY_COUPON_FORM': True,
                # 'distance': distance
            }
            return render(self.request, "bis/checkout.html", context)

        except ObjectDoesNotExist:
            messages.error(self.request, "Vous n'avez pas de commande active")
            return redirect("passengers:checkout")

    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            print(self.request.POST)
            if form.is_valid():
                prenom = form.cleaned_data.get('prenom')
                nom = form.cleaned_data.get('nom')
                id_type = form.cleaned_data.get('id_type')
                id_number = form.cleaned_data.get('id_number')
                # add functionality for these fields
                payment_option = form.cleaned_data.get('payment_option')
                # captcha = form.cleaned_data.get('captcha')
                billing_address = BillingAddress(
                    user=self.request.user,
                    prenom=prenom,
                    nom=nom,
                    id_type=id_type,
                    id_number=id_number,
                )
                billing_address.save()
                order.billing_address = billing_address
                order.save()
 
                # add redirect to the selected payment option
                if payment_option == 'P':
                    return redirect('passengers:payment_bous')
                elif payment_option == 'M':
                    return redirect('passengers:payment_moncash')
                else:
                    messages.warning(self.request, "Votre methode de paiement n'est pas valide")
                    return redirect('passengers:checkout')
            else:
                messages.warning(self.request, "Veuillez remplir tout les champs")
                return redirect('passengers:checkout')
        except ObjectDoesNotExist:
            messages.error(self.request, "Vous n'avez pas de commande active")
            return redirect("passengers:order-summary",)

class CategoryView(View):
    def get(self, *args, **kwargs):
        category = Category.objects.get(slug=self.kwargs['slug'])
        item = Item.objects.filter(category=category, is_active=True)
        context = {
            'object_list': item,
            'category_title': category,
            'category_description': category.description,
            'category_image': category.image
        }
        return render(self.request, "bis/category.html", context)

@method_decorator([login_required, passenger_required], name='dispatch')   
class AddCouponView(LoginRequiredMixin, View):
    def post(self, *args, **kwargs):
        form = CouponForm(self.request.POST or None)
        if form.is_valid():
            try:
                code = form.cleaned_data.get('code')
                order = Order.objects.get(
                    user=self.request.user, ordered=False)
                order.coupon = get_coupon(self.request, code)
                order.save()
                messages.success(self.request, "Successfully added coupon")
                return redirect("passengers:checkout")

            except ObjectDoesNotExist:
                messages.error(request, "You do not have an active order")
                return redirect("passengers:checkout")


class RequestRefundView(View):
    def get(self, *args, **kwargs):
        form = RefundForm()
        context = {
            'form': form
        }
        return render(self.request, "request_refund.html", context)

    def post(self, *args, **kwargs):
        form = RefundForm(self.request.POST)
        if form.is_valid():
            ref_code = form.cleaned_data.get('ref_code')
            message = form.cleaned_data.get('message')
            email = form.cleaned_data.get('email')
            # edit the order
            try:
                order = Order.objects.get(ref_code=ref_code)
                order.refund_requested = True
                order.save()

                # store the refund
                refund = Refund()
                refund.order = order
                refund.reason = message
                refund.email = email
                refund.save()

                messages.success(self.request, "Your request was received")
                return redirect("passengers:request-refund")

            except ObjectDoesNotExist:
                messages.error(self.request, "This order does not exist")
                return redirect("passengers:request-refund")


def create_ref_code():
    prefix = 'BSH-'
    # return ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
    return prefix + ''.join(random.choices(string.digits, k=5))

import moncashify

@passenger_required 
def payment_moncash(request):
    # order_id = request.session.get('order_id')
    # order = get_object_or_404(Order, id=order_id)
    order = Order.objects.get(user=request.user, ordered=False)
    moncash = moncashify.API(settings.MONCASH_CLIENT_ID, settings.MONCASH_SECRET_KEY, debug=False)
    order_id = order.id
    prix = int(order.get_total())
    payment = moncash.payment(order_id, prix)
    return redirect(payment.redirect_url)

# return render(request,'bis/moncash.html', locals())

import datetime
from qr_code.qrcode.utils import ContactDetail, WifiConfig, Coordinates, QRCodeOptions

@passenger_required 
def moncash_p_done(request):
    if request.method == 'GET':
        re_user = request.user
        commande = Order.objects.filter(user=re_user,ordered=False)
        transaction_id_moncash = request.GET['transactionId']
        if commande:
            order = Order.objects.get(user=re_user, ordered=False)
            order_id = order.id
            transaction_id = create_ref_code()
            moncash = moncashify.API(settings.MONCASH_CLIENT_ID, settings.MONCASH_SECRET_KEY, debug=False)
            transaction = moncash.transaction_details_by_order_id(order_id)
            if transaction:
                ordob = Order.objects.get(user=re_user,ordered=False).items.all()
                for i in ordob:
                    transaction = Reservation.objects.create(author=i.item.author, date=order.ordered_date,nom=order.billing_address.nom,prenom=order.billing_address.prenom,id_type=order.billing_address.id_type,id_number=order.billing_address.id_number,client=re_user, date_depart=i.item.date_depart,source=i.item.source, destination=i.item.destination, code=transaction_id, name=i.item.name,quantite=i.quantity,image=i.item.image,prix=i.item.prix)
                    
                payment = Payment()
                payment.charge_id = transaction_id_moncash
                payment.user = request.user
                payment.amount = order.get_total()
                payment.save()
                # assign the payment to the order
                order.ordered = True
                order.payer = True
                order.payment = payment
                # TODO : assign ref code
                order.ref_code = transaction_id
                order.save()
                
                date_now = datetime.datetime.now()
                product = Order.objects.get(user=re_user,ordered=True,ref_code=transaction_id)
                from_email = settings.EMAIL_HOST_USER
                data = {
                    'user': re_user,
                    'product': product,
                    'order': order,
                    'date_now':date_now,
                }
        
                #companies
                for i in Order.objects.get(user=re_user,ordered=True,ref_code=transaction_id).items.all():
                    subjectvend = "hello %s" % i.item.author.username
                    html_contentcomp = render_to_string('companies/comp.html', data)
                    text_contentcomp = strip_tags(html_contentcomp)
            
                    # create the email, and attach the HTML version as well.
                    msg1 = EmailMultiAlternatives(subjectvend, text_contentcomp, from_email, [i.item.author.email])
                    msg1.attach_alternative(html_contentcomp, "text/html")
                    msg1.send(fail_silently=False)
                
                #clients
                html_contentclient = render_to_string('companies/invoice.html', data)
                text_contentclient = strip_tags(html_contentclient)
        
                # create the email, and attach the HTML version as well.
                msg1 = EmailMultiAlternatives("Commande validee", text_contentclient, from_email, [re_user.email])
                msg1.attach_alternative(html_contentclient, "text/html")
                msg1.send(fail_silently=False)
                
                html_content_admin = render_to_string('companies/admin.html', data)
                text_content_admin = strip_tags(html_content_admin)
        
                # create the email, and attach the HTML version as well.
                mail_admins("Nouvelle commande!", text_content_admin, html_message=html_content_admin)
                messages.success(request, "transaction reussie, verifier votre email!!")
            else:
                messages.warning(request, "Erreur de transaction, le paiement n'a pas été effectué!!")
                return redirect('home')
        else:
            moncash = moncashify.API(settings.MONCASH_CLIENT_ID, settings.MONCASH_SECRET_KEY, debug=False)
            transac = moncash.transaction_details_by_transaction_id(transaction_id_moncash)
            if transac:
                transaction = Wallet.objects.filter(user=re_user).update(montant=F('montant') + transac["payment"]["cost"])
                transaction1 = WalletTransac.objects.create(user=re_user, montant=transac["payment"]["cost"])
                if transaction:
                    wallet = Wallet.objects.get(user=request.user)
                    from_email = settings.EMAIL_HOST_USER
                    to_email = [request.user.email]
                    subject = "Recharge reussi le %s" % wallet.date
                    messageadmin = "L'utilisateur %s vient juste de faire une transaction de %s gourdes depuis son compte moncash a son Portefeuille" % (wallet.user.username, request.user.wallet.montant)
                    message = "hello %s \n vous venez d'effectuer une transaction de %s gourdes depuis votre compte moncash a votre Portefeuille sur BusHaiti, \n BusHaiti, Merci!!." % (wallet.user.username, request.user.wallet.montant)
                    mail_admins(subject, messageadmin)
                    send_mail(subject, message, from_email, to_email, fail_silently=False)
                    messages.success(request, "transaction reussi, un mail vous a ete envoyer")
                    return redirect('profile')
                else:
                    messages.error(request, "une erreur s'est produite, la requette a echoue")
                    return redirect('profile')
            else:
                messages.warning(request, "Erreur de transaction, le depot n'a pas été effectué!!")
                return redirect('profile')
    return redirect('home')

def moncash_p_error(request):
    message = "payment echoue"
    return HttpResponse(message)



from django.db.models import F

def payment_bous(request):
    re_user = request.user
    order_id = request.session.get('order_id')
    transaction_id = create_ref_code()
    # order = get_object_or_404(Order, id=order_id)
    order = Order.objects.get(user=request.user, ordered=False)
    order_id = order.id
    price = int(order.get_total())
    wallet_total = Wallet.objects.filter(user=request.user).aggregate(sum_all=Sum('montant')).get('sum_all')
    if wallet_total and wallet_total >= price:
        ordob = Order.objects.get(user=re_user,ordered=False).items.all()
        for i in ordob:
            transaction = Reservation.objects.create(author=i.item.author, date=order.ordered_date,nom=order.billing_address.nom,prenom=order.billing_address.prenom,id_type=order.billing_address.id_type,id_number=order.billing_address.id_number,client=re_user, date_depart=i.item.date_depart,source=i.item.source, destination=i.item.destination, code=transaction_id, name=i.item.name,quantite=i.quantity,image=i.item.image,prix=i.item.prix)
            
        transaction = Wallet.objects.filter(user=re_user).update(montant = F('montant') - price)
        
        payment = Payment()
        payment.charge_id = transaction_id
        payment.user = request.user
        payment.amount = order.get_total()
        payment.save()
        # assign the payment to the order
        order.ordered = True
        order.payer = True
        order.payment = payment
        # TODO : assign ref code
        order.ref_code = transaction_id
        order.save()
        
        date_now = datetime.datetime.now()
        product = Order.objects.get(user=re_user,ordered=True,ref_code=transaction_id)
        from_email = settings.EMAIL_HOST_USER
        data = {
            'user': re_user,
            'product': product,
            'order': order,
            'date_now':date_now,
        }

        #companies
        for i in Order.objects.get(user=re_user,ordered=True,ref_code=transaction_id).items.all():
            subjectvend = "hello %s" % i.item.author.username
            html_contentcomp = render_to_string('companies/comp.html', data)
            text_contentcomp = strip_tags(html_contentcomp)
    
            # create the email, and attach the HTML version as well.
            msg1 = EmailMultiAlternatives(subjectvend, text_contentcomp, from_email, [i.item.author.email])
            msg1.attach_alternative(html_contentcomp, "text/html")
            msg1.send(fail_silently=False)
        
        #clients
        html_contentclient = render_to_string('companies/invoice.html', data)
        text_contentclient = strip_tags(html_contentclient)

        # create the email, and attach the HTML version as well.
        msg1 = EmailMultiAlternatives("Commande validee", text_contentclient, from_email, [re_user.email])
        msg1.attach_alternative(html_contentclient, "text/html")
        msg1.send(fail_silently=False)
        
        html_content_admin = render_to_string('companies/admin.html', data)
        text_content_admin = strip_tags(html_content_admin)

        # create the email, and attach the HTML version as well.
        mail_admins("Nouvelle commande!", text_content_admin, html_message=html_content_admin)
        messages.success(request, "transaction reussie, verifier votre email!!")
        return HttpResponseRedirect('/')
    else:
        messages.warning(request, "Votre Solde est inssufisante!!")
        return redirect('profile')


from django.views.decorators.csrf import csrf_exempt

@passenger_required 
def payment_paypal(request):
    order_id = request.session.get('order_id')
    # order = get_object_or_404(Order, id=order_id)
    order = Order.objects.get(user=request.user, ordered=False)
    return render(request, 'bis/payment-p.html', {'order': order})    

@csrf_exempt
@passenger_required 
def payment_p_done(request):
    if request.method == 'GET':
        body = json.loads(request.body)
        order = Order.objects.get(user=request.user, ordered=False, id=body['orderID'])
        order_id = order.id
        prix = int(order.get_total())
        # transaction1 = Wallet.objects.create(user=re_user,ballance=prix - wallet_total)
        payment = Payment(
            user=request.user,
            charge_id=body['orderID'],
            amount=order.get_total()
        )
        payment.save()
    
        # assign the payment to the order
        order.ordered = True
        order.payment = payment
        # TODO : assign ref code
        order.ref_code = create_ref_code()
        order.save()
        for i in OrderItem.objects.filter(user=re_user,ordered=True):
            transaction = Reservation.objects.create(author=i.item.author, code=order.ref_code,client=request.user,date_depart=i.item.date_depart,name=i.item.name,quantite=i.quantity,image=i.item.image,prix=i.item.prix)
        date_now = strftime("%Y-%m-%d %H:%M:%S", gmtime())
        product = OrderItem.objects.filter(user=re_user,ordered=True)
        from_email = settings.EMAIL_HOST_USER
        data = {
            'user': re_user,
            'product': product,
            'order': order,
            'date_now':date_now
        }

        #companies
        for i in OrderItem.objects.filter(user=re_user,ordered=True):
            subjectvend = "hello %s, (ventes!!!)" % i.item.author.username
            send_mail(subjectvend, "Vous venez de vendre un produit, veuillez connectez afin de voir le produit vendu \n assurez vous que les produits sont tous disponible pour les livraisons",from_email, [i.item.author.email], fail_silently=False)
        #clients
        html_contentclient = render_to_string('companies/invoice.html', data)
        text_contentclient = strip_tags(html_contentclient)

        # create the email, and attach the HTML version as well.
        msg1 = EmailMultiAlternatives("Commande validee", text_contentclient, from_email, [re_user.email])
        msg1.attach_alternative(html_contentclient, "text/html")
        msg1.send(fail_silently=False)
        
        
        html_content_admin = render_to_string('companies/admin.html', data)
        text_content_admin = strip_tags(html_content_admin)

        # create the email, and attach the HTML version as well.
        mail_admins("livraison disponible", text_content_admin, html_message=html_content_admin)
    messages.success(request, "transaction reussie, verifier votre email, verifier votre email")   
    return render(request, 'payment-paypal-done.html', {'order': order})

@csrf_exempt
@passenger_required 
def payment_p_canceled(request):
    return render(request, 'bis/payment-paypal-cancelled.html')