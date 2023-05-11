from django.conf import settings
from django.contrib.auth import SESSION_KEY
from django.test import TestCase
from django.urls import reverse

from tweets.models import Tweet

from .models import FollowUser, User


class TestSignupView(TestCase):
    def setUp(self):
        self.url = reverse("accounts:signup")

    def test_success_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/signup.html")

    def test_success_post(self):
        valid_data = {
            "username": "testuser",
            "email": "test@test.com",
            "password1": "testpassword",
            "password2": "testpassword",
        }
        response = self.client.post(self.url, valid_data)

        self.assertRedirects(
            response,
            reverse("tweets:home"),
            status_code=302,
            target_status_code=200,
        )
        self.assertTrue(User.objects.filter(username=valid_data["username"]).exists())
        self.assertIn(SESSION_KEY, self.client.session)

    def test_failure_post_with_empty_form(self):
        invalid_data = {
            "username": "",
            "email": "",
            "password1": "",
            "password2": "",
        }
        response = self.client.post(self.url, invalid_data)
        self.assertEqual(response.status_code, 200)
        form = response.context["form"]
        self.assertEqual(User.objects.all().count(), 0)
        self.assertFalse(form.is_valid())
        self.assertIn("このフィールドは必須です。", form.errors["username"])
        self.assertIn("このフィールドは必須です。", form.errors["email"])
        self.assertIn("このフィールドは必須です。", form.errors["password1"])
        self.assertIn("このフィールドは必須です。", form.errors["password2"])

    def test_failure_post_with_empty_username(self):
        empty_user_data = {
            "username": "",
            "email": "test@test.com",
            "password1": "testpassword",
            "password2": "testpassword",
        }
        response = self.client.post(self.url, empty_user_data)
        form = response.context["form"]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.all().count(), 0)
        self.assertFalse(form.is_valid())
        self.assertIn("このフィールドは必須です。", form.errors["username"])

    def test_failure_post_with_empty_email(self):
        empty_email_data = {
            "username": "testuser",
            "email": "",
            "password1": "testpassword",
            "password2": "testpassword",
        }
        response = self.client.post(self.url, empty_email_data)
        form = response.context["form"]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.all().count(), 0)
        self.assertFalse(form.is_valid())
        self.assertIn("このフィールドは必須です。", form.errors["email"])

    def test_failure_post_with_empty_password(self):
        empty_password_data = {
            "username": "testuser",
            "email": "test@test.com",
            "password1": "",
            "password2": "",
        }
        response = self.client.post(self.url, empty_password_data)
        form = response.context["form"]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.all().count(), 0)
        self.assertFalse(form.is_valid())
        self.assertIn("このフィールドは必須です。", form.errors["password1"])
        self.assertIn("このフィールドは必須です。", form.errors["password2"])

    def test_failure_post_with_duplicated_user(self):
        duplicated_user_data = {
            "username": "testuser",
            "email": "test@test.com",
            "password1": "testpassword",
            "password2": "testpassword",
        }
        response = self.client.post(self.url, duplicated_user_data)
        response = self.client.post(self.url, duplicated_user_data)

        self.assertEqual(User.objects.all().count(), 1)
        form = response.context["form"]
        self.assertEqual(response.status_code, 200)
        self.assertFalse(form.is_valid())
        self.assertIn("同じユーザー名が既に登録済みです。", form.errors["username"])

    def test_failure_post_with_invalid_email(self):
        invalid_email_data = {
            "username": "testuser",
            "email": "invalid_email",
            "password1": "testpassword",
            "password2": "testpassword",
        }
        response = self.client.post(self.url, invalid_email_data)
        form = response.context["form"]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.all().count(), 0)
        self.assertFalse(form.is_valid())
        self.assertIn("有効なメールアドレスを入力してください。", form.errors["email"])

    def test_failure_post_with_too_short_password(self):
        too_short_password_data = {
            "username": "testuser",
            "email": "test@test.com",
            "password1": "short",
            "password2": "short",
        }
        response = self.client.post(self.url, too_short_password_data)
        form = response.context["form"]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.all().count(), 0)
        self.assertFalse(form.is_valid())
        self.assertIn("このパスワードは短すぎます。最低 8 文字以上必要です。", form.errors["password2"])

    def test_failure_post_with_password_similar_to_username(self):
        password_similar_to_username_data = {
            "username": "testuser",
            "email": "test@test.com",
            "password1": "testuser1",
            "password2": "testuser1",
        }
        response = self.client.post(self.url, password_similar_to_username_data)
        form = response.context["form"]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.all().count(), 0)
        self.assertFalse(form.is_valid())
        self.assertIn("このパスワードは ユーザー名 と似すぎています。", form.errors["password2"])

    def test_failure_post_with_only_numbers_password(self):
        only_numbers_password_data = {
            "username": "testuser",
            "email": "test@test.com",
            "password1": "123456789",
            "password2": "123456789",
        }
        response = self.client.post(self.url, only_numbers_password_data)
        form = response.context["form"]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.all().count(), 0)
        self.assertFalse(form.is_valid())
        self.assertIn("このパスワードは数字しか使われていません。", form.errors["password2"])

    def test_failure_post_with_mismatch_password(self):
        with_mismatch_password_data = {
            "username": "testuser",
            "email": "test@test.com",
            "password1": "hitotsume1",
            "password2": "futatsume2",
        }
        response = self.client.post(self.url, with_mismatch_password_data)
        form = response.context["form"]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.all().count(), 0)
        self.assertFalse(form.is_valid())
        self.assertIn("確認用パスワードが一致しません。", form.errors["password2"])


class TestLoginView(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpassword",
        )
        self.url = reverse("accounts:login")

    def test_success_get(self):
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/login.html")

    def test_success_post(self):
        data = {"username": "testuser", "password": "testpassword"}
        response = self.client.post(self.url, data)
        self.assertRedirects(
            response,
            reverse(settings.LOGIN_REDIRECT_URL),
            status_code=302,
            target_status_code=200,
        )
        self.assertIn(SESSION_KEY, self.client.session)

    def test_failure_post_with_not_exists_user(self):
        data = {
            "username": "test2",
            "password": "testpassword",
        }
        response = self.client.post(self.url, data)
        self.assertEquals(response.status_code, 200)
        form = response.context["form"]
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["__all__"],
            ["正しいユーザー名とパスワードを入力してください。どちらのフィールドも大文字と小文字は区別されます。"],
        )
        self.assertNotIn(SESSION_KEY, self.client.session)

    def test_failure_post_with_empty_password(self):
        empty_data = {
            "username": "test2",
            "password": "",
        }
        response = self.client.post(self.url, empty_data)
        self.assertEquals(response.status_code, 200)
        form = response.context["form"]
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["password"],
            ["このフィールドは必須です。"],
        )
        self.assertNotIn(SESSION_KEY, self.client.session)


class TestLogoutView(TestCase):
    def setUp(self):
        self.url = User.objects.create_user(
            username="testuser",
            password="testpassword",
        )
        self.client.login(username="testuser", password="testpassword")

    def test_success_post(self):
        response = self.client.post(reverse("accounts:logout"))
        self.assertRedirects(
            response,
            reverse(settings.LOGOUT_REDIRECT_URL),
            status_code=302,
            target_status_code=200,
        )
        self.assertNotIn(SESSION_KEY, self.client.session)


class TestUserProfileView(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username="testuser1", email="test1@example.com", password="testpassword")
        self.user2 = User.objects.create_user(username="testuser2", email="test2@example.com", password="testpassword")
        self.url = reverse("accounts:user_profile", args=[self.user1.username])
        self.client.force_login(self.user1)
        FollowUser.objects.create(following=self.user2, follower=self.user1)

    def test_success_get(self):
        Tweet.objects.create(user=self.user1, content="testcontent")
        Tweet.objects.create(user=self.user2, content="testcontent")
        response = self.client.get(self.url)

        self.assertQuerysetEqual(response.context["object_list"], Tweet.objects.filter(user=self.user1))

        self.assertEqual(response.context["following_count"], FollowUser.objects.filter(follower=self.user1).count())
        self.assertEqual(response.context["follower_count"], FollowUser.objects.filter(following=self.user1).count())


class TestUserProfileEditView(TestCase):
    def test_success_get(self):
        pass

    def test_success_post(self):
        pass

    def test_failure_post_with_not_exists_user(self):
        pass

    def test_failure_post_with_incorrect_user(self):
        pass


class TestFollowView(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username="testuser1", email="test1@example.com", password="testpassword")
        self.user2 = User.objects.create_user(username="testuser2", email="test2@example.com", password="testpassword")
        self.url = reverse("accounts:follow", kwargs={"username": self.user2.username})
        self.client.login(username="testuser1", password="testpassword")

    def test_success_post(self):
        response = self.client.post(reverse("accounts:follow", kwargs={"username": "testuser2"}))
        self.assertRedirects(
            response,
            reverse("tweets:home"),
            status_code=302,
            target_status_code=200,
        )
        self.assertEqual(FollowUser.objects.filter(follower=self.user1).count(), 1)

    def test_failure_post_with_not_exist_user(self):
        response = self.client.post(reverse("accounts:follow", kwargs={"username": "user3"}))
        self.assertEqual(response.status_code, 404)
        self.assertEqual(FollowUser.objects.filter(follower=self.user1).count(), 0)

    def test_failure_post_with_self(self):
        response = self.client.post(reverse("accounts:follow", kwargs={"username": "testuser1"}))
        self.assertEqual(response.status_code, 400)
        self.assertEqual(FollowUser.objects.filter(follower=self.user1).count(), 0)


class TestUnfollowView(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username="testuser1", email="test1@example.com", password="testpassword")
        self.user2 = User.objects.create_user(username="testuser2", email="test2@example.com", password="testpassword")
        self.client.login(username="testuser1", password="testpassword")
        FollowUser.objects.create(following=self.user2, follower=self.user1)

    def test_success_post(self):
        response = self.client.post(reverse("accounts:unfollow", kwargs={"username": "testuser2"}))
        self.assertRedirects(
            response,
            reverse("tweets:home"),
            status_code=302,
            target_status_code=200,
        )
        self.assertEqual(FollowUser.objects.filter(follower=self.user1).count(), 0)

    def test_failure_post_with_not_exist_tweet(self):
        response = self.client.post(reverse("accounts:unfollow", kwargs={"username": "user3"}))
        self.assertEqual(response.status_code, 404)
        self.assertEqual(FollowUser.objects.filter(follower=self.user1).count(), 1)

    def test_failure_post_with_incorrect_user(self):
        response = self.client.post(reverse("accounts:unfollow", kwargs={"username": "testuser1"}))
        self.assertEqual(response.status_code, 400)
        self.assertEqual(FollowUser.objects.filter(follower=self.user1).count(), 1)


class TestFollowingListView(TestCase):
    def test_success_get(self):
        self.user1 = User.objects.create_user(username="testuser1", password="testpassword")
        self.user2 = User.objects.create_user(username="testuser2", password="testpassword")
        self.FollowUser1 = FollowUser.objects.create(following=self.user2, follower=self.user1)
        self.FollowUser2 = FollowUser.objects.create(following=self.user1, follower=self.user2)
        self.client.login(username="testuser1", password="testpassword")
        response = self.client.get(reverse("accounts:following_list", kwargs={"username": "testuser1"}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["following_list"]), 1)
        self.assertEqual(response.context["following_list"][0], self.FollowUser1)


class TestFollowerListView(TestCase):
    def test_success_get(self):
        self.user1 = User.objects.create_user(username="testuser1", password="testpassword")
        self.user2 = User.objects.create_user(username="testuser2", password="testpassword")
        self.FollowUser1 = FollowUser.objects.create(following=self.user2, follower=self.user1)
        self.FollowUser2 = FollowUser.objects.create(following=self.user1, follower=self.user2)
        self.client.login(username="testuser1", password="testpassword")
        response = self.client.get(reverse("accounts:follower_list", kwargs={"username": "testuser1"}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["follower_list"]), 1)
        self.assertEqual(response.context["follower_list"][0], self.FollowUser2)
