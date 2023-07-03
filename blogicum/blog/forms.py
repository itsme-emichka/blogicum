from django import forms

from blog.models import Post, User, Comment


class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        exclude = ('author', )
        widgets = {
            'pub_date': forms.DateTimeInput(attrs={'type': 'datetime'})
        }


class UserForm(forms.ModelForm):

    class Meta:
        model = User
        fields = (
            'username',
            'first_name',
            'last_name',
            'email',
        )


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = (
            'text',
        )
        widgets = {
            'text': forms.Textarea(attrs={'rows': 5, 'cols': 10})
        }
