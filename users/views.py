from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.urls import reverse_lazy
from django.contrib.auth import get_user_model, login
from django.db.models import Sum, Count
from .forms import CustomUserCreationForm, CustomAuthenticationForm, UserProfileForm
from .face_utils import process_base64_image, get_face_encoding, verify_face, encode_face_data
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from vault.models import EncryptedFile, FileAccessLog
import json

class CustomLoginView(LoginView):
    form_class = CustomAuthenticationForm
    template_name = 'users/login.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['enable_face_login'] = True
        return context

@login_required
def dashboard(request):
    # Get user's file statistics
    total_files = EncryptedFile.objects.filter(user=request.user).count()
    total_size = EncryptedFile.objects.filter(user=request.user).aggregate(Sum('file_size'))['file_size__sum'] or 0
    recent_activities = FileAccessLog.objects.filter(
        file__user=request.user
    ).select_related('file').order_by('-timestamp')[:5]
    recent_activity_count = FileAccessLog.objects.filter(file__user=request.user).count()

    context = {
        'total_files': total_files,
        'total_size': total_size,
        'recent_activities': recent_activities,
        'recent_activity_count': recent_activity_count,
    }
    return render(request, 'users/dashboard.html', context)

def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created successfully. Please log in.')
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'users/signup.html', {'form': form})

@login_required
def profile(request):
    try:
        if request.method == 'POST':
            form = UserProfileForm(request.POST, instance=request.user)
            if form.is_valid():
                form.save()
                messages.success(request, 'Profile updated successfully.')
                return redirect('profile')
        else:
            form = UserProfileForm(instance=request.user)
        
        return render(request, 'users/profile.html', {
            'form': form,
            'user': request.user
        })
    except Exception as e:
        print(f"Profile error: {str(e)}")  # For debugging
        messages.error(request, 'An error occurred while loading your profile.')
        return redirect('dashboard')

@login_required
@require_POST
def face_setup(request):
    try:
        data = json.loads(request.body)
        image_data = data.get('image')
        
        if not image_data:
            return JsonResponse({
                'success': False,
                'message': 'No image data provided.'
            }, status=400)
        
        # Process the image
        image_array = process_base64_image(image_data)
        if image_array is None:
            return JsonResponse({
                'success': False,
                'message': 'Could not process the image. Please try again.'
            }, status=400)
        
        # Get face encoding
        face_encoding = get_face_encoding(image_array)
        if face_encoding is None:
            return JsonResponse({
                'success': False,
                'message': 'No face detected in the image or could not encode face.'
            }, status=400)
        
        # Save face encoding
        request.user.face_encoding = encode_face_data(face_encoding)
        if request.user.face_encoding is None:
            return JsonResponse({
                'success': False,
                'message': 'Could not save face encoding. Please try again.'
            }, status=500)
        
        request.user.use_face_auth = True
        request.user.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Face authentication setup successful.'
        })
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Invalid request data.'
        }, status=400)
    except Exception as e:
        print(f"Error in face_setup: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': 'An error occurred during setup.'
        }, status=500)

@require_POST
def face_login(request):
    try:
        data = json.loads(request.body)
        username = data.get('username')
        image_data = process_base64_image(data.get('image'))
        
        User = get_user_model()
        user = User.objects.filter(username=username, use_face_auth=True).first()
        
        if not user or not user.face_encoding:
            return JsonResponse({
                'success': False,
                'message': 'User not found or face authentication not set up.'
            }, status=400)
        
        if verify_face(user.face_encoding, image_data):
            login(request, user)
            return JsonResponse({
                'success': True,
                'redirect_url': reverse_lazy('dashboard')
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Face verification failed.'
            }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)
