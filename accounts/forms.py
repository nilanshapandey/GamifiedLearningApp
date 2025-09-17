from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model, password_validation
from .models import StudentProfile

User = get_user_model()


# Small helper to add bootstrap class by default
def input_widget(attrs=None):
    base = {"class": "form-control"}
    if attrs:
        base.update(attrs)
    return forms.TextInput(attrs=base)


# ------------------ STUDENT ------------------
class StudentRegisterForm(forms.ModelForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={"class": "form-control"}))
    username = forms.CharField(max_length=150, widget=input_widget())
    password = forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-control"}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-control"}))

    LANGUAGE_CHOICES = [
        ("english", "English"),
        ("hindi", "Hindi"),
        ("odia", "Odia"),
        ("marathi", "Marathi"),
        ("gujarati", "Gujarati"),
        ("punjabi", "Punjabi"),
        ("telugu", "Telugu"),
        ("bengali", "Bengali"),
        ("kannada", "Kannada"),
        ("urdu", "Urdu"),
        ("other", "Other"),
    ]

    SUBJECT_CHOICES = [
        ("math", "Math"),
        ("hindi", "Hindi"),
        ("english", "English"),
        ("computer science", "Computer Science"),
        ("physics", "Physics"),
        ("chemistry", "Chemistry"),
        ("biology", "Biology"),
        ("geography", "Geography"),
        ("history", "History"),
        ("ethics", "Ethics"),
    ]

    language = forms.ChoiceField(choices=LANGUAGE_CHOICES, widget=forms.Select(attrs={"class": "form-select"}))
    subject = forms.MultipleChoiceField(choices=SUBJECT_CHOICES, widget=forms.CheckboxSelectMultiple(attrs={"class": "form-check-input"}))

    class Meta:
        model = StudentProfile
        fields = [
            "student_name", "father_name", "address", "pincode", "student_class", "subject",
            "board", "language", "roll_number", "mobile_number", "school_name"
        ]
        widgets = {
            "student_name": input_widget(),
            "father_name": input_widget(),
            "address": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
            "pincode": input_widget(),
            "student_class": forms.Select(attrs={"class": "form-select"}),
            "board": forms.Select(attrs={"class": "form-select"}),
            "roll_number": input_widget(),
            "mobile_number": input_widget(),
            "school_name": input_widget(),
        }

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError("A user with this email already exists.")
        return email

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if User.objects.filter(username__iexact=username).exists():
            raise ValidationError("This username is already taken.")
        return username

    def clean(self):
        cleaned = super().clean()
        pwd, pwd2 = cleaned.get("password"), cleaned.get("confirm_password")
        if pwd and pwd2 and pwd != pwd2:
            self.add_error("confirm_password", "Passwords do not match.")
        if pwd:
            try:
                password_validation.validate_password(pwd, user=None)
            except ValidationError as e:
                self.add_error("password", e.messages)
        return cleaned

    def save(self, commit=True):
        data = self.cleaned_data
        # Create user if not editing
        if not self.instance.pk:
            user = User.objects.create_user(username=data["username"], email=data["email"], password=data["password"])
            self.instance.user = user
        # Save StudentProfile
        self.instance.subject = ", ".join(data.get("subject") or [])
        self.instance.language = data.get("language")
        profile = super().save(commit=commit)

        # Auto-create backend Subject, Lesson, Topic, Quiz for selected subjects
        from content.models import Subject, Lesson, Quiz, Question, Choice
        board = data.get("board") or "CBSE"
        class_level = data.get("student_class") or "6"
        for subj_key in data.get("subject") or []:
            subj_name = dict(self.SUBJECT_CHOICES).get(subj_key, subj_key.title())
            subject_obj, _ = Subject.objects.get_or_create(name=subj_name, board=board, class_level=class_level)
            # Create a default lesson
            lesson_obj, _ = Lesson.objects.get_or_create(subject=subject_obj, title=f"Introduction to {subj_name}")
            # Create a default topic (if your model has Topic)
            # If Topic model exists, add here
            # Create a default quiz
            quiz_obj, _ = Quiz.objects.get_or_create(lesson=lesson_obj, title=f"Quiz for {subj_name}")
            # Create a default question
            q_obj, _ = Question.objects.get_or_create(quiz=quiz_obj, text=f"Sample MCQ for {subj_name}", qtype="mcq", marks=1)
            # Create choices
            Choice.objects.get_or_create(question=q_obj, text="Option 1", is_correct=True)
            Choice.objects.get_or_create(question=q_obj, text="Option 2", is_correct=False)
        return profile


# ------------------ LOGIN ------------------
class LoginForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={"class": "form-control"}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-control"}))


# ------------------ FORGOT ------------------
class ForgotPasswordForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={"class": "form-control"}))
