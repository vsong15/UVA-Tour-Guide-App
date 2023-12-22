from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    location = models.CharField(max_length=255)
    rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    comments = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    verified =  models.BooleanField(default=False)

    def __str__(self):
        return f"Review by {self.user.username} for {self.location}"
    