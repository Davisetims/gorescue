from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    USER_TYPES = [
        ('responder', 'Responder'),
        ('victim', 'victim'),
    ]
    first_name = models.CharField(max_length=40, null=True, blank=True)
    last_name = models.CharField(max_length=40, null=True, blank=True)
    email = models.EmailField(max_length=254, unique=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    user_type = models.CharField(max_length=10, choices=USER_TYPES, default='victim')
                                
    
    def __str__(self):
        return f"{self.username} - {self.user_type}"

class EmergencyType(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name

class EmergencyResponder(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, limit_choices_to={'user_type': 'responder'})
    organization = models.CharField(max_length=200)
    contact_number = models.CharField(max_length=20)
    emergency_types = models.ManyToManyField(EmergencyType)
    is_available = models.BooleanField(default=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    last_updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.get_full_name()} ({self.organization})"

class EmergencyAlert(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('dispatched', 'Responder Dispatched'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'user_type': 'victim'})
    emergency_type = models.ForeignKey(EmergencyType, on_delete=models.PROTECT, null=True, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    description = models.TextField(blank=True)
    assigned_responder = models.ForeignKey(
        EmergencyResponder, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    
    def __str__(self):
        return f"{self.emergency_type} alert at {self.timestamp}"
    
    class Meta:
        ordering = ['-timestamp']

    

class EmergencyMessage(models.Model):
    alert = models.ForeignKey(EmergencyAlert, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_from_responder = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['timestamp']
    
    def __str__(self):
        return f"Message for alert {self.alert.id} at {self.timestamp}"
