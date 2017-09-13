from django import forms
from django.core.exceptions import ValidationError


class RegisterForm(forms.Form):

    email = forms.EmailField(widget=forms.EmailInput(  # 记住，这里是EmailInput
        attrs={"class": "form-control"}))

    username = forms.CharField(min_length=4, max_length=12, widget=forms.TextInput(
        attrs={"class": "form-control"}))

    password = forms.CharField(min_length=6, widget=forms.PasswordInput(
        attrs={"class": "form-control"}))

    password2 = forms.CharField(min_length=6, widget=forms.PasswordInput(
        attrs={"class": "form-control"}))

    valid_code = forms.CharField(widget=forms.TextInput(
        attrs={"class": "form-control"}))

    def __init__(self, request, *args, **kwargs):
        # 重写构造器，使其可以额外接收一个参数，用于自定义验证函数时验证验证码
        super(RegisterForm,self).__init__(*args, **kwargs)  #
        self.request = request

    # 自定义方法（局部钩子），密码必须包含字母和数字
    def clean_password(self):
        if self.cleaned_data.get('password').isdigit() or self.cleaned_data.get('password').isalpha():
            raise ValidationError('密码必须包含数字和字母')
        else:
            return self.cleaned_data['password']

    def clean_valid_code(self):  # 检验验证码正确
        if self.cleaned_data.get('valid_code').upper() == self.request.session.get('valid_code'):
            return self.cleaned_data['valid_code']
        else:
            raise ValidationError('验证码不正确')

    # 自定义方法（全局钩子, 检验两个字段），检验两次密码一致;
    def clean(self):
        if self.cleaned_data.get('password') != self.cleaned_data.get('password2'):
            raise ValidationError('密码不一致')
        else:
            return self.cleaned_data


    # 注意，上面的字典取值用get, 因为假如在claen_password中判断失败，那么没有返回值，最下面的clean方法直接取值就会失败


class CommentForm(forms.Form):
    comment_body = forms.CharField(min_length=1,
                                   error_messages={"required":["请输入有效的评论！"]},   # 自定义输入为空时的错误信息
                                   widget=forms.Textarea(attrs={"class": "form-control",
                                                                         "rows": "3",
                                                                         "placeholder": "留下你的评论吧...提示，请勿输入空评论，或非法词汇，比如【垃圾,菜鸟,和谐】"}))

    def clean_comment_body(self):  # 验证用户输入
        forbidden = ["垃圾","菜鸟","和谐"]
        for word in forbidden:
            if word in self.cleaned_data.get("comment_body"):
                raise ValidationError('您的评论中包含非法词汇，请修改! ')
        return self.cleaned_data["comment_body"]



