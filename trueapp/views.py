# Django Imports
from django.http import HttpResponse
from django.contrib.auth import authenticate
# RestFrameWork Imports
from rest_framework.authentication import get_authorization_header, BaseAuthentication
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, exceptions
# Third Party Imports
import jwt
import json
# Local Imports
from .models import Contact, UserContactMapping, User
from .serializers import ContactSerializer, UserSerializer


def index(request):
    """Normal View"""
    return HttpResponse('Hello world')


class ContactsList(APIView):
    """Contact Details View for adding or fetching"""

    def get(self, request):
        """Fetching the contact details"""
        contacts = Contact.objects.all()
        serializer = ContactSerializer(contacts, many=True)
        return Response(serializer.data)

    def post(self, request):
        """Adding the contact Details"""
        auth = TokenAuthentication()
        user, error = auth.authenticate(request)
        if (error):
            return Response(
                error,
                status=400,
                content_type="application/json"
            )
        else:
            name = request.data.get('name', None)
            email = request.data.get('email', None)
            phone = request.data.get('phone', None)
            contact = Contact(
                name=name,
                phone=phone,
                email=email
            )
            contact.save()

            # mapping the contact to the user who saved it
            mapped = UserContactMapping(
                user=user,
                contact=contact
            ).save()

            response = {
                'msg': 'Contact saved successfully',
                'data': request.data
            }
            return Response(
                response,
                status=200,
                content_type="application/json"
            )


class SignupList(APIView):
    """Registering a new user"""

    def post(self, request):
        """Adding the new user"""
        # serializer = UserSerializer(data=request.data)
        # if serializer.is_valid():
        #     serializer.save()
        #     print(serializer)
        import ipdb; ipdb.set_trace()

        # name = request.data.get('name', None)
        # password = request.data.get('password', None)
        # email = request.data.get('email', None)
        # phone = request.data.get('phone', None)
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()



        user = User.objects.get(phone=serializer.data['phone'])
        password = request.data["password"]

        user.set_password(password)
        user.save()


        if user:
            payload = {
                'id': user.id,
                'name': user.name,
            }

            jwt_token = {'token': jwt.encode(payload, "SECRET_KEY")}

            return Response(
                jwt_token,
                status=200,
                content_type="application/json"
            )
        else:
            return Response(
                json.dumps({'Error': "Error in signup"}),
                status=400,
                content_type="application/json"
            )


class LoginList(APIView):
    """Login page for the user"""

    def post(self, request):
        # import ipdb; ipdb.set_trace()
        # if not request.query_params:
        #     return Response({'Error': "Please provide name/password"}, status=400)

        # phone = request.data.get('phone', None)
        phone = request.query_params.get('phone', None)
        password = request.query_params.get('password', None)
        
        if authenticate(phone=phone, password=password):
            user = User.objects.get(phone=phone)
        else:
            return Response({'Error': "Invalid name/password"}, status=400)
        if user:
            payload = {
                'id': user.id,
                'name': user.phone,
            }

            jwt_token = {'token': jwt.encode(payload, "SECRET_KEY")}

            return Response(
                jwt_token,
                status=200,
                content_type="application/json"
            )
        else:
            return Response(
                json.dumps({'Error': "Invalid credentials"}),
                status=400,
                content_type="application/json"
            )


class TokenAuthentication(BaseAuthentication):
    """Generationg the token from the BaseAuthentication"""

    def authenticate(self, request):
        """For authentication the user"""
        # import ipdb; ipdb.set_trace()
        auth = get_authorization_header(request).split()
        if not auth or auth[0].lower() != b'bearer':
            return ('', {'Error': "Token is invalid"})

        if len(auth) == 1:
            msg = 'Invalid token header. No credentials provided.'
            raise exceptions.AuthenticationFailed(msg)
        elif len(auth) > 2:
            msg = 'Invalid token header'
            raise exceptions.AuthenticationFailed(msg)

        try:
            token = auth[1]
            if token == "null":
                msg = 'Null token not allowed'
                raise exceptions.AuthenticationFailed(msg)
        except UnicodeError:
            msg = 'Invalid token header. Token string should not contain invalid characters.'
            raise exceptions.AuthenticationFailed(msg)

        return self.authenticate_credentials(token)

    def authenticate_credentials(self, token):
        """fetcing the registered users
        params:takes the token
        returns:users information
        """
        # import ipdb;ipdb.set_trace()
        try:
            payload = jwt.decode(token, "SECRET_KEY")
            phone = payload['name']
            userid = payload['id']
            user = User.objects.get(
                phone=phone,
                id=userid,
                active=True
            )
        except:
            error = {'Error': "Token is invalid"}
            return '', error

        return user, ''


class SpamList(APIView):
    """Checking for the spam users and can used for blocking"""
    def post(self, request):
        try:
            auth = TokenAuthentication()
            user, error = auth.authenticate(request)
            if (error):
                return Response(
                    error,
                    status=400,
                    content_type="application/json"
                )
            else:
                phone = request.data.get('phone', None)
                a = Contact.objects.filter(phone=phone).update(spam=True)
                b = User.objects.filter(phone=phone).update(spam=True)

                if (a + b):
                    return HttpResponse(
                        json.dumps({'message': "Contact marked as spam"}),
                        status=200,
                        content_type="application/json"
                    )
                else:
                    return HttpResponse(
                        json.dumps({'message': "Contact does not exist"}),
                        status=400,
                        content_type="application/json"
                    )

        except:
            return HttpResponse(
                json.dumps({'Error': "Internal server error"}),
                status=500,
                content_type="application/json"
            )


class SearchNameList(APIView):
    """Search the contacts"""
    def get(self, request):
        """
        search the contacts and fetch the data
        param: Takes the name
        returns:User contacts
        """
        try:
            auth = TokenAuthentication()
            user, error = auth.authenticate(request)
            if (error):
                return Response(
                    error,
                    status=400,
                    content_type="application/json"
                )
            else:
                name = request.GET.get('name', None)

                a = Contact.objects.all().filter(name=name)
                b = Contact.objects.all().filter(name__contains=name).exclude(name=name)

                response = []
                for contact in a:
                    response.append({
                        'name': contact.name,
                        'phone': contact.phone,
                        'spam': contact.spam
                    })
                for contact in b:
                    response.append({
                        'name': contact.name,
                        'phone': contact.phone,
                        'spam': contact.spam
                    })

                return Response(
                    response,
                    status=200,
                    content_type="application/json"
                )
        except:
            return HttpResponse(
                json.dumps({'Error': "Internal server error"}),
                status=500,
                content_type="application/json"
            )


class SearchPhoneList(APIView):
    def get(self, request):
        # import ipdb;ipdb.set_trace()
        phone = request.GET.get('phone', None)

        try:
            auth = TokenAuthentication()
            user, error = auth.authenticate(request)
            if (error):
                return Response(
                    error,
                    status=400,
                    content_type="application/json"
                )
            else:
                profile = User.objects.get(phone=phone)

                if (profile):
                    user = User.objects.get(
                        id=profile.id,
                        active=True
                    )
                response = {
                    'name': user.name,
                    'phone': profile.phone,
                    'spam': profile.spam,
                    'email': user.email
                }

                return Response(
                    response,
                    status=200,
                    content_type="application/json"
                )

        except User.DoesNotExist:
            contacts = Contact.objects.all().filter(phone=phone)
            response = []
            for contact in contacts:
                response.append({
                    'name': contact.name,
                    'phone': contact.phone,
                    'spam': contact.spam,
                    'email': contact.email
                })

            return Response(
                response,
                status=200,
                content_type="application/json"
            )

        except:
            return HttpResponse(
                json.dumps({'Error': "Internal server error"}),
                status=500,
                content_type="application/json"
            )