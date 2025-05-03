from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import SensorData
from django.contrib.auth.decorators import login_required
from .forms import SensorDataForm  # import SensorDataForm
from django.contrib.auth import get_user_model
from django.contrib import messages
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.utils import timezone
from datetime import timedelta



@csrf_exempt
#@login_required
def receive_sensor_data(request):
    print("🚨 ฟังก์ชันถูกเรียกแล้ว")
    if request.method == "POST":
        try:
            data = json.loads(request.body.decode("utf-8"))
            user_id = data.get("user_id")
            heart_rate = data.get("heart_rate")
            skin_temperature = data.get("skin_temperature")
            ambient_temperature = data.get("ambient_temperature")
            humidity = data.get("humidity")
            skin_resistance = data.get("skin_resistance")
            risk = data.get("risk", "low")

            User = get_user_model()
            user = User.objects.get(id=user_id)

            sensor_data = SensorData.objects.create(
                user=user,
                heart_rate=heart_rate,
                skin_temperature=skin_temperature,
                ambient_temperature=ambient_temperature,
                humidity=humidity,
                skin_resistance=skin_resistance,
                risk=risk,
            )

            # ✅ Broadcast ข้อมูลไปยัง WebSocket
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                "sensor_group",
                {
                    "type": "send_sensor_data",
                    "data": {
                        "user_id": user.id,
                        "timestamp": str(sensor_data.timestamp),
                        "heart_rate": sensor_data.heart_rate,
                        "skin_temperature": sensor_data.skin_temperature,
                        "ambient_temperature": sensor_data.ambient_temperature,
                        "humidity": sensor_data.humidity,
                        "skin_resistance": sensor_data.skin_resistance,
                        "risk": sensor_data.risk,
                    },
                }
            )
            
            print("✅ ส่งข้อมูลเข้าสู่ WebSocket แล้ว:", sensor_data.heart_rate)
            return JsonResponse({"status": "success"})

        except Exception as e:
            import traceback
            traceback.print_exc()  # 👈 แสดง traceback ใน log
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "Invalid request method"}, status=405)




#@login_required
#def receive_sensor_data(request):
#    if request.method == "POST":
#        form = SensorDataForm(request.POST)
#        if form.is_valid():
#            # ตั้งค่า user เป็นผู้ใช้ที่ล็อกอินอยู่
#            sensor_data = form.save(commit=False)
#            sensor_data.user = request.user  # ตั้งค่า user เป็นผู้ใช้ที่ล็อกอิน
#            sensor_data.save()  # บันทึกข้อมูล
#            return redirect("index")  # เปลี่ยนไปที่หน้ารายการข้อมูล
#    else:
#        form = SensorDataForm()
#
#    return render(request, 'sensor_data_form.html', {'form': form})
#


@login_required
def display_data(request):
    seven_days_ago = timezone.now() - timedelta(days=7)
    sensor_data = SensorData.objects.filter(
        user=request.user,
        timestamp__gte=seven_days_ago
    ).order_by("-timestamp")

    return render(request, "sensor/display_data.html", {"sensor_data": sensor_data})
