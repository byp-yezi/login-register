from django.test import TestCase
import datetime
# from login import models
# Create your tests here.
from django.utils import timezone

print(datetime.datetime.utcnow().replace(tzinfo=timezone.utc))
# print(models.ConfirmString.objects.filter(id=2) + datetime.timedelta(7))

# 2023-08-21 06:34:43.850911