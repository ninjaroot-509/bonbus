from django.shortcuts import redirect, render
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect

from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import TemplateView

from django.contrib.auth.mixins import LoginRequiredMixin
from ..models import *

from ..forms import *
from django.db import transaction
from django.views.generic import CreateView, ListView, UpdateView
from django.urls import reverse_lazy

from django.contrib import messages
from time import gmtime, strftime
import datetime
from datetime import date
from django.http import HttpResponseRedirect
from django.utils import timezone

@login_required
def testimonial(request):
    re_user = request.user
    testi = Testimonial.objects.filter(user=re_user)
    if request.method == 'POST':
        message = request.POST['message']
        testimonial = Testimonial.objects.create(user=re_user, message=message)
    return render(request, 'bis/testi.html', {'testi':testi})

@login_required
def bevalide(request):
    return render(request, 'bis/bevalide.html')

class CompanyListView(ListView):
    model = User
    context_object_name = 'comps'

    def get_queryset(self):
        comps = User.objects.filter(user=self.request.user.company)
        paginator = Paginator(comps, 10)
        page = self.request.GET.get('page')
        try:
            comps = paginator.page(page)
        except PageNotAnInteger:
            comps = paginator.page(1)
        except EmptyPage:
            comps = paginator.page(paginator.num_pages)
        return comps

def profile_view(request, slug):
	p = Profile.objects.filter(slug=slug).first()
	u = p.user
	return render(request, "companies/profile.html", locals())

login_required
def profile(request):
    return render(request, 'companies/myprofile.html')

class ProfileUpdateView(LoginRequiredMixin, TemplateView):
    user_form = UserForm
    profile_form = ProfileForm
    template_name = 'companies/profile_update.html'

    def post(self, request):

        post_data = request.POST or None
        file_data = request.FILES or None

        user_form = UserForm(post_data, instance=request.user)
        profile_form = ProfileForm(post_data, file_data, instance=request.user.profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'votre profile est mise-a-jour')
            return HttpResponseRedirect(reverse_lazy('profile'))

        context = self.get_context_data(
                                        user_form=user_form,
                                        profile_form=profile_form
                                    )

        return self.render_to_response(context)     

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

def contact(request):
    if request.method == 'POST':
        f = ContactusForm(request.POST)
        if f.is_valid():
            name = f.cleaned_data['fullname']
            sender = f.cleaned_data['email']
            subject = "{}:{}, fek kontakte Administrasyon an".format(name, sender)
            message = "Subject: {}\n\nMessage: {}".format(f.cleaned_data['subject'], f.cleaned_data['message'])
            mail_admins(subject, message)
            f.save()
            messages.info(request, "mesaj ou a ale avek sikse")
            return redirect('core:contact')
    else:
        f = ContactusForm()
    return render(request, 'bis/contact.html', {'form': f})

def about(request):
    return render(request, 'bis/about.html')

def faq(request):
    return render(request, 'bis/faq.html')
    
def howork(request):
    return render(request, 'bis/howork.html')

class SignUpView(TemplateView):
    template_name = 'registration/signup.html'


def home(request):
    today = date.today()
    now1 = datetime.datetime.now().time()
    # now = datetime.datetime.now().strftime("%Y, %m, %d, %H, %M")
    now = timezone.now()
    # nowfilter = now + datetime.timedelta(hours = 1)
    # timefilter = nowfilter.time().strftime('%H:%M')
    items = Bus.objects.filter(is_active=True).order_by('-date_depart')
    testi = Testimonial.objects.all()
    if request.user.is_authenticated:
        if request.user.is_passenger:
            return redirect('passengers:viewp')
        if request.user.is_company:
            return redirect('companies:mybus')
        else:
            return redirect('bevalide')
    return render(request, 'bis/index.html', locals())

