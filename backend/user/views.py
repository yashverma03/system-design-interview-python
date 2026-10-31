from decorators.is_public import is_public
from decorators.roles import roles
from dto.email_password_dto import EmailPasswordDto
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from user.dto.create_user_dto import CreateUserDto
from user.dto.get_users_dto import GetUsersDto
from user.dto.update_user_dto import UpdateUserDto
from user.models import UserRole
from user.services import UserService
from utils.dto_validator import DTOValidator

user_service = UserService()


@is_public
@api_view(['POST'])
def register(request):
  dto = DTOValidator.validate(CreateUserDto, request.data)
  return Response(user_service.create_user(dict(dto)), status=status.HTTP_201_CREATED)


@is_public
@api_view(['POST'])
def login(request):
  dto = DTOValidator.validate(EmailPasswordDto, request.data)
  return Response(user_service.login(dto), status=status.HTTP_200_OK)


@api_view(['GET'])
@roles([UserRole.ADMIN])
def list_users(request):
  dto = DTOValidator.validate(GetUsersDto, request.query_params)
  return Response(user_service.get_users(dto))


@roles([UserRole.ADMIN])
def delete_user(request, id):
  user_service.delete_user(id)
  return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'PUT', 'DELETE'])
def user_detail(request, id):
  if request.method == 'GET':
    return Response(user_service.get_user(id))
  if request.method == 'PUT':
    dto = DTOValidator.validate(UpdateUserDto, request.data)
    return Response(user_service.update_user(id, dict(dto)))
  return delete_user(request, id)
