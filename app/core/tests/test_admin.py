from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import force_authenticate, APIClient


class TestsAdminSite(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = get_user_model().objects.create_superuser(
            email="admin@londonappdev.com", password="password123"
        )
        self.client.force_login(self.admin_user)
        self.user = get_user_model().objects.create_user(
            email="test@londonappdev.com",
            password="password123",
            name="Test user full name",
        )

    def test_users_listed(self):
        """
        Test that users are listed on user page
        """
        url = reverse("admin:core_user_changelist")
        res = self.client.get(url)

        self.assertContains(res, self.user.name)
        self.assertContains(res, self.user.email)

    def test_user_change_page(self):
        """
        Test that user edit page work
        """
        url = reverse("admin:core_user_change", args=[self.user.id])
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)

    def test_create_user_page(self):
        """
        Test that the create user page works
        """
        url = reverse("admin:core_user_add")
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)

    def test__admin_can_see_users_list(self):
        """
        Test that admin have permission to see users list in UserListViewSet
        """
        url = reverse('user:user-list')
        self.client.force_authenticate(user=self.admin_user)
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)
