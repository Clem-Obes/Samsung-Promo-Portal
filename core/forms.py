from django import forms
from .models import TestimonyComment


class TestimonyCommentForm(forms.ModelForm):
    class Meta:
        model = TestimonyComment
        fields = ['text', 'photo', 'video', 'rating', 'device_received']
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Share your experience with Samsung Promo Portal... What did you achieve? How was the process?',
            }),
            'rating': forms.RadioSelect(choices=[(i, f'{i} Star{"s" if i > 1 else ""}') for i in range(1, 6)]),
            'device_received': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Galaxy S24 Ultra, Galaxy Buds Pro',
            }),
            'photo': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
            }),
            'video': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'accept': 'video/*',
            }),
        }
        labels = {
            'text': 'Your Testimony',
            'photo': 'Upload Photo (optional)',
            'video': 'Upload Video (optional)',
            'rating': 'Your Rating',
            'device_received': 'Device Received (optional)',
        }

    def clean_photo(self):
        photo = self.cleaned_data.get('photo')
        if photo:
            if photo.size > 5 * 1024 * 1024:  # 5MB limit
                raise forms.ValidationError('Photo file size must be under 5MB.')
            if not photo.content_type.startswith('image/'):
                raise forms.ValidationError('Please upload a valid image file.')
        return photo

    def clean_video(self):
        video = self.cleaned_data.get('video')
        if video:
            if video.size > 50 * 1024 * 1024:  # 50MB limit
                raise forms.ValidationError('Video file size must be under 50MB.')
            allowed_types = ['video/mp4', 'video/webm', 'video/ogg', 'video/quicktime']
            if video.content_type not in allowed_types:
                raise forms.ValidationError('Please upload a valid video file (MP4, WebM, OGG, or MOV).')
        return video
