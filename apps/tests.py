from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.test import TestCase
from django.urls import reverse
from Produits.models import Produit


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
		response_restreint = self.client.get(reverse('comptable'))
		self.assertEqual(response_restreint.status_code, 403)

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

	def test_product_search_filters_results(self):
		Produit.objects.create(reference='REF-001', designation='Sac de riz', prix_unitaire=1000)
		Produit.objects.create(reference='REF-002', designation='Huile alimentaire', prix_unitaire=2000)
		response = self.client.get(reverse('produits'), {'q': 'riz'})
		self.assertContains(response, 'Sac de riz')
		self.assertNotContains(response, 'Huile alimentaire')


class SuiviExpeditionTests(TestCase):
	def setUp(self):
		self.admin = User.objects.create_user('admin_suivi', password='mot-de-passe', is_staff=True)
		self.client.force_login(self.admin)
		self.produit = Produit.objects.create(reference='PROD-GPS-01', designation='Televiseur 4K', prix_unitaire=250000)

	def test_creer_suivi_expedition(self):
		response = self.client.post(reverse('suivi_create'), {
			'numero_suivi': 'TRK-2026-TEST',
			'produit': self.produit.pk,
			'quantite': 5,
			'statut': '1_FOURNISSEUR',
			'transporteur': 'Sahel Express',
			'immatriculation_vehicule': 'M-9999-BK',
			'nom_chauffeur': 'Amadou Diallo',
			'telephone_chauffeur': '+223 76 00 00 00',
			'lat_fournisseur': 12.6392,
			'lng_fournisseur': -8.0029,
			'lat_entrepot': 12.6500,
			'lng_entrepot': -7.9800,
			'lat_client': 12.6100,
			'lng_client': -7.9500,
		})
		self.assertEqual(response.status_code, 302)
		from apps.models import SuiviExpedition
		suivi = SuiviExpedition.objects.get(numero_suivi='TRK-2026-TEST')
		self.assertEqual(suivi.produit, self.produit)
		self.assertEqual(suivi.quantite, 5)

	def test_api_update_gps(self):
		from apps.models import SuiviExpedition
		suivi = SuiviExpedition.objects.create(
			numero_suivi='TRK-GPS-API',
			produit=self.produit,
			quantite=1,
			statut='1_FOURNISSEUR',
			lat_actuelle=12.6392,
			lng_actuelle=-8.0029
		)
		import json
		response = self.client.post(
			reverse('suivi_update_gps_api', args=[suivi.pk]),
			data=json.dumps({
				'lat': 12.6450,
				'lng': -7.9900,
				'vitesse': 60.5,
				'progression': 45,
				'statut': '2_TRANSIT_ENTREPOT'
			}),
			content_type='application/json'
		)
		self.assertEqual(response.status_code, 200)
		suivi.refresh_from_db()
		self.assertEqual(suivi.lat_actuelle, 12.6450)
		self.assertEqual(suivi.lng_actuelle, -7.9900)
		self.assertEqual(suivi.vitesse_kmh, 60.5)
		self.assertEqual(suivi.progression_pct, 45)
		self.assertEqual(suivi.statut, '2_TRANSIT_ENTREPOT')
		self.assertTrue(suivi.historique_positions.exists())

