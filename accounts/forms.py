from django import forms
from django.contrib.auth import get_user_model
from .models import Profile, StudentProfile

User = get_user_model()


# ------------------
# Base Register Form
# ------------------
class BaseRegisterForm(forms.ModelForm):
    email = forms.EmailField(required=True)
    password = forms.CharField(widget=forms.PasswordInput(attrs={"id": "password"}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={"id": "confirm_password"}))

    class Meta:
        model = Profile
        fields = ["unique_name", "language", "photo"]

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get("password") != cleaned_data.get("confirm_password"):
            raise forms.ValidationError("Passwords do not match!")
        return cleaned_data

    def save_user(self, email, password):
        user, created = User.objects.get_or_create(
            email=email,
            defaults={"username": email}
        )
        if created:
            user.set_password(password)
            user.save()
        return user


# ------------------
# Student Form
# ------------------
class StudentRegisterForm(BaseRegisterForm):
    student_name = forms.CharField(required=True, label="Full Name")
    father_name = forms.CharField(required=False)
    roll_number = forms.CharField(required=False)
    school_name = forms.CharField(required=False)

    board = forms.ChoiceField(
        choices=StudentProfile.BOARD_CHOICES,
        required=True
    )

    student_class = forms.ChoiceField(
        choices=StudentProfile.CLASS_CHOICES,
        required=True
    )

    subject = forms.MultipleChoiceField(
        choices=[
            ('Math', 'Mathematics'),
            ('Science', 'Science'),
            ('Social Science', 'Social Science'),
            ('Geography', 'Geography'),
            ('English', 'English'),
            ('Hindi', 'Hindi'),
        ],
        widget=forms.CheckboxSelectMultiple,
        required=True
    )

    address = forms.CharField(widget=forms.Textarea, required=False)
    pincode = forms.CharField(required=False)
    mobile_number = forms.CharField(required=False)

    def save(self, commit=True):
        user = self.save_user(self.cleaned_data["email"], self.cleaned_data["password"])
        profile = super().save(commit=False)
        profile.user = user
        profile.role = "student"
        if commit:
            profile.save()

        # create student profile
        StudentProfile.objects.create(
            user=user,
            unique_name=self.cleaned_data.get("unique_name"),
            student_name=self.cleaned_data.get("student_name"),
            father_name=self.cleaned_data.get("father_name"),
            roll_number=self.cleaned_data.get("roll_number"),
            school_name=self.cleaned_data.get("school_name"),
            board=self.cleaned_data.get("board"),
            student_class=self.cleaned_data.get("student_class"),
            subject=", ".join(self.cleaned_data.get("subject")),
            address=self.cleaned_data.get("address"),
            pincode=self.cleaned_data.get("pincode"),
            mobile_number=self.cleaned_data.get("mobile_number"),
        )
        return profile


# ------------------
# Teacher Form
# ------------------
class TeacherRegisterForm(BaseRegisterForm):
    subject = forms.CharField(required=True)
    qualification = forms.CharField(required=True)
    experience = forms.CharField(required=False)


# ------------------
# Parent Form
# ------------------
class ParentRegisterForm(BaseRegisterForm):
    father_name = forms.CharField(required=True, label="Parent Name")
    child_name = forms.CharField(required=False)
    relation = forms.CharField(required=False)


# ------------------
# Login Form
# ------------------
class LoginForm(forms.Form):
    email = forms.EmailField()
    role = forms.ChoiceField(choices=Profile.ROLE_CHOICES)
    password = forms.CharField(widget=forms.PasswordInput)
