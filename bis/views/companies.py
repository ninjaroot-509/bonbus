from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, ListView, UpdateView, DeleteView
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.core.mail import send_mail, BadHeaderError, mail_admins
from django.urls import reverse_lazy, reverse
from django.db.models.signals import post_save
from django.template import Context
from django.template.loader import render_to_string, get_template
from django.utils.html import strip_tags
from django.contrib.auth import authenticate
from django.core.mail import EmailMultiAlternatives
import datetime
from datetime import date
from django.db.models import Q
from django.http import HttpResponseRedirect

from ..decorators import company_required
from ..forms import *
from ..models import *
from django.utils import timezone

@company_required
def check(request, code):
    Order.objects.filter(ref_code=code).update(utiliser=True)
    Reservation.objects.filter(code=code).update(utiliser=True)
    send = Reservation.objects.get(code=code)
    from_email = settings.EMAIL_HOST_USER
    to_email = [send.client.email]
    user_message = "%s ticket verifier avec succes comme etant utiliser \n depart: %s \n destination: %s \n BusHaiti, Merci!!!" % (send.client.username, send.source, send.destination)
    send_mail("verification ticket", user_message, from_email, to_email, fail_silently=False)
    mail_admins("1 ticket verifier!", user_message)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@company_required
def uncheck(request, code):
    Order.objects.filter(ref_code=code).update(utiliser=False)
    Reservation.objects.filter(code=code).update(utiliser=False)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@company_required
def search_reser(request):
    query = request.GET.get('q','')
    #The empty string handles an empty "request"
    if query:
            # queryset = (Q(code__icontains=query))
            #I assume "text" is a field in your model
            #i.e., text = model.TextField()
            #Use | if searching multiple fields, i.e., 
            queryset = (Q(code__icontains=query)|Q(prenom__icontains=query)|Q(nom__icontains=query)|Q(id_number__icontains=query))
            results = Reservation.objects.filter(queryset).distinct().order_by('-date')
    else:
       results = []
    return render(request, 'companies/all_re.html', {'items':results, 'query':query})

@company_required
def viewcomp(request):
    return render(request, 'companies/index.html', {})

@company_required
def reservation_listes(request):
    items = Reservation.objects.filter(author=request.user).order_by('-date')
    return render(request, 'companies/all_re.html', locals())

@company_required
def reservation_at_this_time(request):
    today = date.today()
    now1 = datetime.datetime.now().time()
    # now = datetime.datetime.now().strftime("%Y, %m, %d, %H, %M")
    now = timezone.now()
    # nowfilter = now + datetime.timedelta(hours = 1)
    # timefilter = nowfilter.time().strftime('%H:%M')
    items = Bus.objects.filter(author=request.user).order_by('-date_depart')
    return render(request, 'companies/at_time.html', locals())

@company_required
def mybus(request):
    items = Bus.objects.filter(author=request.user).order_by('-date_depart')
    return render(request, 'companies/mybus.html', locals())

@company_required
def bus_at_this_time(request):
    now1 = datetime.datetime.now().time()
    now = datetime.datetime.now()
    nowfilter = now + datetime.timedelta(hours = 1)
    # timefilter = nowfilter.time().strftime('%H:%M')
    items = Bus.objects.filter(author=request.user).order_by('-date_depart')
    return render(request, 'companies/bus_at_time.html', locals())

@company_required
def edit_n_places(request):
    context = {}
    if request.method == 'POST':
        id_r = request.POST.get('bus_id')
        n_places = request.POST.get('places')
        try:
            bus = Bus.objects.get(id=id_r)
            Bus.objects.filter(id=bus.id).update(nombre_place=n_places)
        except Bus.DoesNotExist:
            messages.error(request, "Désolé, le bus n'existe pas!!")
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

class CompanySignUpView(CreateView):
    model = User
    form_class = CompanySignUpForm
    template_name = 'registration/signup_form.html'

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'company'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('profile-update')
        
def register_companies(request):
    if request.method == 'POST':
        form = UserFormCompanies(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password1 = form.cleaned_data['password1']
            password2 = form.cleaned_data['password2']
            addresse = request.POST.get('addresse')
            ville = request.POST.get('ville')
            telephone = request.POST.get('telephone')
            q1 = request.POST.get('q1')
            q2 = request.POST.get('q2')
            q3 = request.POST.get('q3')
            
            if User.objects.exclude(pk=instance.pk).filter(username=username).exists():
                messages.warning(request, "le Nom d'utilisateur (%s) est déjà utilisé!!" % username)
                HttpResponseRedirect(request.META.get('HTTP_REFERER'))
            
            if password1 and password2 and password1 != password2:
                messages.warning(request, "Les mots de passe saisis ne correspondent pas!!")
                HttpResponseRedirect(request.META.get('HTTP_REFERER'))
            else:
                user.set_password(password1)
                user.save()
                user = authenticate(username=username, email=email, password=password1)
                if user is not None:
                    if user.is_active:
                        login(request, user)

                from_email = settings.EMAIL_HOST_USER
                to_email = [email]
        
                subject = "nouvelle compagnie ({})".format(username)
                message = "l'entreprise {} vient juste d'envoyer une demande adhération! \n Ville: {} \n Addresse: {} \n Telephone: {} \n Comment avez-vous connu BusHaiti?: \n{}\n \n Quelles sont vos motivations pour adhérer à BusHaiti?: \n{}\n \n Si vous avez des idées de projets, de contribution pour/dans l'association?: \n{}\n \n BusHaiti, Merci!!!.".format(username, ville, addresse, telephone, q1, q2, q3)
                mail_admins(subject, message)
                
                message1 = "vous venez d'envoyer une demande adhération! \n nom de l'entreprise: {} \n Ville: {} \n Addresse: {} \n Telephone: {} \n Comment avez-vous connu BusHaiti?: \n{}\n \n Quelles sont vos motivations pour adhérer à BusHaiti?: \n{}\n \n Si vous avez des idées de projets, de contribution pour/dans l'association?: \n{}\n \n BusHaiti, Merci!!!.".format(username, ville, addresse, telephone, q1, q2, q3)
                send_mail(subject, message1, from_email, to_email, fail_silently=False)
                
                messages.success(request, "La Demande a ete envoyer avec success, d'ici peu on vous recontactera. BusHaiti, Merci!!")
                return redirect('profile-update')
        else:
            messages.warning(request, "Assurez-vous de bien remplir tous les champs, ou Utilisateur deja existant!!")
            HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    return render(request, 'registration/signup_form_companies.html', {'form':UserFormCompanies()})        
        
    
@method_decorator([login_required, company_required], name='dispatch')  
class AddBusView(LoginRequiredMixin, CreateView):
    model = Bus
    template_name = 'companies/addbus.html'
    form_class = BusForm
    success_url = reverse_lazy('companies:mybus')
    
    # def get_form_kwargs(self):
    #     kwargs = super().get_form_kwargs()
    #     kwargs['user'] = self.request.user
    #     return kwargs

    def form_valid(self, form):
        form.instance.author = self.request.user
        # new_bus = self.get_object()
        
        subject1 = "{} new bus {}".format(form.instance.author.username, form.instance.name)
        message1 = "l'entreprise {} vient juste d'ajouter un bus ({}).".format(form.instance.author.username, form.instance.name)
        mail_admins(subject1, message1)
        
        from_email = settings.EMAIL_HOST_USER
        to_email = [form.instance.author.email]
        user_message = "votre nouveau bus (%s) a ete ajouter avec success" % (form.instance.name)
        send_mail("vous venez d'ajouter un nouveau bus", user_message, from_email, to_email, fail_silently=False)

        return super().form_valid(form)

    def test_func(self):
        bus = self.get_object()
        if self.request.user == bus.author:
            return True
        return False
    
@method_decorator([login_required, company_required], name='dispatch')  
class BusUpdateView(LoginRequiredMixin, UpdateView):
    model = Bus
    template_name = 'companies/addbus.html'
    success_url = reverse_lazy('companies:mybus')
    form_class = BusForm

    # def get_form_kwargs(self):
    #     kwargs = super().get_form_kwargs()
    #     kwargs['user'] = self.request.user
    #     return kwargs

    def form_valid(self, form):
        form.instance.author = self.request.user
        # new_bus = self.get_object()
        
        subject2 = "l'entreprise {} a modifier son bus ({})".format(form.instance.author.username, form.instance.name)
        message2 = "l'entreprise {} vient juste de modifier son bus ({}).".format(form.instance.author.username, form.instance.name)
        mail_admins(subject2, message2)
        
        from_email = settings.EMAIL_HOST_USER
        to_email = [form.instance.author.email]
        user_message = "votre bus (%s) a ete modifier avec success" % (form.instance.name)
        send_mail("vous venez de modifier un bus", user_message, from_email, to_email, fail_silently=False)
    
        return super().form_valid(form)

    def test_func(self):
        bus = self.get_object()
        if self.request.user == bus.author:
            return True
        return False

@method_decorator([login_required, company_required], name='dispatch')  
class BusDeleteView(LoginRequiredMixin, DeleteView):
    template_name = 'companies/bus_delete.html'
    model = Bus
    success_url = reverse_lazy('companies:mybus')
    
@method_decorator([login_required, company_required], name='dispatch')  
class AddTaxiView(LoginRequiredMixin, CreateView):
    model = Bus
    template_name = 'companies/addbus.html'
    form_class = TaxiForm
    success_url = reverse_lazy('companies:mybus')
    
    # def get_form_kwargs(self):
    #     kwargs = super().get_form_kwargs()
    #     kwargs['user'] = self.request.user
    #     return kwargs

    def form_valid(self, form):
        form.instance.author = self.request.user
        # new_bus = self.get_object()
        
        subject1 = "{} new bus {}".format(form.instance.author.username, form.instance.name)
        message1 = "l'entreprise {} vient juste d'ajouter un bus ({}).".format(form.instance.author.username, form.instance.name)
        mail_admins(subject1, message1)
        
        from_email = settings.EMAIL_HOST_USER
        to_email = [form.instance.author.email]
        user_message = "votre nouveau bus (%s) a ete ajouter avec success" % (form.instance.name)
        send_mail("vous venez d'ajouter un nouveau bus", user_message, from_email, to_email, fail_silently=False)

        return super().form_valid(form)

    def test_func(self):
        bus = self.get_object()
        if self.request.user == bus.author:
            return True
        return False
    
@method_decorator([login_required, company_required], name='dispatch')  
class TaxiUpdateView(LoginRequiredMixin, UpdateView):
    model = Bus
    template_name = 'companies/addbus.html'
    success_url = reverse_lazy('companies:mybus')
    form_class = TaxiForm

    # def get_form_kwargs(self):
    #     kwargs = super().get_form_kwargs()
    #     kwargs['user'] = self.request.user
    #     return kwargs

    def form_valid(self, form):
        form.instance.author = self.request.user
        # new_bus = self.get_object()
        
        subject2 = "l'entreprise {} a modifier son bus ({})".format(form.instance.author.username, form.instance.name)
        message2 = "l'entreprise {} vient juste de modifier son bus ({}).".format(form.instance.author.username, form.instance.name)
        mail_admins(subject2, message2)
        
        from_email = settings.EMAIL_HOST_USER
        to_email = [form.instance.author.email]
        user_message = "votre bus (%s) a ete modifier avec success" % (form.instance.name)
        send_mail("vous venez de modifier un bus", user_message, from_email, to_email, fail_silently=False)
    
        return super().form_valid(form)

    def test_func(self):
        bus = self.get_object()
        if self.request.user == bus.author:
            return True
        return False

@method_decorator([login_required, company_required], name='dispatch')  
class TaxiDeleteView(LoginRequiredMixin, DeleteView):
    template_name = 'companies/bus_delete.html'
    model = TaxiForm
    success_url = reverse_lazy('companies:mybus')