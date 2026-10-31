from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from django.conf import settings
from django.db.models import Q
from django.utils import timezone as django_timezone
from user.models import User
from utils.exceptions import ConflictException, NotFoundException, UnauthorizedException
from utils.pagination import paginate

PUBLIC_FIELDS = ('id', 'email', 'name', 'role', 'created_at', 'updated_at')


class UserService:
  def create_user(self, dto):
    if User.objects.filter(email=dto['email'], deleted_at=None).exists():
      raise ConflictException('User with this email already exists')
    dto['password'] = self.hash_password(dto['password'])
    user = User.objects.create(**dto)
    return {'token': self.generate_token(user), 'user': self.public_user(user.id)}

  def login(self, dto):
    user = User.objects.filter(email=dto['email'], deleted_at=None).first()
    if not user or not self.verify_password(dto['password'], user.password):
      raise UnauthorizedException('Invalid email or password')
    return {'token': self.generate_token(user), 'user': self.public_user(user.id)}

  def get_users(self, dto):
    users = User.objects.filter(deleted_at=None).order_by('-created_at')
    if dto.get('search'):
      users = users.filter(Q(name__icontains=dto['search']) | Q(email__icontains=dto['search']))
    return paginate(users.values(*PUBLIC_FIELDS), dto['page'], dto['limit'])

  def get_user(self, id):
    user = User.objects.filter(id=id, deleted_at=None).values(*PUBLIC_FIELDS).first()
    if not user:
      raise NotFoundException('User not found')
    return user

  def update_user(self, id, dto):
    if 'password' in dto:
      dto['password'] = self.hash_password(dto['password'])
    updated = User.objects.filter(id=id, deleted_at=None).update(**dto, updated_at=django_timezone.now())
    if updated == 0:
      raise NotFoundException('User not found')
    return self.get_user(id)

  def delete_user(self, id) -> None:
    updated = User.objects.filter(id=id, deleted_at=None).update(deleted_at=django_timezone.now())
    if updated == 0:
      raise NotFoundException('User not found or already deleted')

  def public_user(self, id):
    return User.objects.filter(id=id).values(*PUBLIC_FIELDS).first()

  def generate_token(self, user) -> str:
    now = datetime.now(timezone.utc)
    payload = {
      'user_id': str(user.id),
      'email': user.email,
      'role': user.role,
      'iat': now,
      'exp': now + timedelta(days=settings.JWT_EXPIRY_DAYS),
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm='HS256')

  def hash_password(self, password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

  def verify_password(self, password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
