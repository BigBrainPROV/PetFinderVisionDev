from django.db import models


class Marks(models.Model):
    """
        id:
        latitude
        longtitude
        breed:
        color:
        type:
        image:
    """
    latitude = models.FloatField()
    longtitude = models.FloatField()
    breed = models.CharField(max_length=255)
    color = models.CharField(max_length=255)
    type = models.CharField(max_length=255)
    image = models.ImageField(upload_to='images/', blank=True, null=True)

    def __str__(self):
        return f'{self.latitude} {self.longtitude} {self.breed} {self.color} {self.type}'

    class Meta:
        verbose_name = 'Метка'
        verbose_name_plural = 'Метки'
