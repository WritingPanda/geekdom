import datetime

from django.db import models
from django.contrib.auth.models import User

from userena.models import UserenaBaseProfile
from easy_thumbnails.fields import *

from manager.helpers import pusher_call

class UserProfile(UserenaBaseProfile):
  user = models.OneToOneField(User, unique=True, verbose_name=('user'), related_name='my_profile')
  company_name = models.CharField(max_length=200, blank=True)
  office_num = models.CharField(max_length=200, blank=True)

  bio = models.TextField(blank=True)

  address = models.CharField(max_length=200, blank=True)
  city = models.CharField(max_length=200, blank=True)
  state = models.CharField(max_length=200, blank=True)
  zipcode = models.CharField(max_length=200, blank=True)

  phone_number = models.CharField(max_length=200, blank=True)
  twitter = models.CharField(max_length=200, blank=True)
  facebook = models.CharField(max_length=200, blank=True)
  gchat = models.CharField(max_length=200, blank=True)
  skype = models.CharField(max_length=200, blank=True)
  linkedin = models.CharField(max_length=200, blank=True)
  website = models.CharField(max_length=200, blank=True)
  
  skills = models.CharField(max_length=200, blank=True)

  available_for_office_hours = models.CharField(max_length=200, blank=True)
  available_for_workshops = models.CharField(max_length=200, blank=True)

  has_parking_pass = models.BooleanField()
  has_office_key = models.BooleanField()
  has_elevator_fob = models.BooleanField()
  
  membership_type = models.ForeignKey("MembershipType", blank=True, null=True)
  custom_membership_price = models.DecimalField(blank=True, null=True, max_digits=5, decimal_places=2)

  notes = models.TextField(blank=True, help_text="These notes are not visible to members.")
  
  # Flomio fields
  flomio_tag_uuid = models.CharField(max_length=200, blank=True)

  def __str__(self): return self.user.get_full_name()
  def __unicode__(self): return u'%s' % (self.user.get_full_name())  
  class Meta: ordering = ["user__first_name"]
      
  def get_absolute_url(self): return "/members/" + str(self.user.id)  
  def title(self): return self.user.get_full_name()
  def is_checked_in(self):
    now = datetime.datetime.now()
    checkin = Checkin.objects.filter(userprofile = self).filter(expires_at__gte = now)
    if len(checkin) > 0:
      return True
    else:
      return False

  def check_in(self, method=False):
    now = datetime.datetime.now()
    checkins = Checkin.objects.filter(userprofile = self).filter(expires_at__gte = now)

    if method == "kiosk": method = 1
    if method == "foursquare": method = 2
    if method == "flomio": method = 3
    if method == "desktop": method = 4

    if checkins.count() == 0:
      checkin = Checkin.objects.get_or_create(
        userprofile = self, 
        expires_at = datetime.datetime.now() + datetime.timedelta(hours = 8),
        method = method,
        )
      pusher_call(channel="geekdom", event="checkin", payload=self.user.id)
      return True
    else:
      return False

  def check_out(self):
    now = datetime.datetime.now()
    checkins = Checkin.objects.filter(userprofile = self).filter(expires_at__gte = now)
    if checkins.count() > 0:
      for checkin in checkins:
        checkin.expires_at = now - datetime.timedelta(minutes = 1)
        checkin.save()
      pusher_call(channel="geekdom", event="checkout", payload=self.user.id)
      return True
    else:
      return False
  
  def toggle_check_in(self, check_in_method=1):
      ''' Toggles the check_in status of the user '''
      # import pdb;pdb.set_trace()
      if not self.is_checked_in():
          self.check_in(method = check_in_method)
          return "User is now checked in"
      else:
          self.check_out()
          return "User is now checked out"


class MembershipType(models.Model):
  name = models.CharField(max_length=200)
  price = models.DecimalField(max_digits=5, decimal_places=2)
  DURATION_CHOICES = (('mo', 'Monthly'),('dy', 'Daily'),('wk', 'Weekly'),('qu', 'Quarterly'),('ba', 'Bi-annually'),('yr', 'Yearly'),)
  duration = models.CharField(max_length=2, choices=DURATION_CHOICES)

  def __str__(self): return self.name
  def __unicode__(self): return u'%s' % (self.name)
  def total_membership(self): return self.userprofile_set.all().count()
  def total_revenue(self): return self.userprofile_set.all().count() * self.price



class BackgroundImage(models.Model):
    url = models.CharField(max_length=200, blank=True)



class Checkin(models.Model):
  userprofile = models.ForeignKey(UserProfile)
  expires_at = models.DateTimeField()
  occurred_on = models.DateTimeField(auto_now_add = True)
  updated_on = models.DateTimeField(auto_now = True) 
  METHOD_CHOICES = (
    ('1', 'Kiosk'),
    ('2', 'Foursquare'),
    ('3', 'Flomio'),
    ('4', 'Desktop'),
  )
  method = models.IntegerField(default = 1, choices=METHOD_CHOICES)
 
  def __str__(self): return self.userprofile.user.get_full_name + " - " + self.expires_at




class Event(models.Model):
  name = models.CharField(max_length=200)
  description = models.TextField()
  starts_at = models.DateTimeField()
  ends_at = models.DateTimeField()
  added_by = models.ForeignKey(User)
  link = models.URLField(max_length=200, blank=True)

  publish_to_site = models.BooleanField()

  def __str__(self): return self.name
  def __unicode__(self): return u'%s' % (self.name)




class CtaBanner(models.Model):
  text = models.CharField(max_length=200)
  link = models.URLField(max_length=200, blank=True)


