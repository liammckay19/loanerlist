from django.shortcuts import render

# Create your views here.
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def capture_image(request):
    if request.method == 'POST':
        # Handle the captured image here (e.g., save it to a file or process it)
        # You can access the image data in request.FILES['image'] if you use a form
        # For simplicity, we'll just return a success message for now
        return render(request, 'camera/capture.html', {'message': 'Image captured successfully'})
    return render(request, 'camera/capture.html',{'message': 'Image2 captured successfully'})