from django.db import models
from django.conf import settings

class SensorData(models.Model):
    RISK_LEVEL_CHOICES = [
        ('normal', 'ปกติ'),
        ('low', 'ต่ำ'),
        ('medium', 'กลาง'),
        ('high', 'สูง'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # เชื่อมโยงกับ User
    heart_rate = models.FloatField()  # อัตราการเต้นของหัวใจ
    skin_temperature = models.FloatField()  # อุณหภูมิผิว
    ambient_temperature = models.FloatField()  # อุณหภูมิโดยรอบ
    humidity = models.FloatField()  # ความชื้นโดยรอบ
    skin_resistance = models.FloatField()  # ความต้านทานผิวหนัง
    risk = models.CharField(max_length=10, choices=RISK_LEVEL_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)  # บันทึกเวลาที่ได้รับข้อมูล

    def __str__(self):
        return f"SensorData for {self.user.username} at {self.timestamp}"
