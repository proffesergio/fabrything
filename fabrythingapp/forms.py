from django import forms
from fabrythingapp.models import ProductReview

class ProductReviewForm(forms.ModelForm):
    review_heading = forms.CharField(widget=forms.Textarea(attrs={'placeholder':'Thanks to Fabrything for this amazing item!', 'class':'form-control'}))
    review = forms.CharField(widget=forms.Textarea(attrs={'placeholder':'Write Review', 'class':'form-control'}))
    # rating = forms.IntegerField(widget=forms.IntegerField(attrs={'placeholder':'Rate Your Review', 'class':'form-control'}))
    # rating = forms.ChoiceField(widget=forms.ChoiceField)

    class Meta:
        model = ProductReview
        fields = ['review_heading', 'review', 'rating']