from datetime import datetime, timezone
from unittest.mock import MagicMock

import bcrypt
import jwt
import pytest
from django.conf import settings
from user.services import UserService
from utils.exceptions import ConflictException, NotFoundException, UnauthorizedException


@pytest.fixture
def service():
  return UserService()


@pytest.fixture
def user_model(mocker):
  return mocker.patch('user.services.User')


class TestPasswords:
  def test_hash_is_not_plaintext_and_verifies(self, service):
    hashed = service.hash_password('password123')
    assert hashed != 'password123'
    assert service.verify_password('password123', hashed) is True

  def test_verify_rejects_wrong_password(self, service):
    hashed = service.hash_password('password123')
    assert service.verify_password('wrong-password', hashed) is False

  def test_hash_is_salted(self, service):
    assert service.hash_password('password123') != service.hash_password('password123')


class TestGenerateToken:
  def test_payload_and_expiry(self, service, sample_user):
    token = service.generate_token(sample_user)
    payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=['HS256'])

    assert payload['user_id'] == str(sample_user.id)
    assert payload['email'] == sample_user.email
    assert payload['role'] == sample_user.role
    expires_in = datetime.fromtimestamp(payload['exp'], timezone.utc) - datetime.fromtimestamp(payload['iat'], timezone.utc)
    assert expires_in.days == settings.JWT_EXPIRY_DAYS

  def test_signed_with_secret(self, service, sample_user):
    token = service.generate_token(sample_user)
    with pytest.raises(jwt.InvalidSignatureError):
      jwt.decode(token, 'another-secret-with-at-least-32-bytes', algorithms=['HS256'])


class TestCreateUser:
  def test_raises_conflict_when_email_exists(self, service, user_model):
    user_model.objects.filter.return_value.exists.return_value = True

    with pytest.raises(ConflictException):
      service.create_user({'email': 'jane@example.com', 'name': 'Jane', 'password': 'password123'})
    user_model.objects.create.assert_not_called()

  def test_hashes_password_and_returns_token(self, service, user_model, sample_user):
    user_model.objects.filter.return_value.exists.return_value = False
    user_model.objects.create.return_value = sample_user
    public = {'id': sample_user.id, 'email': sample_user.email}
    user_model.objects.filter.return_value.values.return_value.first.return_value = public

    result = service.create_user({'email': sample_user.email, 'name': 'Jane', 'password': 'password123'})

    created = user_model.objects.create.call_args.kwargs
    assert created['password'] != 'password123'
    assert bcrypt.checkpw(b'password123', created['password'].encode())
    assert result['user'] == public
    assert jwt.decode(result['token'], settings.JWT_SECRET_KEY, algorithms=['HS256'])['user_id'] == str(sample_user.id)


class TestLogin:
  def test_unknown_email(self, service, user_model):
    user_model.objects.filter.return_value.first.return_value = None

    with pytest.raises(UnauthorizedException):
      service.login({'email': 'nobody@example.com', 'password': 'password123'})

  def test_wrong_password(self, service, user_model, sample_user):
    sample_user.password = service.hash_password('password123')
    user_model.objects.filter.return_value.first.return_value = sample_user

    with pytest.raises(UnauthorizedException):
      service.login({'email': sample_user.email, 'password': 'wrong-password'})

  def test_success_returns_token_and_user(self, service, user_model, sample_user):
    sample_user.password = service.hash_password('password123')
    public = {'id': sample_user.id, 'email': sample_user.email}
    filtered = MagicMock()
    filtered.first.return_value = sample_user
    filtered.values.return_value.first.return_value = public
    user_model.objects.filter.return_value = filtered

    result = service.login({'email': sample_user.email, 'password': 'password123'})

    assert result['user'] == public
    assert 'token' in result


class TestGetUser:
  def test_not_found(self, service, user_model):
    user_model.objects.filter.return_value.values.return_value.first.return_value = None

    with pytest.raises(NotFoundException):
      service.get_user('missing-id')

  def test_returns_user(self, service, user_model):
    public = {'id': 'abc', 'email': 'jane@example.com'}
    user_model.objects.filter.return_value.values.return_value.first.return_value = public

    assert service.get_user('abc') == public


class TestGetUsers:
  def test_paginates_without_search(self, service, user_model):
    queryset = user_model.objects.filter.return_value.order_by.return_value
    values = queryset.values.return_value
    values.count.return_value = 25
    values.__getitem__.return_value = [{'id': 1}, {'id': 2}]

    result = service.get_users({'page': 2, 'limit': 10})

    values.__getitem__.assert_called_once_with(slice(10, 20))
    queryset.filter.assert_not_called()
    assert result == {'items': [{'id': 1}, {'id': 2}], 'page': 2, 'limit': 10, 'total': 25, 'total_pages': 3}

  def test_applies_search_filter(self, service, user_model):
    queryset = user_model.objects.filter.return_value.order_by.return_value
    searched = queryset.filter.return_value
    searched.values.return_value.count.return_value = 0
    searched.values.return_value.__getitem__.return_value = []

    service.get_users({'page': 1, 'limit': 10, 'search': 'jane'})

    queryset.filter.assert_called_once()


class TestUpdateUser:
  def test_not_found(self, service, user_model):
    user_model.objects.filter.return_value.update.return_value = 0

    with pytest.raises(NotFoundException):
      service.update_user('missing-id', {'name': 'New'})

  def test_hashes_new_password(self, service, user_model, mocker):
    update = user_model.objects.filter.return_value.update
    update.return_value = 1
    mocker.patch.object(service, 'get_user', return_value={'id': 'abc'})

    service.update_user('abc', {'password': 'new-password-1'})

    assert update.call_args.kwargs['password'] != 'new-password-1'
    assert bcrypt.checkpw(b'new-password-1', update.call_args.kwargs['password'].encode())


class TestDeleteUser:
  def test_not_found(self, service, user_model):
    user_model.objects.filter.return_value.update.return_value = 0

    with pytest.raises(NotFoundException):
      service.delete_user('missing-id')

  def test_soft_deletes(self, service, user_model):
    update = user_model.objects.filter.return_value.update
    update.return_value = 1

    service.delete_user('abc')

    assert 'deleted_at' in update.call_args.kwargs
    assert update.call_args.kwargs['deleted_at'] is not None
