from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import redirect


class AuthorRequiredMixin(UserPassesTestMixin):
    """Ограничивает доступ к объекту только автору."""

    raise_exception = False
    login_url = None

    def test_func(self):
        if not self.request.user.is_authenticated:
            return False
        return self.get_object().author == self.request.user

    def handle_no_permission(self):
        messages.error(
            self.request,
            'У вас нет прав для выполнения этого действия.'
        )
        return redirect(self.get_redirect_url())

    def get_redirect_url(self):
        """Возвращает URL для редиректа (переопределяется в наследниках)."""
        raise NotImplementedError(
            'Метод get_redirect_url должен быть переопределен'
        )
