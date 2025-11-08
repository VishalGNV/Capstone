from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.conf import settings
from .models import EncryptedFile, FileAccessLog
from .forms import FileUploadForm, FileDownloadForm
from .utils import save_encrypted_file, get_decrypted_file
import mimetypes
import os
from django.db.models import Sum

# Create your views here.

@login_required
def upload_file(request):
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            password = form.cleaned_data['password']
            
            try:
                # Read file content
                file_content = file.read()
                
                # Encrypt file data
                from .utils import encrypt_file
                encrypted_data, salt, iv = encrypt_file(file_content, password)
                
                # Create file record with encrypted data stored in DB
                encrypted_file = EncryptedFile.objects.create(
                    user=request.user,
                    filename=file.name,
                    original_filename=file.name,
                    file_type=file.content_type or 'application/octet-stream',
                    file_size=file.size,
                    encrypted_path='',  # No longer using filesystem
                    encrypted_data=encrypted_data,  # Store in database
                    salt=salt,
                    iv=iv
                )
                
                # Log access
                FileAccessLog.objects.create(
                    file=encrypted_file,
                    user=request.user,
                    access_type='upload',
                    ip_address=request.META.get('REMOTE_ADDR'),
                    user_agent=request.META.get('HTTP_USER_AGENT')
                )
                
                messages.success(request, 'File uploaded and encrypted successfully.')
                return redirect('file-list')
            
            except Exception as e:
                print(f"Error uploading file: {str(e)}")
                import traceback
                traceback.print_exc()
                messages.error(request, 'Error uploading file. Please try again.')
                return redirect('upload-file')
    else:
        form = FileUploadForm()
    
    return render(request, 'vault/upload.html', {'form': form})

@login_required
def file_list(request):
    try:
        # Ensure encrypted files directory exists
        encrypted_files_path = settings.ENCRYPTED_FILES_ROOT
        if not os.path.exists(encrypted_files_path):
            os.makedirs(encrypted_files_path, exist_ok=True)
            print(f"Created encrypted files directory at {encrypted_files_path}")
        
        # Get user's files
        files = EncryptedFile.objects.filter(user=request.user).order_by('-created_at')
        file_count = files.count()
        print(f"Found {file_count} files for user {request.user.username}")
        
        # Calculate total size
        total_size = files.aggregate(total=Sum('file_size'))['total'] or 0
        
        # Prepare context
        context = {
            'files': files,
            'total_size': total_size,
            'total_files': file_count,
            'user': request.user
        }
        
        return render(request, 'vault/file_list.html', context)
        
    except Exception as e:
        print(f"Error in file_list view: {str(e)}")
        messages.error(request, 'An error occurred while loading your files. Please try again.')
        return redirect('dashboard')

@login_required
def download_file(request, file_id):
    try:
        encrypted_file = get_object_or_404(EncryptedFile, id=file_id, user=request.user)
        action = request.GET.get('action', 'download')  # 'download' or 'view'
        
        print(f"Download request for file_id={file_id}, action={action}, user={request.user.username}")
        
        if request.method == 'POST':
            form = FileDownloadForm(request.POST)
            if form.is_valid():
                try:
                    # Check if encrypted data exists in database
                    if not encrypted_file.encrypted_data:
                        print(f"ERROR: Encrypted data not found for file_id={file_id}")
                        messages.error(request, 'File data not found. It may have been corrupted.')
                        return redirect('file-list')
                    
                    # Convert salt and IV from bytes (already in correct format from DB)
                    # Decrypt file from database
                    from .utils import decrypt_file
                    decrypted_content = decrypt_file(
                        encrypted_file.encrypted_data,
                        form.cleaned_data['password'],
                        bytes(encrypted_file.salt),
                        bytes(encrypted_file.iv)
                    )
                    
                    print(f"File decrypted successfully: {encrypted_file.original_filename}")
                    
                    # Log access
                    FileAccessLog.objects.create(
                        file=encrypted_file,
                        user=request.user,
                        access_type=action,
                        ip_address=request.META.get('REMOTE_ADDR'),
                        user_agent=request.META.get('HTTP_USER_AGENT')
                    )
                    
                    # Prepare response
                    content_type = encrypted_file.file_type
                    response = HttpResponse(decrypted_content, content_type=content_type)
                    
                    if action == 'download':
                        response['Content-Disposition'] = f'attachment; filename="{encrypted_file.original_filename}"'
                    else:
                        # For viewing, use inline disposition
                        response['Content-Disposition'] = f'inline; filename="{encrypted_file.original_filename}"'
                    
                    return response
                
                except ValueError as e:
                    print(f"ERROR: Decryption failed - {str(e)}")
                    messages.error(request, 'Invalid password. Please try again.')
                    return render(request, 'vault/file_access.html', {
                        'form': form,
                        'file': encrypted_file,
                        'action': action
                    })
                except Exception as e:
                    print(f"ERROR accessing file: {str(e)}")
                    import traceback
                    traceback.print_exc()
                    messages.error(request, 'An error occurred. Please try again or contact support.')
                    return redirect('file-list')
        else:
            form = FileDownloadForm()
        
        return render(request, 'vault/file_access.html', {
            'form': form,
            'file': encrypted_file,
            'action': action
        })
    
    except Exception as e:
        print(f"ERROR in download_file view: {str(e)}")
        import traceback
        traceback.print_exc()
        messages.error(request, 'An error occurred loading the file.')
        return redirect('file-list')

@login_required
def delete_file(request, file_id):
    encrypted_file = get_object_or_404(EncryptedFile, id=file_id, user=request.user)
    
    if request.method == 'POST':
        form = FileDownloadForm(request.POST)
        if form.is_valid():
            try:
                # Convert salt and IV from bytes (already in correct format from DB)
                # Verify password by attempting decryption
                from .utils import decrypt_file
                try:
                    decrypt_file(
                        encrypted_file.encrypted_data,
                        form.cleaned_data['password'],
                        bytes(encrypted_file.salt),
                        bytes(encrypted_file.iv)
                    )
                except Exception:
                    messages.error(request, 'Invalid password.')
                    return redirect('file-list')
                
                # Delete database record (encrypted_data is in DB, no filesystem cleanup needed)
                encrypted_file.delete()
                
                # Log deletion
                FileAccessLog.objects.create(
                    file=encrypted_file,
                    user=request.user,
                    access_type='delete',
                    ip_address=request.META.get('REMOTE_ADDR'),
                    user_agent=request.META.get('HTTP_USER_AGENT')
                )
                
                messages.success(request, 'File deleted successfully.')
            except Exception as e:
                print(f"Error deleting file: {str(e)}")
                messages.error(request, 'Error deleting file. Please try again.')
    else:
        form = FileDownloadForm()
        return render(request, 'vault/file_access.html', {
            'form': form,
            'file': encrypted_file,
            'action': 'delete'
        })
    
    return redirect('file-list')

@login_required
def access_logs(request):
    logs = FileAccessLog.objects.filter(
        file__user=request.user
    ).select_related('file', 'user').order_by('-timestamp')
    
    return render(request, 'vault/access_logs.html', {'logs': logs})
