from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.html import escape, mark_safe
from django.urls import reverse
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from PIL import Image
from django.db.models import Sum
from autoslug import AutoSlugField
from django.core.mail import send_mail, BadHeaderError, mail_admins
from phonenumber_field.modelfields import PhoneNumberField
from ckeditor.fields import RichTextField
from randomslugfield import RandomSlugField
from django_slugify_processor.text import slugify
# Create your models here.


class User(AbstractUser):
    is_company = models.BooleanField(default=False)
    is_passenger = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = 'Utilisateur'
        verbose_name_plural = 'Tout les Utilisateurs'

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True)
    photo = models.ImageField(upload_to='profile_pics/', null=True, blank=True, help_text="Entrer une photo de vous, c'est pas obligatoire!")
    numero = PhoneNumberField(blank=True, help_text='Votre numero pesonnel!')
    slug = AutoSlugField(populate_from='user')
    
    class Meta:
        verbose_name = 'Profile'
        verbose_name_plural = 'Tout les Profile'
    
    def __str__(self):
        return self.user.username
    
    # def save(self, *args, **kwargs):
    #     super().save(*args, **kwargs)

    #     img = Image.open(self.photo.path)

    #     if img.height > 300 or img.width > 300:
    #         output_size = (300, 300)
    #         img.thumbnail(output_size)
    #         img.save(self.photo.path)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

def email_new_user(sender, **kwargs):
    if kwargs["created"]:  # only for new users
        new_user = kwargs["instance"] 
        print(new_user.email)
        subject = "New user (%s)" % sender.username
        message = "l'utisateur %s vient juste de creer un compte." % sender.username
        message_to_user = "Bienvenue et merci d'avoir fait confiance a BusHaiti"
        email_user = "%s" % new_user.email
        mail_admins(subject, message)
        # send_mail(subject, message_to_user, 'stanleycastin@gmail.com', email_user, fail_silently=False)
post_save.connect(email_new_user, sender=User)

    
class Contactus(models.Model):
    name = models.CharField(max_length=200, help_text="Name of the sender")
    email = models.EmailField(max_length=200)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
 
    class Meta:
        verbose_name = 'Message de Contact'
        verbose_name_plural = 'Listes des Messages de Contact'
 
    def __str__(self):
        return self.name + "-" +  self.email
    

class Category(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField()
    description = models.TextField()
    image = models.ImageField()
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Categorie'
        verbose_name_plural = 'Tout les Categories'
        
    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("category", kwargs={
            'slug': self.slug
        })

# class BusManager(models.Manager):
#     def get_queryset(self):
#         now = datetime.datetime.now().strftime('%I:%M:%S')
#         min_time = now #now - 30 minutes
#         return super(BusManager, self).filter(time__gt=now).update(nombre_place=55)
import string
import random

def rand_slug():
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(6))
    
class Bus(models.Model):
    author = models.ForeignKey(User, 
                               related_name='item_auth', on_delete=models.CASCADE)
    name = models.CharField(max_length=130)    
    source = models.CharField(choices=settings.CHOICES_CITY_BUS, max_length=50)
    destination = models.CharField(choices=settings.CHOICES_CITY_BUS, max_length=50)
    prix = models.FloatField()
    slug = AutoSlugField(populate_from=['name','destination'], unique=True)
    nombre_place = models.IntegerField(null=True, blank=True, help_text="Seulement pour les bus!")
    description = models.TextField()
    # date = models.DateField()
    # time = models.TimeField()
    date_depart = models.DateTimeField(null=True, blank=True, help_text="Seulement pour les bus! \n example: jj/mm/AAAA h:m")
    image = models.ImageField(upload_to='bus_photos/%Y/%m/%d/')
    photo_1 = models.ImageField(upload_to='bus_photos/%Y/%m/%d/', blank=True, null=True)
    photo_2 = models.ImageField(upload_to='bus_photos/%Y/%m/%d/', blank=True, null=True)
    photo_3 = models.ImageField(upload_to='bus_photos/%Y/%m/%d/', blank=True, null=True)
    photo_4 = models.ImageField(upload_to='bus_photos/%Y/%m/%d/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_taxi = models.BooleanField(default=False)
    # objects = BusManager()
    
    class Meta:
        ordering = ('-date_depart',)
        verbose_name = 'Auto-Mobile'
        verbose_name_plural = 'Listes des Auto-Mobiles'

    def __str__(self):
        return 'bus {}'.format(self.name)
    
    def get_absolute_url(self):
        return reverse("passengers:bus_detail", kwargs={
            'slug': self.slug
        })
    
    def get_add_ticket_url(self):
        return reverse("passengers:add-ticket", kwargs={
            'slug': self.slug
        })

    def get_remove_ticket_url(self):
        return reverse("passengers:remove-ticket", kwargs={
            'slug': self.slug
        })
        
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(rand_slug() + "-" + self.name)
        super(Bus, self).save(*args, **kwargs)

CHOICES_TYPE_ID_R = (
    ('C', 'CIN'),
    ('P', 'Passport'),
    ('N', 'NIF'),
)

class Reservation(models.Model):
    author = models.ForeignKey(User,related_name='request_author', on_delete=models.CASCADE)
    client = models.ForeignKey(User,related_name='request_client', on_delete=models.CASCADE)
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    id_type = models.CharField(choices=CHOICES_TYPE_ID_R, max_length=1)
    id_number = models.CharField(max_length=250)
    name = models.CharField(max_length=130)
    source = models.CharField(max_length=130)
    destination = models.CharField(max_length=130)
    code = models.CharField(max_length=50)
    prix = models.FloatField()
    quantite = models.IntegerField()
    date_depart = models.DateTimeField()
    date = models.DateField()
    image = models.ImageField(upload_to='reservation/%Y/%m/%d/')
    utiliser = models.BooleanField(default=False)
    
    class Meta:
        ordering = ('-date',)
        verbose_name = 'Reservation'
        verbose_name_plural = 'Listes des Reservations'

    def __str__(self):
        return 'bus {}'.format(self.name)

class OrderItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)
    item = models.ForeignKey(Bus, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    
    class Meta:
        verbose_name = 'Panier'
        verbose_name_plural = 'Tout les tickets'
    
    def __str__(self):
        return f"{self.quantity} of {self.item.name}"

    def get_total_item_prix(self):
        return self.quantity * self.item.prix

    def get_final_prix(self):
        return self.get_total_item_prix()


class Order(models.Model):
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE)
    ref_code = models.CharField(max_length=20)
    items = models.ManyToManyField(OrderItem)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField()
    ordered = models.BooleanField(default=False)
    billing_address = models.ForeignKey('BillingAddress', related_name='billing_address', on_delete=models.SET_NULL, blank=True, null=True)
    payment = models.ForeignKey('Payment', on_delete=models.SET_NULL, blank=True, null=True)
    coupon = models.ForeignKey('Coupon', on_delete=models.SET_NULL, blank=True, null=True)
    payer = models.BooleanField(default=False)
    utiliser = models.BooleanField(default=False)
    refund_requested = models.BooleanField(default=False)
    refund_granted = models.BooleanField(default=False)

    '''
    1. Item added to cart
    2. Adding a BillingAddress
    (Failed Checkout)
    3. Payment
    4. Being delivered
    5. Received
    6. Refunds
    '''
    
    class Meta:
        verbose_name = 'Commande'
        verbose_name_plural = 'Listes des Commandes Effectuées'

    def __str__(self):
        return self.user.username

    def get_total(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.get_final_prix()
        if self.coupon:
            total -= self.coupon.amount
        return total
    
    def get_ticket_total(self):
        totale = 0
        for order_item in self.items.all():
            totale += order_item.quantity
        return totale

CHOICES_TYPE_ID = (
    ('C', 'CIN'),
    ('P', 'Passport'),
    ('N', 'NIF'),
)

class BillingAddress(models.Model):
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE)
    id_type = models.CharField(choices=CHOICES_TYPE_ID, max_length=1)
    id_number = models.CharField(max_length=250)
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    default = models.BooleanField(default=False)

    def __str__(self):
        return f"payer par {self.user.username}"

    class Meta:
        verbose_name = 'Facturation details'
        verbose_name_plural = 'Informations des facturations'


class Payment(models.Model):
    charge_id = models.CharField(max_length=50)
    user = models.ForeignKey(User,
                             on_delete=models.SET_NULL, blank=True, null=True)
    amount = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True, editable=False)
    
    class Meta:
        verbose_name = 'Paiment'
        verbose_name_plural = 'Informations des Paiment Effectuées'
    
    def __str__(self):
        return self.user.username


class Coupon(models.Model):
    code = models.CharField(max_length=15)
    amount = models.FloatField()
    
    def __str__(self):
        return self.code


class Refund(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    reason = models.TextField()
    accepted = models.BooleanField(default=False)
    email = models.EmailField()
    
    class Meta:
        verbose_name = 'Remboursement'
        verbose_name_plural = 'Remboursements listes'
    
    def __str__(self):
        return f"{self.pk}"

class Wishlist(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)# here CASCADE is the behavior to adopt when the referenced object(because it is a foreign key) is deleted. it is not specific to django,this is an sql standard.
    wished_bus = models.ForeignKey(Bus,on_delete=models.CASCADE)
    slug = models.CharField(max_length=30,null=True,blank=True)
    added_date = models.DateTimeField(auto_now_add=True, editable=False)
    
    class Meta:
        verbose_name = 'Bus Favori'
        verbose_name_plural = 'Listes des Bus Favoris'
    
    def __str__(self):
        return self.wished_bus.name
        
class BroadCast_Email(models.Model):
    sujet = models.CharField(max_length=200)
    creer = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=True)
    message = RichTextField()

    def __str__(self):
        return self.sujet

    class Meta:
        verbose_name = "Diffuser un e-mail à tous les membres"
        verbose_name_plural = "Courriel BroadCast"
        

class Wallet(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    montant = models.FloatField(blank=True, null=True, default=0)
    date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return '{} a {} Gourdes'.format(self.user.username, self.montant) # TODO
        
        
class WalletTransac(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    montant = models.FloatField(blank=True, null=True, default=0)
    date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return '{} a ajoute {} Gourdes, {}'.format(self.user.username, self.montant, self.date) # TODO

class Testimonial(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    message = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return '{} a ajoute un testi le {}'.format(self.user.username,self.date) # TODO