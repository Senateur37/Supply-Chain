from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.test import TestCase
from django.urls import reverse


User = get_user_model()


class GestionUtilisateursTests(TestCase):
	def setUp(self):
		self.admin = User.objects.create_user('admin', password='mot-de-passe', is_staff=True)
		self.client.force_login(self.admin)

	def test_admin_can_create_and_edit_user(self):
		response = self.client.post(reverse('utilisateurs'), {
			'username': 'employe',
			'first_name': 'Awa',
			'last_name': 'Kone',
			'email': 'awa@example.com',
			'role': 'commercial',
			'password1': 'MotDePasseSolide123!',
			'password2': 'MotDePasseSolide123!',
		})
		self.assertRedirects(response, reverse('utilisateurs'))
		utilisateur = User.objects.get(username='employe')

		response = self.client.post(reverse('utilisateur_edit', args=[utilisateur.pk]), {
			'username': 'employe',
			'first_name': 'Awa',
			'last_name': 'Traore',
			'email': 'awa@example.com',
			'role': 'admin',
			'is_staff': 'on',
		})
		self.assertRedirects(response, reverse('utilisateurs'))
		utilisateur.refresh_from_db()
		self.assertEqual(utilisateur.last_name, 'Traore')
		self.assertTrue(utilisateur.is_staff)
		self.assertEqual(utilisateur.groups.get().name, 'admin')

	def test_role_is_saved_and_restricts_modules(self):
		utilisateur = User.objects.create_user('commercial', password='mot-de-passe')
		utilisateur.groups.create(name='commercial')
		self.client.force_login(utilisateur)
		self.assertEqual(self.client.get(reverse('ventes')).status_code, 200)
		with self.assertRaises(PermissionDenied):
			self.client.get(reverse('comptable'))

	def test_admin_cannot_delete_self_or_superuser(self):
		response = self.client.post(reverse('utilisateur_delete', args=[self.admin.pk]))
		self.assertRedirects(response, reverse('utilisateurs'))
		self.assertTrue(User.objects.filter(pk=self.admin.pk).exists())

		superuser = User.objects.create_superuser('root', password='mot-de-passe')
		response = self.client.post(reverse('utilisateur_delete', args=[superuser.pk]))
		self.assertRedirects(response, reverse('utilisateurs'))
		self.assertTrue(User.objects.filter(pk=superuser.pk).exists())

	def test_admin_can_delete_regular_user(self):
		utilisateur = User.objects.create_user('a-supprimer', password='mot-de-passe')
		response = self.client.post(reverse('utilisateur_delete', args=[utilisateur.pk]))
		self.assertRedirects(response, reverse('utilisateurs'))
		self.assertFalse(User.objects.filter(pk=utilisateur.pk).exists())

	def test_non_staff_cannot_access_user_management(self):
		utilisateur = User.objects.create_user('employe', password='mot-de-passe')
		self.client.force_login(utilisateur)
		response = self.client.get(reverse('utilisateurs'))
		self.assertNotEqual(response.status_code, 200)
