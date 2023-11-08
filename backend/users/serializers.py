from djoser.serializers import UserSerializer
from rest_framework.serializers import SerializerMethodField
from users.models import Subscriber, User


class CustomUserSerializer(UserSerializer):
    """Сериализатор для работы с информацией о пользователях."""
    is_subscribed = SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name', 'is_subscribed',)

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        return not user.is_anonymous and Subscriber.objects.filter(
            user=user, author=obj).exists()
